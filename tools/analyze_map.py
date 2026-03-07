#!/usr/bin/env python3
"""
Analyze the Killington trail map image to find trail line positions.
This script uses color detection to identify trail lines on the map,
then outputs their positions as percentage coordinates.
"""

import cv2
import numpy as np
from PIL import Image
import json
import sys

MAP_PATH = "public/killington-trail-map.jpg"

def load_image():
    img = cv2.imread(MAP_PATH)
    if img is None:
        print(f"ERROR: Could not load {MAP_PATH}")
        sys.exit(1)
    h, w = img.shape[:2]
    print(f"Image size: {w}x{h}")
    return img

def analyze_colors(img):
    """Sample colors across the image to understand the trail line color palette."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, w = img.shape[:2]

    # Convert to RGB for reporting
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Sample a grid of points and report dominant colors
    print("\n=== Color Analysis ===")
    print("Sampling colors across the image to identify trail line hues...\n")

    # Look at the HSV histogram for the bright colored lines
    # Trail lines are typically: cyan/blue, pink/magenta, green/yellow, white

    # Define color ranges for trail lines in HSV
    color_ranges = {
        'cyan_blue': {'lower': np.array([85, 80, 120]), 'upper': np.array([110, 255, 255])},
        'light_blue': {'lower': np.array([90, 40, 180]), 'upper': np.array([115, 200, 255])},
        'pink_magenta': {'lower': np.array([140, 60, 120]), 'upper': np.array([175, 255, 255])},
        'red': {'lower': np.array([0, 80, 120]), 'upper': np.array([10, 255, 255])},
        'yellow_green': {'lower': np.array([20, 60, 120]), 'upper': np.array([45, 255, 255])},
        'bright_green': {'lower': np.array([45, 80, 120]), 'upper': np.array([85, 255, 255])},
        'white_bright': {'lower': np.array([0, 0, 220]), 'upper': np.array([180, 40, 255])},
        'orange': {'lower': np.array([10, 80, 150]), 'upper': np.array([22, 255, 255])},
    }

    for name, rng in color_ranges.items():
        mask = cv2.inRange(hsv, rng['lower'], rng['upper'])
        pixel_count = cv2.countNonZero(mask)
        pct = pixel_count / (w * h) * 100
        if pct > 0.05:  # Only show colors with meaningful presence
            # Find centroid of this color
            coords = np.where(mask > 0)
            if len(coords[0]) > 0:
                cy = np.mean(coords[0]) / h * 100
                cx = np.mean(coords[1]) / w * 100
                # Find bounding box
                min_y = np.min(coords[0]) / h * 100
                max_y = np.max(coords[0]) / h * 100
                min_x = np.min(coords[1]) / w * 100
                max_x = np.max(coords[1]) / w * 100
                print(f"  {name}: {pct:.2f}% of image, center=({cx:.1f}%, {cy:.1f}%), "
                      f"bbox=x:[{min_x:.1f}-{max_x:.1f}], y:[{min_y:.1f}-{max_y:.1f}]")

    return hsv

def find_trail_lines(img, hsv):
    """
    Detect trail lines by color and extract their paths.
    Returns regions where trail-colored pixels are concentrated.
    """
    h, w = img.shape[:2]

    print("\n=== Trail Line Detection ===\n")

    # Combine cyan and light blue (most trail lines appear as these)
    cyan_mask = cv2.inRange(hsv, np.array([85, 50, 120]), np.array([115, 255, 255]))

    # Pink/magenta trails (harder trails)
    pink_mask = cv2.inRange(hsv, np.array([140, 50, 120]), np.array([175, 255, 255]))

    # Yellow/green borders (easy trail outlines)
    yellow_mask = cv2.inRange(hsv, np.array([20, 50, 120]), np.array([50, 255, 255]))

    # White/bright lines
    white_mask = cv2.inRange(hsv, np.array([0, 0, 210]), np.array([180, 50, 255]))

    # Combine all trail colors
    all_trails = cv2.bitwise_or(cyan_mask, pink_mask)
    all_trails = cv2.bitwise_or(all_trails, yellow_mask)

    # Morphological operations to clean up noise and connect lines
    kernel = np.ones((3, 3), np.uint8)
    all_trails = cv2.morphologyEx(all_trails, cv2.MORPH_CLOSE, kernel, iterations=2)
    all_trails = cv2.morphologyEx(all_trails, cv2.MORPH_OPEN, kernel, iterations=1)

    # Divide the image into a grid and find trail density in each cell
    grid_cols = 20
    grid_rows = 15
    cell_w = w // grid_cols
    cell_h = h // grid_rows

    print("Trail density heatmap (% of trail-colored pixels per grid cell):")
    print(f"Grid: {grid_cols}x{grid_rows}, each cell = {cell_w}x{cell_h}px\n")

    # Header
    print("     ", end="")
    for c in range(grid_cols):
        x_pct = (c + 0.5) / grid_cols * 100
        print(f"{x_pct:5.0f}", end="")
    print("  (x%)")
    print("     " + "-----" * grid_cols)

    for r in range(grid_rows):
        y_pct = (r + 0.5) / grid_rows * 100
        print(f"{y_pct:4.0f}|", end="")
        for c in range(grid_cols):
            cell = all_trails[r*cell_h:(r+1)*cell_h, c*cell_w:(c+1)*cell_w]
            density = cv2.countNonZero(cell) / (cell_w * cell_h) * 100
            if density > 15:
                print("  ###", end="")
            elif density > 8:
                print("  ## ", end="")
            elif density > 3:
                print("  #  ", end="")
            elif density > 1:
                print("  .  ", end="")
            else:
                print("     ", end="")
        print(f"  ({y_pct:.0f}%)")

    return all_trails, cyan_mask, pink_mask, yellow_mask

def find_peak_regions(all_trails, img_shape):
    """
    Use connected component analysis to find major trail clusters
    which correspond to peak areas.
    """
    h, w = img_shape[:2]

    print("\n=== Peak Region Detection ===\n")

    # Dilate to connect nearby trail segments
    kernel = np.ones((15, 15), np.uint8)
    dilated = cv2.dilate(all_trails, kernel, iterations=3)

    # Find connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(dilated, connectivity=8)

    # Filter by size - only keep significant regions
    regions = []
    for i in range(1, num_labels):  # Skip background (label 0)
        area = stats[i, cv2.CC_STAT_AREA]
        if area > 5000:  # Minimum area threshold
            x = stats[i, cv2.CC_STAT_LEFT]
            y = stats[i, cv2.CC_STAT_TOP]
            bw = stats[i, cv2.CC_STAT_WIDTH]
            bh = stats[i, cv2.CC_STAT_HEIGHT]
            cx, cy = centroids[i]
            regions.append({
                'area': area,
                'x_pct': x / w * 100,
                'y_pct': y / h * 100,
                'w_pct': bw / w * 100,
                'h_pct': bh / h * 100,
                'cx_pct': cx / w * 100,
                'cy_pct': cy / h * 100,
            })

    # Sort by x position (left to right)
    regions.sort(key=lambda r: r['cx_pct'])

    print(f"Found {len(regions)} significant trail regions:\n")
    for i, r in enumerate(regions):
        print(f"  Region {i+1}: center=({r['cx_pct']:.1f}%, {r['cy_pct']:.1f}%), "
              f"bbox=({r['x_pct']:.1f}%, {r['y_pct']:.1f}%) "
              f"size=({r['w_pct']:.1f}% x {r['h_pct']:.1f}%), area={r['area']}px")

    return regions

def extract_trail_paths_by_color(img, hsv):
    """
    For each color channel (cyan=blue trails, pink=harder trails, yellow=green trails),
    find individual line segments using skeletonization and contour detection.
    """
    h, w = img.shape[:2]

    print("\n=== Extracting Trail Paths by Color ===\n")

    color_configs = {
        'cyan': {
            'lower': np.array([85, 50, 120]),
            'upper': np.array([115, 255, 255]),
            'description': 'Blue/Cyan trails (intermediate)',
        },
        'pink': {
            'lower': np.array([140, 50, 120]),
            'upper': np.array([175, 255, 255]),
            'description': 'Pink/Magenta trails (advanced)',
        },
        'yellow': {
            'lower': np.array([20, 50, 120]),
            'upper': np.array([50, 255, 255]),
            'description': 'Yellow/Green trails (beginner)',
        },
    }

    all_paths = {}

    for color_name, config in color_configs.items():
        mask = cv2.inRange(hsv, config['lower'], config['upper'])

        # Clean up
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter by size and shape (trail lines are long and thin)
        trail_contours = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 200:
                continue

            # Get bounding rect
            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect = max(bw, bh) / max(min(bw, bh), 1)
            length = max(bw, bh)

            # Trail lines are elongated (high aspect ratio) or large
            if length > 30 or area > 1000:
                # Simplify the contour to get key points
                epsilon = 0.005 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)

                # Convert to percentage coordinates
                points = [(p[0][0] / w * 100, p[0][1] / h * 100) for p in approx]

                trail_contours.append({
                    'area': area,
                    'length': length,
                    'x_pct': x / w * 100,
                    'y_pct': y / h * 100,
                    'w_pct': bw / w * 100,
                    'h_pct': bh / h * 100,
                    'points': points,
                })

        # Sort by area (largest first)
        trail_contours.sort(key=lambda c: c['area'], reverse=True)

        print(f"{config['description']}: {len(trail_contours)} line segments found")

        # Show top segments
        for i, tc in enumerate(trail_contours[:20]):
            print(f"  #{i+1}: area={tc['area']}, bbox=({tc['x_pct']:.1f}%,{tc['y_pct']:.1f}%) "
                  f"size=({tc['w_pct']:.1f}%x{tc['h_pct']:.1f}%), "
                  f"{len(tc['points'])} points")

        if len(trail_contours) > 20:
            print(f"  ... and {len(trail_contours) - 20} more smaller segments")

        all_paths[color_name] = trail_contours

    return all_paths

def create_vertical_slices(all_trails, img_shape):
    """
    Slice the image into vertical columns and find where trails exist
    at each height level. This helps map trails from top to bottom.
    """
    h, w = img_shape[:2]

    print("\n=== Vertical Trail Profile (where trails exist at each x-position) ===\n")

    num_slices = 40  # 40 vertical slices = 2.5% each
    slice_w = w // num_slices

    for s in range(num_slices):
        x_pct = (s + 0.5) / num_slices * 100
        col = all_trails[:, s*slice_w:(s+1)*slice_w]

        # Find y-ranges where trails exist in this column
        row_density = np.mean(col > 0, axis=1)
        trail_rows = np.where(row_density > 0.05)[0]  # >5% trail pixels in row

        if len(trail_rows) > 0:
            y_min = trail_rows[0] / h * 100
            y_max = trail_rows[-1] / h * 100
            # Find clusters (gaps > 20px mean separate trail groups)
            gaps = np.where(np.diff(trail_rows) > 30)[0]
            num_clusters = len(gaps) + 1

            bar_len = int((y_max - y_min) / 2)
            bar = "#" * bar_len
            print(f"  x={x_pct:5.1f}%: y=[{y_min:5.1f}%-{y_max:5.1f}%] "
                  f"({num_clusters} trail groups) {bar}")

def main():
    print("=" * 70)
    print("  Killington Trail Map Analyzer")
    print("=" * 70)

    img = load_image()
    hsv = analyze_colors(img)

    all_trails, cyan, pink, yellow = find_trail_lines(img, hsv)

    find_peak_regions(all_trails, img.shape)

    create_vertical_slices(all_trails, img.shape)

    extract_trail_paths_by_color(img, hsv)

    print("\n" + "=" * 70)
    print("  Analysis Complete")
    print("=" * 70)

if __name__ == "__main__":
    main()
