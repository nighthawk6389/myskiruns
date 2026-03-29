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

from utils.color_ranges import COLOR_RANGES, VIS_COLORS_BGR

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


def cleanup_mask(mask: np.ndarray, min_area: int = 300) -> np.ndarray:
    """Morphological cleanup: open (remove noise), close (fill gaps), remove small components."""
    kernel = np.ones((3, 3), np.uint8)
    # Open to remove small noise
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    # Close to fill small gaps in lines
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    # Remove small connected components
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] < min_area:
            mask[labels == i] = 0
    return mask


def detect_black_trails(img: np.ndarray, hsv_img: np.ndarray,
                        existing_masks: dict) -> np.ndarray:
    """Step 2c: Detect black trails using Canny edge detection + dark-line filtering.

    Black trails can't be found by color alone — dark lines on dark terrain.
    Instead: find edges of dark regions, extract the dark lines between them.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Gaussian blur to suppress terrain texture
    gray_blur = cv2.GaussianBlur(gray, (5, 5), 1.5)

    # Canny edge detection
    edges = cv2.Canny(gray_blur, 30, 100)

    # Darkness mask — keep only regions that are actually dark
    v_channel = hsv_img[:, :, 2]
    s_channel = hsv_img[:, :, 1]
    dark_mask = ((v_channel < 100) & (s_channel < 80)).astype(np.uint8) * 255

    # Dilate edges to bridge the two sides of a dark line
    dilated_edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    # The dark line body: dark pixels near edges
    dark_near_edges = cv2.bitwise_and(dark_mask, dilated_edges)

    # Dilate to connect fragmented dark line segments
    dark_lines = cv2.dilate(dark_near_edges, np.ones((3, 3), np.uint8), iterations=2)

    # Close gaps
    kernel = np.ones((3, 3), np.uint8)
    dark_lines = cv2.morphologyEx(dark_lines, cv2.MORPH_CLOSE, kernel, iterations=3)

    # Subtract already-detected colored trail masks
    for name, mask in existing_masks.items():
        if name != "black":
            # Dilate the colored mask a bit to ensure full subtraction
            dilated = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)
            dark_lines = cv2.bitwise_and(dark_lines, cv2.bitwise_not(dilated))

    # Cleanup: remove small components and non-elongated blobs
    dark_lines = cleanup_mask(dark_lines, min_area=400)

    # Additional filtering: remove components with low aspect ratio (text, blobs)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(dark_lines)
    for i in range(1, num_labels):
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        aspect = max(w, h) / max(min(w, h), 1)
        if aspect < 3:
            dark_lines[labels == i] = 0

    return dark_lines


def run_segmentation(img: np.ndarray) -> dict:
    """Run full color segmentation pipeline. Returns dict of color_name -> binary mask."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    masks = {}

    # Segment each color
    for color_name, ranges in COLOR_RANGES.items():
        print(f"  Segmenting {color_name}...")
        mask = segment_color(hsv, ranges)
        mask = cleanup_mask(mask)
        masks[color_name] = mask
        pixel_count = np.count_nonzero(mask)
        print(f"    {pixel_count:,} pixels ({pixel_count / mask.size * 100:.2f}%)")

    # Black trails via edge detection
    print("  Detecting black trails (edge detection)...")
    masks["black"] = detect_black_trails(img, hsv, masks)
    pixel_count = np.count_nonzero(masks["black"])
    print(f"    {pixel_count:,} pixels ({pixel_count / masks['black'].size * 100:.2f}%)")

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
