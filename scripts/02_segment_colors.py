#!/usr/bin/env python3
"""Step 2: Color segmentation of trail map into per-color binary masks.

Usage:
    python 02_segment_colors.py          # Run segmentation with current thresholds
    python 02_segment_colors.py --tune   # Interactive HSV threshold tuning with trackbars
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

from utils.color_ranges import TRAIL_COLOR_RANGES, LIFT_COLOR_RANGES, OTHER_COLOR_RANGES, COLOR_RANGES, VIS_COLORS_BGR

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
MASKS_DIR = OUTPUT_DIR / "masks"
IMAGE_PATH = OUTPUT_DIR / "trailmap_300dpi.png"


def load_image():
    """Load the trail map image."""
    if not IMAGE_PATH.exists():
        print(f"ERROR: Image not found at {IMAGE_PATH}. Run 01_convert_pdf.py first.")
        sys.exit(1)
    img = cv2.imread(str(IMAGE_PATH))
    if img is None:
        print(f"ERROR: Could not read {IMAGE_PATH}")
        sys.exit(1)
    return img


def segment_color(hsv_img: np.ndarray, ranges: list) -> np.ndarray:
    """Create binary mask for a color using one or more HSV ranges."""
    mask = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
    for lower, upper in ranges:
        mask |= cv2.inRange(hsv_img, lower, upper)
    return mask


def cleanup_mask(mask: np.ndarray, min_area: int = 200) -> np.ndarray:
    """Morphological cleanup: open (remove noise), close (fill gaps), remove small components."""
    kernel = np.ones((3, 3), np.uint8)
    # Open to remove small noise
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    # Close to fill small gaps in lines (where text overlaps trail lines)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    # Remove small connected components
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] < min_area:
            mask[labels == i] = 0
    return mask


def gap_fill_mask(mask: np.ndarray) -> np.ndarray:
    """Fill small gaps in trail lines caused by text labels or anti-aliasing.

    Strategy: dilate to bridge small gaps, close to merge, then erode back.
    This connects fragmented trail segments without fattening the lines much.
    """
    # Dilate to bridge gaps (up to ~10px gap at this resolution)
    dilated = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)
    # Close to merge nearby fragments
    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), iterations=2)
    # Erode back to approximate original line width
    result = cv2.erode(closed, np.ones((5, 5), np.uint8), iterations=2)
    # Keep original mask pixels (don't lose any)
    result = cv2.bitwise_or(result, mask)
    return result


def detect_black_trails(img: np.ndarray, hsv_img: np.ndarray,
                        existing_masks: dict) -> np.ndarray:
    """Detect black trails (advanced + double-black) using adaptive thresholding.

    Black trail lines are dark lines on a painted terrain that also has dark areas
    (shadows, trees, rocks). Color-based approaches fail because there's no
    distinguishing hue.

    Strategy: Use adaptive thresholding to find locally-dark features relative to
    their surroundings (trail lines have higher local contrast than terrain texture).
    Then rely on the heuristic scoring in Step 3 to filter out text, buildings, etc.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Adaptive threshold: finds pixels that are dark relative to their local
    # neighborhood. Block size 11 captures thin lines; C=5 controls sensitivity.
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, blockSize=11, C=5
    )

    # Combine with absolute darkness constraint — trail lines should be
    # genuinely dark, not just darker than a bright background
    v_channel = hsv_img[:, :, 2]
    dark_enough = (v_channel < 140).astype(np.uint8) * 255
    adaptive = cv2.bitwise_and(adaptive, dark_enough)

    # Subtract already-detected colored trail masks (+ lifts)
    for name, mask in existing_masks.items():
        if name != "black":
            dilated = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)
            adaptive = cv2.bitwise_and(adaptive, cv2.bitwise_not(dilated))

    # Morphological cleanup
    kernel = np.ones((3, 3), np.uint8)
    # Open to remove single-pixel noise and thin terrain texture
    adaptive = cv2.morphologyEx(adaptive, cv2.MORPH_OPEN, kernel, iterations=1)
    # Close to connect fragmented line segments
    adaptive = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Remove small components (text characters, dots)
    adaptive = cleanup_mask(adaptive, min_area=150)

    # Remove very low aspect-ratio blobs (buildings, large terrain patches)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(adaptive)
    for i in range(1, num_labels):
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        aspect = max(w, h) / max(min(w, h), 1)
        # Remove compact blobs (aspect < 2.5) unless very small (might be short trail segment)
        if aspect < 2.5 and area > 500:
            adaptive[labels == i] = 0

    return adaptive


