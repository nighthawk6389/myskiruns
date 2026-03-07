#!/usr/bin/env python3
"""
Overlay the current trailPaths.ts coordinates on the actual map image
to see how far off they are from the real trail lines.
"""

import cv2
import numpy as np
import re

MAP_PATH = "public/killington-trail-map.jpg"
PATHS_PATH = "src/data/trailPaths.ts"
OUTPUT_PATH = "tools/current_paths_overlay.jpg"

def parse_trail_paths(filepath):
    """Parse trailPaths.ts to extract trail coordinates."""
    with open(filepath, 'r') as f:
        content = f.read()

    trails = {}
    # Find each trail entry
    pattern = r"'([^']+)':\s*\[\s*\[\s*((?:\[[^\]]+\],?\s*)+)\]"
    for match in re.finditer(pattern, content):
        trail_id = match.group(1)
        coords_str = match.group(2)
        # Parse coordinate pairs
        coord_pattern = r'\[(\d+\.?\d*),\s*(\d+\.?\d*)\]'
        coords = [(float(x), float(y)) for x, y in re.findall(coord_pattern, coords_str)]
        if coords:
            trails[trail_id] = coords
    return trails

# Peak colors for visualization
PEAK_COLORS = {
    'snowshed': (0, 255, 0),       # Green
    'sunrise': (0, 200, 200),       # Teal
    'ramshead': (255, 255, 0),      # Cyan (in BGR)
    'snowdon': (0, 165, 255),       # Orange (in BGR)
    'skye-peak': (255, 0, 0),       # Blue (in BGR)
    'killington-peak': (0, 0, 255), # Red (in BGR)
    'bear-mountain': (255, 0, 255), # Magenta (in BGR)
}

# Map trail IDs to peaks
TRAIL_PEAKS = {
    'snowshed-slope': 'snowshed', 'yodeler': 'snowshed', 'idler': 'snowshed',
    'snow-play': 'snowshed', 'snowshed-crossover': 'snowshed',
    'sun-dog': 'sunrise', 'rendezvous': 'sunrise', 'bear-cub': 'sunrise',
    'bear-view': 'sunrise', 'sunrise-connector': 'sunrise',
    'easy-street': 'ramshead', 'swirl': 'ramshead', 'treezy': 'ramshead',
    'squeeze-play': 'ramshead', 'ramshead-run': 'ramshead',
    'ramshead-liftline': 'ramshead', 'header': 'ramshead', 'vagabond': 'ramshead',
    'caper': 'ramshead', 'timberline': 'ramshead', 'start-park': 'ramshead',
    'great-northern': 'snowdon', 'bunny-buster': 'snowdon', 'chute': 'snowdon',
    'conclusion': 'snowdon', 'upper-fis': 'snowdon', 'mountain-run': 'snowdon',
    'mountain-training': 'snowdon', 'snowdon-liftline': 'snowdon',
    'upper-snowdon': 'snowdon', 'lower-snowdon': 'snowdon', 'bittersweet': 'snowdon',
    'sass': 'snowdon', 'northstar': 'snowdon', 'royal-flush': 'snowdon',
    'upper-northbrook': 'snowdon', 'lower-northbrook': 'snowdon',
    'snowdon-glades': 'snowdon',
    'outer-limits': 'bear-mountain', 'devils-fiddle': 'bear-mountain',
    'wildfire': 'bear-mountain', 'lower-wildfire': 'bear-mountain',
    'bear-claw': 'bear-mountain', 'bear-mountain-liftline': 'bear-mountain',
    'bear-trax': 'bear-mountain', 'falls-brook': 'bear-mountain',
    'skye-burst-bear': 'bear-mountain', 'bear-run': 'bear-mountain',
    'growler': 'bear-mountain', 'centerpiece': 'bear-mountain',
    'spacewalk': 'bear-mountain', 'the-stash': 'bear-mountain',
    'lil-stash': 'bear-mountain',
}
# Skye Peak and Killington Peak trails
for tid in ['skyelark', 'upper-skyelark', 'skyeburst', 'upper-skyeburst',
            'skye-hawk', 'skyebits', 'cruise-control', 'mouse-trap', 'somewhere',
            'breakaway', 'touch-down', 'patsys', 'twister', 'catwalk',
            'upper-catwalk', 'great-eastern', 'home-stretch', 'lower-home-stretch',
            'juggernaut', 'vertigo', 'upper-vertigo', 'ovation', 'needles-eye',
            'panic-button', 'dream-maker', 'dream-maker-headwall', 'highline',
            'pipe-dream', 'valley-plunge', 'field-goal', 'roundabout',
            'roundabout-glade', 'tin-man', 'skye-peak-liftline', 'great-bear',
            'upper-great-bear', 'woodward-peace-park']:
    TRAIL_PEAKS[tid] = 'skye-peak'

