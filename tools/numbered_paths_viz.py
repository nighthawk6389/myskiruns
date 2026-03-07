#!/usr/bin/env python3
"""
Generate numbered path visualizations for each peak region.
Each extracted sweepline path gets a unique number drawn on the map.
The clean map is shown side-by-side so trail names can be read
and matched to path numbers.

Also outputs a JSON with path details for easy reference.
"""

import cv2
import numpy as np
import re
import json
import os
from collections import defaultdict

MAP_PATH = "public/killington-trail-map.jpg"
OUTPUT_DIR = "tools/numbered_paths"

# Re-run sweepline extraction to get ALL paths (not just the matched ones)
# This time we'll import the sweepline module

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


def load_current_paths():
    """Parse trailPaths.ts for current path assignments."""
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


# Peak regions for cropping
PEAK_REGIONS = {
    'snowshed':        (0, 14, 38, 85),
    'sunrise':         (0, 18, 32, 68),
    'bear-mountain':   (12, 42, 12, 72),
    'skye-peak':       (26, 58, 3, 72),
    'killington-peak': (40, 68, 1, 58),
    'snowdon':         (58, 90, 8, 68),
    'ramshead':        (78, 100, 15, 75),
}

DIFF_COLORS = {
    'green': (0, 200, 0),
    'blue': (255, 200, 0),
    'black': (0, 50, 255),
    'double-black': (180, 0, 255),
}


def main():
    img = cv2.imread(MAP_PATH)
    h, w = img.shape[:2]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    trail_info = load_trail_info()
    current_paths = load_current_paths()

    # For each peak, create a visualization showing:
    # Left: clean map with paths drawn and numbered
    # Output: JSON mapping path numbers to coordinates for reference

    all_peak_data = {}

    for peak_id, (x_min, x_max, y_min, y_max) in PEAK_REGIONS.items():
        # Get trails for this peak
        peak_trails = {tid: info for tid, info in trail_info.items()
                       if info['peak'] == peak_id}

        if not peak_trails:
            continue

        # Crop region
        px_x1 = int(x_min / 100 * w)
        px_x2 = int(x_max / 100 * w)
        px_y1 = int(y_min / 100 * h)
        px_y2 = int(y_max / 100 * h)

        crop_w = px_x2 - px_x1
        crop_h = px_y2 - px_y1

        crop = img[px_y1:px_y2, px_x1:px_x2].copy()

        # Draw each trail path with its current ID number
        path_data = []
        path_num = 0

        for trail_id, info in sorted(peak_trails.items()):
            if trail_id not in current_paths:
                continue

            path_num += 1
            pts = current_paths[trail_id]

            # Convert to crop pixel coordinates
            crop_pts = []
            for x_pct, y_pct in pts:
                px = int((x_pct - x_min) / (x_max - x_min) * crop_w)
                py = int((y_pct - y_min) / (y_max - y_min) * crop_h)
                crop_pts.append((px, py))

            if len(crop_pts) < 2:
                continue

            # Get color for difficulty
            diff = info.get('difficulty', '')
            color = DIFF_COLORS.get(diff, (200, 200, 200))

            # Draw path
            pts_arr = np.array(crop_pts, dtype=np.int32)
            cv2.polylines(crop, [pts_arr], False, color, 3, cv2.LINE_AA)

            # Draw number at path start and midpoint
            start = crop_pts[0]
            mid = crop_pts[len(crop_pts) // 2]

            label = f"{path_num}"

            # Background circle + number at midpoint
            cv2.circle(crop, mid, 12, (0, 0, 0), -1)
            cv2.circle(crop, mid, 12, color, 2)
            cv2.putText(crop, label, (mid[0] - 6, mid[1] + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Store data
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            path_data.append({
                'num': path_num,
                'current_trail_id': trail_id,
                'current_name': info['name'],
                'difficulty': diff,
                'center_x': round(np.mean(xs), 1),
                'center_y': round(np.mean(ys), 1),
                'top_y': round(min(ys), 1),
                'bot_y': round(max(ys), 1),
                'left_x': round(min(xs), 1),
                'right_x': round(max(xs), 1),
                'points': pts,
            })

        # Save numbered visualization
        out_path = f"{OUTPUT_DIR}/{peak_id}_numbered.jpg"
        cv2.imwrite(out_path, crop, [cv2.IMWRITE_JPEG_QUALITY, 95])

        all_peak_data[peak_id] = path_data

        print(f"\n{peak_id}: {len(path_data)} paths")
        print(f"  {'#':>3} {'Current ID':<30} {'Name':<25} {'Diff':<8} {'Center':>15}")
        print(f"  {'---':>3} {'-'*30:<30} {'-'*25:<25} {'-'*8:<8} {'-'*15:>15}")
        for pd in path_data:
            print(f"  {pd['num']:>3} {pd['current_trail_id']:<30} {pd['current_name']:<25} "
                  f"{pd['difficulty']:<8} ({pd['center_x']:>5.1f}, {pd['center_y']:>5.1f})")

    # Save all path data as JSON
    json_path = f"{OUTPUT_DIR}/path_data.json"
    with open(json_path, 'w') as f:
        json.dump(all_peak_data, f, indent=2)

    print(f"\nSaved numbered visualizations and data to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