def create_sky_mask(img: np.ndarray) -> np.ndarray:
    """Create a mask of the sky area at the top of the image.

    The sky is blue/cyan and would otherwise contaminate the blue trail mask.
    Strategy: the sky is the top portion of the image with high brightness
    and blue/cyan hue.
    """
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Sky pixels: blue-cyan hue, moderate-high value, in top 20% of image
    sky_color = cv2.inRange(hsv, np.array([80, 20, 100]), np.array([140, 255, 255]))

    # Only keep sky in the top portion
    sky_mask = np.zeros((h, w), dtype=np.uint8)
    sky_region_h = int(0.20 * h)
    sky_mask[:sky_region_h, :] = sky_color[:sky_region_h, :]

    # Dilate to cover fringe pixels
    sky_mask = cv2.dilate(sky_mask, np.ones((15, 15), np.uint8), iterations=2)

    return sky_mask


def run_segmentation(img: np.ndarray) -> dict:
    """Run full color segmentation pipeline. Returns dict of color_name -> binary mask."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    masks = {}

    # Create sky mask to exclude from blue detection
    sky_mask = create_sky_mask(img)
    sky_pixels = np.count_nonzero(sky_mask)
    print(f"  Sky mask: {sky_pixels:,} pixels excluded")

    # Segment trail colors
    print("\n  --- Trail colors ---")
    for color_name, ranges in TRAIL_COLOR_RANGES.items():
        print(f"  Segmenting {color_name}...")
        mask = segment_color(hsv, ranges)
        # Subtract sky from blue mask
        if color_name == "blue":
            before = np.count_nonzero(mask)
            mask = cv2.bitwise_and(mask, cv2.bitwise_not(sky_mask))
            removed = before - np.count_nonzero(mask)
            print(f"    Removed {removed:,} sky pixels")
        mask = cleanup_mask(mask)
        mask = gap_fill_mask(mask)
        masks[color_name] = mask
        num_labels = cv2.connectedComponentsWithStats(mask)[0] - 1
        pixel_count = np.count_nonzero(mask)
        print(f"    {pixel_count:,} pixels ({pixel_count / mask.size * 100:.2f}%), {num_labels} components")

    # Black trails via edge detection (includes advanced AND expert/double-black)
    print("  Detecting black trails (edge detection)...")
    masks["black"] = detect_black_trails(img, hsv, masks)
    masks["black"] = gap_fill_mask(masks["black"])
    pixel_count = np.count_nonzero(masks["black"])
    num_labels = cv2.connectedComponentsWithStats(masks["black"])[0] - 1
    print(f"    {pixel_count:,} pixels ({pixel_count / masks['black'].size * 100:.2f}%), {num_labels} components")

    # Segment lift colors (tracked separately)
    print("\n  --- Lift lines (excluded from trail extraction) ---")
    for color_name, ranges in LIFT_COLOR_RANGES.items():
        print(f"  Segmenting {color_name}...")
        mask = segment_color(hsv, ranges)
        mask = cleanup_mask(mask, min_area=500)
        masks[color_name] = mask
        pixel_count = np.count_nonzero(mask)
        print(f"    {pixel_count:,} pixels ({pixel_count / mask.size * 100:.2f}%)")

    # Other (boundaries)
    for color_name, ranges in OTHER_COLOR_RANGES.items():
        mask = segment_color(hsv, ranges)
        mask = cleanup_mask(mask)
        masks[color_name] = mask

    # Subtract lift masks from trail masks to remove any overlap
    print("\n  Subtracting lift lines from trail masks...")
    combined_lifts = np.zeros_like(list(masks.values())[0])
    for lift_name in LIFT_COLOR_RANGES:
        if lift_name in masks:
            dilated_lift = cv2.dilate(masks[lift_name], np.ones((5, 5), np.uint8), iterations=1)
            combined_lifts = cv2.bitwise_or(combined_lifts, dilated_lift)

    for trail_name in list(TRAIL_COLOR_RANGES.keys()) + ["black"]:
        if trail_name in masks:
            before = np.count_nonzero(masks[trail_name])
            masks[trail_name] = cv2.bitwise_and(masks[trail_name], cv2.bitwise_not(combined_lifts))
            after = np.count_nonzero(masks[trail_name])
            removed = before - after
            if removed > 0:
                print(f"    {trail_name}: removed {removed:,} lift-overlap pixels")

    return masks


def save_masks(masks: dict):
    """Save each mask as a PNG file."""
    MASKS_DIR.mkdir(parents=True, exist_ok=True)
    for name, mask in masks.items():
        path = MASKS_DIR / f"{name}_mask.png"
        cv2.imwrite(str(path), mask)
        print(f"  Saved {path}")


def save_composite_overlay(img: np.ndarray, masks: dict):
    """Save a composite image showing all masks overlaid on the original."""
    overlay = img.copy()
    for name, mask in masks.items():
        color = VIS_COLORS_BGR.get(name, (255, 255, 255))
        colored = np.zeros_like(img)
        colored[:] = color
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) // 255
        overlay = cv2.addWeighted(overlay, 1.0, colored * mask_3ch, 0.4, 0)

    path = OUTPUT_DIR / "color_overlay.png"
    cv2.imwrite(str(path), overlay)
    print(f"  Saved composite overlay to {path}")


def interactive_tune(img: np.ndarray):
    """Interactive HSV threshold tuning with OpenCV trackbars."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Downscale for display
    scale = 1200 / max(img.shape[1], img.shape[0])
    display_size = (int(img.shape[1] * scale), int(img.shape[0] * scale))

    cv2.namedWindow("HSV Tuner", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("HSV Tuner", display_size[0], display_size[1])

    cv2.createTrackbar("H Low", "HSV Tuner", 0, 180, lambda x: None)
    cv2.createTrackbar("H High", "HSV Tuner", 180, 180, lambda x: None)
    cv2.createTrackbar("S Low", "HSV Tuner", 0, 255, lambda x: None)
    cv2.createTrackbar("S High", "HSV Tuner", 255, 255, lambda x: None)
    cv2.createTrackbar("V Low", "HSV Tuner", 0, 255, lambda x: None)
    cv2.createTrackbar("V High", "HSV Tuner", 255, 255, lambda x: None)

    print("\nInteractive HSV tuning mode.")
    print("Adjust trackbars to isolate trail colors. Press 'q' to quit.\n")
    print("Suggested starting points:")
    for name, ranges in COLOR_RANGES.items():
        for lower, upper in ranges:
            print(f"  {name}: H[{lower[0]}-{upper[0]}] S[{lower[1]}-{upper[1]}] V[{lower[2]}-{upper[2]}]")

    while True:
        h_lo = cv2.getTrackbarPos("H Low", "HSV Tuner")
        h_hi = cv2.getTrackbarPos("H High", "HSV Tuner")
        s_lo = cv2.getTrackbarPos("S Low", "HSV Tuner")
        s_hi = cv2.getTrackbarPos("S High", "HSV Tuner")
        v_lo = cv2.getTrackbarPos("V Low", "HSV Tuner")
        v_hi = cv2.getTrackbarPos("V High", "HSV Tuner")

        lower = np.array([h_lo, s_lo, v_lo])
        upper = np.array([h_hi, s_hi, v_hi])
        mask = cv2.inRange(hsv, lower, upper)

        # Show mask overlaid on original
        result = img.copy()
        result[mask > 0] = [0, 255, 0]

        display = cv2.resize(result, display_size)
        cv2.imshow("HSV Tuner", display)

        key = cv2.waitKey(30) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    print(f"\nFinal values: H[{h_lo}-{h_hi}] S[{s_lo}-{s_hi}] V[{v_lo}-{v_hi}]")


def main():
    parser = argparse.ArgumentParser(description="Color segmentation of trail map")
    parser.add_argument("--tune", action="store_true", help="Interactive HSV tuning mode")
    args = parser.parse_args()

    print("Loading image...")
    img = load_image()
    print(f"  Image size: {img.shape[1]}x{img.shape[0]}")

    if args.tune:
        interactive_tune(img)
        return

    print("\nRunning color segmentation...")
    masks = run_segmentation(img)

    print("\nSaving masks...")
    save_masks(masks)
    save_composite_overlay(img, masks)

    # Save stats
    stats = {}
    for name, mask in masks.items():
        num_labels, _, comp_stats, _ = cv2.connectedComponentsWithStats(mask)
        stats[name] = {
            "pixel_count": int(np.count_nonzero(mask)),
            "component_count": num_labels - 1,  # subtract background
            "percentage": round(np.count_nonzero(mask) / mask.size * 100, 3),
        }

    stats_path = OUTPUT_DIR / "segmentation_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2))
    print(f"\nStats saved to {stats_path}")
    print("\nDone! Inspect masks in scripts/output/masks/")


if __name__ == "__main__":
    main()