for tid in ['superstar', 'cascade', 'downdraft', 'double-dipper', 'big-dipper-glade',
            'flume', 'escapade', 'east-fall', 'upper-east-fall', 'rime', 'reason',
            'julio', 'high-road', 'north-way', 'great-eastern-kp', 'fis', 'lower-fis',
            'solitude', 'k1-gondola-run', 'anarchy', 'upper-canyon', 'lower-canyon',
            'old-superstar', 'killington-liftline', 'superstar-glade', 'header-kp',
            'mouse-run', 'low-road', 'the-mall']:
    TRAIL_PEAKS[tid] = 'killington-peak'


def main():
    img = cv2.imread(MAP_PATH)
    h, w = img.shape[:2]
    print(f"Image: {w}x{h}")

    trails = parse_trail_paths(PATHS_PATH)
    print(f"Parsed {len(trails)} trails from {PATHS_PATH}")

    viz = img.copy()

    # Draw each trail path
    for trail_id, coords in trails.items():
        peak = TRAIL_PEAKS.get(trail_id, 'unknown')
        color = PEAK_COLORS.get(peak, (128, 128, 128))

        # Convert percentage coords to pixel coords
        points = [(int(x / 100 * w), int(y / 100 * h)) for x, y in coords]

        # Draw the polyline
        pts = np.array(points, dtype=np.int32)
        cv2.polylines(viz, [pts], False, color, 3, cv2.LINE_AA)

        # Draw dots at each coordinate point
        for px, py in points:
            cv2.circle(viz, (px, py), 4, color, -1)

    # Draw 10% grid
    for pct in range(0, 101, 10):
        x = int(pct / 100 * w)
        y = int(pct / 100 * h)
        if x < w:
            cv2.line(viz, (x, 0), (x, h), (0, 0, 200), 1)
            cv2.putText(viz, f"{pct}%", (x + 3, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 200), 2)
        if y < h:
            cv2.line(viz, (0, y), (w, y), (0, 0, 200), 1)
            cv2.putText(viz, f"{pct}%", (5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 200), 2)

    # Add legend
    legend_y = 50
    cv2.rectangle(viz, (w - 450, legend_y - 10), (w - 10, legend_y + 190), (0, 0, 0), -1)
    for i, (peak_name, color) in enumerate(PEAK_COLORS.items()):
        y = legend_y + 25 * i + 15
        cv2.line(viz, (w - 440, y), (w - 400, y), color, 3)
        cv2.putText(viz, peak_name, (w - 390, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # Save
    small = cv2.resize(viz, (w // 2, h // 2))
    cv2.imwrite(OUTPUT_PATH, small, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"Saved to {OUTPUT_PATH}")

    # Print summary of where each peak's trails are placed
    print("\n=== Current Trail Placement Summary ===\n")
    for peak_name in PEAK_COLORS:
        peak_trails = [tid for tid, p in TRAIL_PEAKS.items() if p == peak_name]
        if not peak_trails:
            continue
        all_x = []
        all_y = []
        for tid in peak_trails:
            if tid in trails:
                for x, y in trails[tid]:
                    all_x.append(x)
                    all_y.append(y)
        if all_x:
            print(f"  {peak_name}:")
            print(f"    x range: {min(all_x):.1f}% - {max(all_x):.1f}%")
            print(f"    y range: {min(all_y):.1f}% - {max(all_y):.1f}%")
            print(f"    center: ({np.mean(all_x):.1f}%, {np.mean(all_y):.1f}%)")

if __name__ == "__main__":
    main()
