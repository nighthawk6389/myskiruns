#!/usr/bin/env python3
"""Step 6: Visualization overlays for debugging and verification."""

import json
import sys
from pathlib import Path

import cv2
import numpy as np

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
IMAGE_PATH = OUTPUT_DIR / "trailmap_300dpi.png"
POLYLINES_PATH = OUTPUT_DIR / "extracted_polylines.json"

COLOR_MAP = {
    "green": (0, 200, 0),
    "blue": (255, 80, 0),
    "black": (100, 100, 100),
}


def draw_polylines_on_image(img: np.ndarray, polylines: list,
                            draw_labels: bool = True) -> np.ndarray:
    """Draw polylines on an image copy with color coding and labels."""
    overlay = img.copy()

    for trail in polylines:
        color = COLOR_MAP.get(trail["color"], (255, 255, 255))
        pts = np.array(trail["points"], dtype=np.int32)  # already [x, y]

        if len(pts) < 2:
            continue

        # Draw the polyline
        cv2.polylines(overlay, [pts], isClosed=False, color=color,
                      thickness=3, lineType=cv2.LINE_AA)

        # Draw label at the start of the trail
        if draw_labels:
            label = trail["id"]
            x, y = pts[0]
            cv2.putText(overlay, label, (x + 5, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)

    return overlay


def create_per_color_overlays(img: np.ndarray, polylines: list):
    """Create separate overlay images per color."""
    for color_name in COLOR_MAP:
        color_trails = [t for t in polylines if t["color"] == color_name]
        if not color_trails:
            continue

        overlay = draw_polylines_on_image(img, color_trails)
        # Downscale for reasonable file size
        scale = 2400 / max(overlay.shape[1], overlay.shape[0])
        w, h = int(overlay.shape[1] * scale), int(overlay.shape[0] * scale)
        small = cv2.resize(overlay, (w, h))

        path = OUTPUT_DIR / f"overlay_{color_name}.jpg"
        cv2.imwrite(str(path), small, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"  Saved {path} ({len(color_trails)} trails)")


def create_composite_overlay(img: np.ndarray, polylines: list):
    """Create a single overlay with all colors."""
    overlay = draw_polylines_on_image(img, polylines, draw_labels=False)

    # Downscale
    scale = 2400 / max(overlay.shape[1], overlay.shape[0])
    w, h = int(overlay.shape[1] * scale), int(overlay.shape[0] * scale)
    small = cv2.resize(overlay, (w, h))

    path = OUTPUT_DIR / "overlay_all.jpg"
    cv2.imwrite(str(path), small, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"  Saved {path} ({len(polylines)} trails)")


def create_numbered_overlay(img: np.ndarray, polylines: list):
    """Create overlay with large numbered labels for LLM identification."""
    overlay = img.copy()

    for i, trail in enumerate(polylines):
        color = COLOR_MAP.get(trail["color"], (255, 255, 255))
        pts = np.array(trail["points"], dtype=np.int32)

        if len(pts) < 2:
            continue

        cv2.polylines(overlay, [pts], isClosed=False, color=color,
                      thickness=4, lineType=cv2.LINE_AA)

        # Large numbered label at midpoint
        mid_idx = len(pts) // 2
        mx, my = pts[mid_idx]
        label = str(i)
        cv2.putText(overlay, label, (mx + 8, my),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(overlay, label, (mx + 8, my),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)

    # Downscale
    scale = 3000 / max(overlay.shape[1], overlay.shape[0])
    w, h = int(overlay.shape[1] * scale), int(overlay.shape[0] * scale)
    small = cv2.resize(overlay, (w, h))

    path = OUTPUT_DIR / "overlay_numbered.jpg"
    cv2.imwrite(str(path), small, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"  Saved {path} (numbered for LLM identification)")


def main():
    if not POLYLINES_PATH.exists():
        print("ERROR: Run 03_extract_polylines.py first.")
        sys.exit(1)

    print("Loading image...")
    img = cv2.imread(str(IMAGE_PATH))
    if img is None:
        print(f"ERROR: Could not load {IMAGE_PATH}")
        sys.exit(1)

    data = json.loads(POLYLINES_PATH.read_text())
    polylines = data["accepted"]
    print(f"Loaded {len(polylines)} accepted polylines")

    print("\nCreating per-color overlays...")
    create_per_color_overlays(img, polylines)

    print("\nCreating composite overlay...")
    create_composite_overlay(img, polylines)

    print("\nCreating numbered overlay...")
    create_numbered_overlay(img, polylines)

    # Summary stats
    print("\n--- Summary ---")
    for color in COLOR_MAP:
        count = len([t for t in polylines if t["color"] == color])
        print(f"  {color}: {count} segments")
    print(f"  Total: {len(polylines)}")
    if data.get("uncertain"):
        print(f"  Uncertain (needs SAM 2): {len(data['uncertain'])}")


if __name__ == "__main__":
    main()
