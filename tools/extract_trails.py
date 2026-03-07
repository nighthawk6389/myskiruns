#!/usr/bin/env python3
"""
Extract trail line paths from the Killington trail map image using color
detection and skeletonization. Outputs coordinates as percentage-based
polylines ready for trailPaths.ts.
"""

import cv2
import numpy as np
from collections import defaultdict
import json

MAP_PATH = "public/killington-trail-map.jpg"

def load_and_prep(path):
    img = cv2.imread(path)
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return img, hsv, w, h

def extract_color_mask(hsv, lower, upper):
    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    return mask

def skeletonize(mask):
    """Thin a binary mask to 1-pixel-wide skeleton lines."""
    skel = np.zeros_like(mask)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    done = False
    temp = mask.copy()
    while not done:
        eroded = cv2.erode(temp, element)
        opened = cv2.dilate(eroded, element)
        sub = cv2.subtract(temp, opened)
        skel = cv2.bitwise_or(skel, sub)
        temp = eroded.copy()
        if cv2.countNonZero(temp) == 0:
            done = True
    return skel

def trace_skeleton_paths(skeleton, w, h, min_length=30):
    """
    Trace connected paths through a skeleton image.
    Returns list of paths, each path is a list of (x%, y%) points.
    """
    # Find connected components on the skeleton
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        skeleton, connectivity=8
    )

    paths = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < min_length:
            continue

        # Get all pixels for this component
        ys, xs = np.where(labels == i)

        if len(xs) < 5:
            continue

        # Order points along the path by walking from one end
        # Use the topmost point as start (since trails go top-to-bottom)
        start_idx = np.argmin(ys)

        # Simple path ordering: sort by y coordinate (top to bottom)
        # and subsample to get reasonable number of points
        order = np.argsort(ys)
        ordered_xs = xs[order]
        ordered_ys = ys[order]

        # Subsample to ~10-20 points
        total = len(ordered_xs)
        if total < 5:
            continue

        step = max(total // 15, 1)
        sampled_x = ordered_xs[::step]
        sampled_y = ordered_ys[::step]

        # Always include last point
        if sampled_x[-1] != ordered_xs[-1]:
            sampled_x = np.append(sampled_x, ordered_xs[-1])
            sampled_y = np.append(sampled_y, ordered_ys[-1])

        # Smooth the path with a rolling average
        if len(sampled_x) > 3:
            window = min(3, len(sampled_x))
            smoothed_x = np.convolve(sampled_x, np.ones(window)/window, mode='valid')
            smoothed_y = np.convolve(sampled_y, np.ones(window)/window, mode='valid')
        else:
            smoothed_x = sampled_x.astype(float)
            smoothed_y = sampled_y.astype(float)

        # Convert to percentages
        path = [(round(x / w * 100, 1), round(y / h * 100, 1))
                for x, y in zip(smoothed_x, smoothed_y)]

        # Calculate path length in pixels
        if len(path) >= 2:
            length = sum(
                np.sqrt((path[j][0] - path[j-1][0])**2 + (path[j][1] - path[j-1][1])**2)
                for j in range(1, len(path))
            )
        else:
            length = 0

        bbox_w = (max(p[0] for p in path) - min(p[0] for p in path))
        bbox_h = (max(p[1] for p in path) - min(p[1] for p in path))

        paths.append({
            'points': path,
            'length': length,
            'area': area,
            'top_y': min(p[1] for p in path),
            'bot_y': max(p[1] for p in path),
            'left_x': min(p[0] for p in path),
            'right_x': max(p[0] for p in path),
            'center_x': np.mean([p[0] for p in path]),
            'center_y': np.mean([p[1] for p in path]),
            'bbox_w': bbox_w,
            'bbox_h': bbox_h,
        })

    # Sort by area (largest/longest first)
    paths.sort(key=lambda p: p['area'], reverse=True)
    return paths


def assign_to_regions(paths, regions):
    """Assign each path to a region based on its center position."""
    assigned = defaultdict(list)
    unassigned = []

    for path in paths:
        cx = path['center_x']
        cy = path['center_y']

        best_region = None
        best_dist = float('inf')

        for region_name, (x_min, x_max, y_min, y_max) in regions.items():
            if x_min <= cx <= x_max and y_min <= cy <= y_max:
                # Center of region
                rcx = (x_min + x_max) / 2
                rcy = (y_min + y_max) / 2
                dist = np.sqrt((cx - rcx)**2 + (cy - rcy)**2)
                if dist < best_dist:
                    best_dist = dist
                    best_region = region_name

        if best_region:
            assigned[best_region].append(path)
        else:
            unassigned.append(path)

    return assigned, unassigned


def main():
    img, hsv, w, h = load_and_prep(MAP_PATH)
    print(f"Image: {w}x{h}")

    # Extract color masks
    print("\nExtracting trail lines by color...")
    cyan_mask = extract_color_mask(hsv, [85, 50, 120], [115, 255, 255])
    pink_mask = extract_color_mask(hsv, [140, 50, 120], [175, 255, 255])
    yellow_mask = extract_color_mask(hsv, [20, 50, 120], [50, 255, 255])

    # Combine
    all_mask = cv2.bitwise_or(cyan_mask, pink_mask)
    all_mask = cv2.bitwise_or(all_mask, yellow_mask)

    print(f"  Cyan pixels: {cv2.countNonZero(cyan_mask):,}")
    print(f"  Pink pixels: {cv2.countNonZero(pink_mask):,}")
    print(f"  Yellow pixels: {cv2.countNonZero(yellow_mask):,}")
    print(f"  Total trail pixels: {cv2.countNonZero(all_mask):,}")

    # Skeletonize each color channel
    print("\nSkeletonizing trail lines (this may take a moment)...")

    cyan_skel = skeletonize(cyan_mask)
    print(f"  Cyan skeleton: {cv2.countNonZero(cyan_skel):,} pixels")

    pink_skel = skeletonize(pink_mask)
    print(f"  Pink skeleton: {cv2.countNonZero(pink_skel):,} pixels")

    yellow_skel = skeletonize(yellow_mask)
    print(f"  Yellow skeleton: {cv2.countNonZero(yellow_skel):,} pixels")

    # Trace paths
    print("\nTracing paths through skeletons...")
    cyan_paths = trace_skeleton_paths(cyan_skel, w, h, min_length=50)
    pink_paths = trace_skeleton_paths(pink_skel, w, h, min_length=50)
    yellow_paths = trace_skeleton_paths(yellow_skel, w, h, min_length=50)

    print(f"  Cyan paths: {len(cyan_paths)}")
    print(f"  Pink paths: {len(pink_paths)}")
    print(f"  Yellow paths: {len(yellow_paths)}")

    # Print the largest paths for each color
    print("\n" + "=" * 70)
    print("TOP CYAN (BLUE/INTERMEDIATE) TRAIL PATHS:")
    print("=" * 70)
    for i, p in enumerate(cyan_paths[:30]):
        pts_str = " -> ".join(f"({x},{y})" for x, y in p['points'][:5])
        if len(p['points']) > 5:
            pts_str += f" ... ({len(p['points'])} pts total)"
        print(f"  C{i+1}: area={p['area']}, x=[{p['left_x']:.1f}-{p['right_x']:.1f}], "
              f"y=[{p['top_y']:.1f}-{p['bot_y']:.1f}], center=({p['center_x']:.1f},{p['center_y']:.1f})")
        print(f"       {pts_str}")

    print("\n" + "=" * 70)
    print("TOP PINK (ADVANCED) TRAIL PATHS:")
    print("=" * 70)
    for i, p in enumerate(pink_paths[:30]):
        pts_str = " -> ".join(f"({x},{y})" for x, y in p['points'][:5])
        if len(p['points']) > 5:
            pts_str += f" ... ({len(p['points'])} pts total)"
        print(f"  P{i+1}: area={p['area']}, x=[{p['left_x']:.1f}-{p['right_x']:.1f}], "
              f"y=[{p['top_y']:.1f}-{p['bot_y']:.1f}], center=({p['center_x']:.1f},{p['center_y']:.1f})")
        print(f"       {pts_str}")

    print("\n" + "=" * 70)
    print("TOP YELLOW (BEGINNER) TRAIL PATHS:")
    print("=" * 70)
    for i, p in enumerate(yellow_paths[:20]):
        pts_str = " -> ".join(f"({x},{y})" for x, y in p['points'][:5])
        if len(p['points']) > 5:
            pts_str += f" ... ({len(p['points'])} pts total)"
        print(f"  Y{i+1}: area={p['area']}, x=[{p['left_x']:.1f}-{p['right_x']:.1f}], "
              f"y=[{p['top_y']:.1f}-{p['bot_y']:.1f}], center=({p['center_x']:.1f},{p['center_y']:.1f})")
        print(f"       {pts_str}")

    # Visualize extracted paths on the map
    print("\nGenerating visualization...")
    viz = img.copy()

    # Draw extracted skeleton paths
    for path in cyan_paths[:40]:
        pts = [(int(x/100*w), int(y/100*h)) for x,y in path['points']]
        if len(pts) >= 2:
            cv2.polylines(viz, [np.array(pts)], False, (255, 255, 0), 2, cv2.LINE_AA)

    for path in pink_paths[:40]:
        pts = [(int(x/100*w), int(y/100*h)) for x,y in path['points']]
        if len(pts) >= 2:
            cv2.polylines(viz, [np.array(pts)], False, (255, 0, 255), 2, cv2.LINE_AA)

    for path in yellow_paths[:20]:
        pts = [(int(x/100*w), int(y/100*h)) for x,y in path['points']]
        if len(pts) >= 2:
            cv2.polylines(viz, [np.array(pts)], False, (0, 255, 255), 2, cv2.LINE_AA)

    # Add grid
    for pct in range(0, 101, 10):
        x = int(pct / 100 * w)
        y = int(pct / 100 * h)
        if x < w:
            cv2.line(viz, (x, 0), (x, h), (0, 0, 200), 1)
            cv2.putText(viz, f"{pct}", (x+3, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,200), 2)
        if y < h:
            cv2.line(viz, (0, y), (w, y), (0, 0, 200), 1)

    small = cv2.resize(viz, (w // 2, h // 2))
    cv2.imwrite("tools/extracted_paths.jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print("Saved extracted paths visualization to tools/extracted_paths.jpg")

    # Output all paths as JSON for further processing
    all_paths_data = {
        'cyan': [{'points': p['points'], 'area': p['area'],
                  'x_range': [p['left_x'], p['right_x']],
                  'y_range': [p['top_y'], p['bot_y']],
                  'center': [p['center_x'], p['center_y']]}
                 for p in cyan_paths[:50]],
        'pink': [{'points': p['points'], 'area': p['area'],
                  'x_range': [p['left_x'], p['right_x']],
                  'y_range': [p['top_y'], p['bot_y']],
                  'center': [p['center_x'], p['center_y']]}
                 for p in pink_paths[:50]],
        'yellow': [{'points': p['points'], 'area': p['area'],
                    'x_range': [p['left_x'], p['right_x']],
                    'y_range': [p['top_y'], p['bot_y']],
                    'center': [p['center_x'], p['center_y']]}
                   for p in yellow_paths[:30]],
    }

    with open("tools/extracted_paths.json", 'w') as f:
        json.dump(all_paths_data, f, indent=2)
    print("Saved path data to tools/extracted_paths.json")


if __name__ == "__main__":
    main()
