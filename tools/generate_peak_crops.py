#!/usr/bin/env python3
"""
Generate high-resolution crops of each peak region from the trail map.
Also overlay the extracted trail paths with their current IDs for comparison.
This makes it possible to visually read trail names and match them to paths.
"""

import cv2
import numpy as np
import re
import os

MAP_PATH = "public/killington-trail-map.jpg"
OUTPUT_DIR = "tools/peak_crops"

# Peak regions (x_min%, x_max%, y_min%, y_max%) - with generous margins
PEAK_REGIONS = {
    'snowshed':        (0, 14, 38, 85),
    'sunrise':         (0, 18, 32, 68),
    'bear-mountain':   (12, 42, 12, 72),
    'skye-peak':       (26, 58, 3, 72),
    'killington-peak': (40, 68, 1, 58),
    'snowdon':         (58, 90, 8, 68),
    'ramshead':        (78, 100, 15, 75),
}

# Colors for different trail difficulties
COLORS = {
    'cyan': (255, 255, 0),      # cyan paths -> yellow draw
    'pink': (255, 0, 255),      # pink paths -> magenta draw
    'yellow': (0, 255, 255),    # yellow paths -> cyan draw
    'default': (0, 255, 0),     # fallback green
}


def load_trail_paths():
    """Parse trailPaths.ts to get current trail paths."""
    with open("src/data/trailPaths.ts", 'r') as f:
        content = f.read()

    paths = {}
    pattern = r"'([a-z][a-z0-9-]+)':\s*\[\[(.+?)\]\]"
    for match in re.finditer(pattern, content):
        trail_id = match.group(1)
        points_str = match.group(2)
        point_pattern = r'\[(\d+\.?\d*),\s*(\d+\.?\d*)\]'
        points = [(float(x), float(y)) for x, y in re.findall(point_pattern, points_str)]
        if points:
            paths[trail_id] = points
    return paths


def load_trail_info():
    """Parse trails.ts for trail metadata."""
    with open("src/data/trails.ts", 'r') as f:
        content = f.read()

    trails = {}
    pattern = r"\{\s*id:\s*'([^']+)',\s*name:\s*'([^']*)'(?:.*?difficulty:\s*'([^']+)')(?:.*?peak:\s*'([^']+)')"
    for match in re.finditer(pattern, content, re.DOTALL):
        trail_id, name, difficulty, peak = match.groups()
        trails[trail_id] = {
            'name': name,
            'difficulty': difficulty,
            'peak': peak,
        }
    return trails


def main():
    img = cv2.imread(MAP_PATH)
    h, w = img.shape[:2]
    print(f"Image: {w}x{h}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    paths = load_trail_paths()
    trail_info = load_trail_info()
    print(f"Loaded {len(paths)} paths, {len(trail_info)} trail definitions")

    for peak_id, (x_min, x_max, y_min, y_max) in PEAK_REGIONS.items():
        # Convert percentages to pixels
        px_x1 = int(x_min / 100 * w)
        px_x2 = int(x_max / 100 * w)
        px_y1 = int(y_min / 100 * h)
        px_y2 = int(y_max / 100 * h)

        # Crop
        crop = img[px_y1:px_y2, px_x1:px_x2].copy()
        crop_h, crop_w = crop.shape[:2]

        # Generate two versions:
        # 1. Clean crop (for reading trail names)
        clean_path = f"{OUTPUT_DIR}/{peak_id}_clean.jpg"
        cv2.imwrite(clean_path, crop, [cv2.IMWRITE_JPEG_QUALITY, 95])

        # 2. Annotated crop with trail paths and IDs overlaid
        annotated = crop.copy()

        # Draw all trail paths that fall in this region
        peak_trails = {tid: info for tid, info in trail_info.items()
                       if info['peak'] == peak_id}

        for trail_id, info in peak_trails.items():
            if trail_id not in paths:
                continue

            pts = paths[trail_id]
            # Convert percentage coords to pixel coords within the crop
            crop_pts = []
            for x_pct, y_pct in pts:
                px = int((x_pct - x_min) / (x_max - x_min) * crop_w)
                py = int((y_pct - y_min) / (y_max - y_min) * crop_h)
                crop_pts.append((px, py))

            if len(crop_pts) < 2:
                continue

            # Choose color based on difficulty
            diff = info.get('difficulty', '')
            if diff in ('green',):
                color = (0, 200, 0)
            elif diff in ('blue',):
                color = (255, 200, 0)
            elif diff in ('black',):
                color = (0, 0, 255)
            elif diff in ('double-black',):
                color = (0, 0, 200)
            else:
                color = (200, 200, 200)

            # Draw the trail path
            pts_arr = np.array(crop_pts, dtype=np.int32)
            cv2.polylines(annotated, [pts_arr], False, color, 3, cv2.LINE_AA)

            # Label at the midpoint
            mid_idx = len(crop_pts) // 2
            mx, my = crop_pts[mid_idx]

            # Draw label background
            label = trail_id
            font_scale = 0.45
            thickness = 1
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            cv2.rectangle(annotated, (mx - 2, my - th - 4), (mx + tw + 2, my + 4), (0, 0, 0), -1)
            cv2.putText(annotated, label, (mx, my),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

        annotated_path = f"{OUTPUT_DIR}/{peak_id}_annotated.jpg"
        cv2.imwrite(annotated_path, annotated, [cv2.IMWRITE_JPEG_QUALITY, 95])

        n_trails = len(peak_trails)
        print(f"  {peak_id}: {crop_w}x{crop_h}px, {n_trails} trails → {clean_path}")

    print(f"\nSaved crops to {OUTPUT_DIR}/")
    print("Use _clean.jpg files to read trail names from the map")
    print("Use _annotated.jpg files to see current path assignments")


if __name__ == "__main__":
    main()
