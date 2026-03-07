#!/usr/bin/env python3
"""
Extract trail paths using a horizontal sweepline approach:
1. For each color channel, scan the image in horizontal bands
2. At each band, find clusters of colored pixels
3. Track clusters across bands to form trail lines
4. The center of each cluster at each band = a point on the trail path

This avoids the fragmentation issues of skeletonization by naturally
following trails from top to bottom.
"""

import cv2
import numpy as np
from collections import defaultdict
import json
import re

MAP_PATH = "public/killington-trail-map.jpg"
TRAILS_PATH = "src/data/trails.ts"

PEAK_REGIONS = {
    'snowshed':        (0, 10, 40, 82),
    'sunrise':         (3, 16, 35, 62),
    'bear-mountain':   (14, 38, 15, 68),
    'skye-peak':       (28, 57, 5, 68),
    'killington-peak': (42, 66, 3, 62),
    'snowdon':         (62, 88, 10, 65),
    'ramshead':        (82, 100, 18, 70),
}

DIFFICULTY_TO_COLOR = {
    'green': 'yellow',
    'blue': 'cyan',
    'black': 'pink',
    'double-black': 'pink',
}


def extract_masks(hsv):
    """Extract trail color masks with tight thresholds."""
    # Cyan/blue trails - tighter range to avoid picking up sky/water
    cyan = cv2.inRange(hsv, np.array([88, 60, 130]), np.array([115, 255, 255]))
    # Pink/magenta trails
    pink = cv2.inRange(hsv, np.array([145, 50, 130]), np.array([172, 255, 255]))
    # Yellow/green trails (trail markings, not forest)
    yellow = cv2.inRange(hsv, np.array([20, 80, 150]), np.array([48, 255, 255]))

    # Light cleanup - don't over-connect
    kernel = np.ones((2, 2), np.uint8)
    for mask in [cyan, pink, yellow]:
        cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1, dst=mask)

    return {'cyan': cyan, 'pink': pink, 'yellow': yellow}


def sweepline_trace(mask, w, h, band_height_px=8, min_cluster_width=3, max_gap_bands=4):
    """
    Trace trails through a color mask using horizontal band sweepline.

    For each horizontal band:
    - Find horizontal runs of colored pixels
    - Cluster nearby runs
    - Track which clusters connect to clusters in the band above
    - Clusters that persist for many bands = trail lines
    """
    num_bands = h // band_height_px

    # Active trails being tracked: list of {points: [(x_pct, y_pct)], last_x: float, gap: int}
    active_trails = []
    completed_trails = []

    for band_idx in range(num_bands):
        y_start = band_idx * band_height_px
        y_end = min(y_start + band_height_px, h)
        y_center = (y_start + y_end) / 2
        y_pct = y_center / h * 100

        # Get the band of the mask
        band = mask[y_start:y_end, :]

        # Find clusters of colored pixels in this band
        # Project band vertically: for each x column, is there any colored pixel?
        col_projection = np.any(band > 0, axis=0).astype(np.uint8)

        # Find runs of 1s (connected horizontal segments)
        clusters = []
        in_run = False
        run_start = 0
        for x in range(w):
            if col_projection[x] and not in_run:
                in_run = True
                run_start = x
            elif not col_projection[x] and in_run:
                in_run = False
                run_width = x - run_start
                if run_width >= min_cluster_width:
                    cx = (run_start + x) / 2
                    cx_pct = cx / w * 100
                    clusters.append({
                        'x_pct': cx_pct,
                        'width': run_width,
                        'x_start': run_start,
                        'x_end': x,
                    })
        if in_run:
            run_width = w - run_start
            if run_width >= min_cluster_width:
                cx = (run_start + w) / 2
                cx_pct = cx / w * 100
                clusters.append({
                    'x_pct': cx_pct,
                    'width': run_width,
                    'x_start': run_start,
                    'x_end': w,
                })

        # Match clusters to active trails
        used_clusters = set()
        for trail in active_trails:
            trail['gap'] += 1

            # Find closest cluster to this trail's last x position
            best_cluster = None
            best_dist = float('inf')
            # Maximum horizontal shift per band (in pixels) - trails don't jump far
            max_shift = 40

            for ci, cluster in enumerate(clusters):
                if ci in used_clusters:
                    continue
                dist = abs(cluster['x_pct'] - trail['last_x'])
                dist_px = abs(cluster['x_pct'] - trail['last_x']) / 100 * w
                if dist_px < max_shift and dist < best_dist:
                    best_dist = dist
                    best_cluster = ci

            if best_cluster is not None:
                used_clusters.add(best_cluster)
                cluster = clusters[best_cluster]
                trail['points'].append((round(cluster['x_pct'], 1), round(y_pct, 1)))
                trail['last_x'] = cluster['x_pct']
                trail['gap'] = 0

        # Start new trails from unmatched clusters
        for ci, cluster in enumerate(clusters):
            if ci not in used_clusters:
                active_trails.append({
                    'points': [(round(cluster['x_pct'], 1), round(y_pct, 1))],
                    'last_x': cluster['x_pct'],
                    'gap': 0,
                })

        # Complete trails that have been inactive too long
        still_active = []
        for trail in active_trails:
            if trail['gap'] > max_gap_bands:
                if len(trail['points']) >= 4:
                    completed_trails.append(trail)
            else:
                still_active.append(trail)
        active_trails = still_active

    # Complete remaining active trails
    for trail in active_trails:
        if len(trail['points']) >= 4:
            completed_trails.append(trail)

    return completed_trails


def simplify_trail_points(points, target_points=8):
    """Reduce a trail to ~target_points using Douglas-Peucker."""
    if len(points) <= target_points:
        return points

    pts = np.array(points, dtype=np.float32).reshape(-1, 1, 2)

    # Binary search for the right epsilon
    lo, hi = 0.1, 20.0
    for _ in range(20):
        mid = (lo + hi) / 2
        simplified = cv2.approxPolyDP(pts, mid, False)
        if len(simplified) > target_points:
            lo = mid
        else:
            hi = mid

    simplified = cv2.approxPolyDP(pts, hi, False)
    result = [(round(float(p[0][0]), 1), round(float(p[0][1]), 1)) for p in simplified]

    # Ensure at least 3 points
    if len(result) < 3:
        step = max(len(points) // 3, 1)
        result = [points[0], points[len(points)//2], points[-1]]

    return result


def compute_trail_stats(trail):
    """Compute statistics for a traced trail."""
    pts = trail['points']
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return {
        'points': pts,
        'center_x': np.mean(xs),
        'center_y': np.mean(ys),
        'top_y': min(ys),
        'bot_y': max(ys),
        'left_x': min(xs),
        'right_x': max(xs),
        'height': max(ys) - min(ys),
        'width': max(xs) - min(xs),
        'num_points': len(pts),
    }


def assign_to_peaks(trails):
    """Assign traced trails to peak regions."""
    assigned = defaultdict(list)
    unassigned = []

    for trail in trails:
        cx = trail['center_x']
        cy = trail['center_y']

        best_peak = None
        best_dist = float('inf')

        for peak_id, (x_min, x_max, y_min, y_max) in PEAK_REGIONS.items():
            margin = 2
            if (x_min - margin) <= cx <= (x_max + margin) and (y_min - margin) <= cy <= (y_max + margin):
                rcx = (x_min + x_max) / 2
                rcy = (y_min + y_max) / 2
                dist = np.sqrt((cx - rcx)**2 + (cy - rcy)**2)
                if dist < best_dist:
                    best_dist = dist
                    best_peak = peak_id

        if best_peak:
            assigned[best_peak].append(trail)
        else:
            unassigned.append(trail)

    return assigned, unassigned


def parse_trails_ts():
    """Parse trails.ts to get trail definitions."""
    with open(TRAILS_PATH, 'r') as f:
        content = f.read()

    trails_by_peak = defaultdict(list)
    pattern = r"\{\s*id:\s*'([^']+)',\s*name:\s*'([^']*)'(?:.*?),\s*difficulty:\s*'([^']+)',\s*peak:\s*'([^']+)'"
    for match in re.finditer(pattern, content):
        trail_id, name, difficulty, peak = match.groups()
        trails_by_peak[peak].append({
            'id': trail_id,
            'name': name,
            'difficulty': difficulty,
            'expected_color': DIFFICULTY_TO_COLOR.get(difficulty, 'cyan'),
        })
    return trails_by_peak


def match_trails_in_peak(trail_defs, extracted_paths_by_color):
    """
    Match trail definitions to extracted paths within a single peak.

    Strategy:
    - Group trails by expected color
    - For each color, sort both trails and paths by x-position
    - Use position-based matching: leftmost trail = leftmost path, etc.
    """
    matches = {}

    for color in ['cyan', 'pink', 'yellow']:
        # Trails expecting this color
        color_trails = [t for t in trail_defs if t['expected_color'] == color]
        if not color_trails:
            continue

        # Available paths of this color, sorted by x position
        color_paths = sorted(
            extracted_paths_by_color.get(color, []),
            key=lambda p: (p['center_x'], p['top_y'])
        )

        # Filter: only keep paths with decent vertical extent (> 3% height)
        good_paths = [p for p in color_paths if p['height'] > 3]
        # If not enough good paths, lower the threshold
        if len(good_paths) < len(color_trails):
            good_paths = [p for p in color_paths if p['height'] > 1.5]
        if len(good_paths) < len(color_trails):
            good_paths = color_paths  # use all

        if not good_paths:
            continue

        # Sort trails by their name/expected position
        # (We don't have position info from the definition, so sort by name)
        # Actually, just match in order: sort both by x position and pair them up

        # For a better match, use greedy nearest-neighbor
        used = set()
        for trail in color_trails:
            best_idx = None
            best_score = float('inf')

            for j, path in enumerate(good_paths):
                if j in used:
                    continue
                # Prefer paths with more height (longer trails)
                score = -path['height']  # prefer taller
                if score < best_score:
                    best_score = score
                    best_idx = j

            if best_idx is not None:
                used.add(best_idx)
                matches[trail['id']] = good_paths[best_idx]

    return matches


def generate_trailpaths_ts(all_matches, trails_by_peak):
    """Generate the final trailPaths.ts content."""
    lines = []
    lines.append("// Trail path coordinate data for polyline overlays on the trail map image.")
    lines.append("// Each trail is keyed by trail ID and contains an array of segments.")
    lines.append("// Each segment is an array of [x, y] percentage coordinate pairs (0-100)")
    lines.append("// matching the SVG viewBox=\"0 0 100 100\" used in ImageMap.tsx.")
    lines.append("//")
    lines.append("// Coordinates extracted from trail map image via OpenCV sweepline analysis.")
    lines.append("// Image: killington-trail-map.jpg (4572x2704px)")
    lines.append("//")
    lines.append("// Peak layout (left to right):")
    lines.append("//   Snowshed → Sunrise → Bear Mountain → Skye Peak")
    lines.append("//   → Killington Peak → Snowdon → Ramshead")
    lines.append("")
    lines.append("export type TrailPathSegment = [number, number][];")
    lines.append("")
    lines.append("export const trailPaths: Record<string, TrailPathSegment[]> = {")

    peak_order = ['snowshed', 'sunrise', 'bear-mountain', 'skye-peak',
                  'killington-peak', 'snowdon', 'ramshead']

    matched_count = 0
    total_count = 0

    for peak_id in peak_order:
        trails = trails_by_peak.get(peak_id, [])
        lines.append(f"\n  // === {peak_id.upper().replace('-', ' ')} ===")

        for trail in trails:
            total_count += 1
            tid = trail['id']
            if tid in all_matches:
                matched_count += 1
                path = all_matches[tid]
                simplified = simplify_trail_points(path['points'], target_points=10)
                pts_str = ", ".join(f"[{x}, {y}]" for x, y in simplified)
                lines.append(f"  '{tid}': [[{pts_str}]],")
            else:
                lines.append(f"  // '{tid}': no path extracted")

    lines.append("};")

    print(f"\n  Matched {matched_count}/{total_count} trails with CV-extracted paths")
    return "\n".join(lines)


def visualize(img, all_matches, w, h):
    """Visualize matched paths on the map."""
    viz = img.copy()

    color_map = {
        'cyan': (255, 255, 0),
        'pink': (255, 0, 255),
        'yellow': (0, 255, 255),
    }

    for trail_id, path_info in all_matches.items():
        color = color_map.get(path_info.get('color', ''), (255, 255, 255))
        pts = [(int(x/100*w), int(y/100*h)) for x, y in path_info['points']]
        if len(pts) >= 2:
            cv2.polylines(viz, [np.array(pts)], False, color, 3, cv2.LINE_AA)

    # Grid
    for pct in range(0, 101, 10):
        x = int(pct / 100 * w)
        y = int(pct / 100 * h)
        if x < w:
            cv2.line(viz, (x, 0), (x, h), (0, 0, 180), 1)
        if y < h:
            cv2.line(viz, (0, y), (w, y), (0, 0, 180), 1)

    small = cv2.resize(viz, (w // 2, h // 2))
    cv2.imwrite("tools/sweepline_paths.jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print("Saved visualization to tools/sweepline_paths.jpg")


def main():
    print("=" * 70)
    print("  Sweepline Trail Path Extraction")
    print("=" * 70)

    img = cv2.imread(MAP_PATH)
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    print(f"Image: {w}x{h}")

    # Step 1: Color masks
    print("\n[1] Extracting color masks...")
    masks = extract_masks(hsv)
    for name, mask in masks.items():
        print(f"  {name}: {cv2.countNonZero(mask):,} pixels")

    # Step 2: Sweepline tracing
    print("\n[2] Running sweepline trace...")
    all_traced = {}
    for color_name, mask in masks.items():
        traced = sweepline_trace(mask, w, h, band_height_px=6, min_cluster_width=4, max_gap_bands=5)
        # Compute stats
        traced_with_stats = []
        for t in traced:
            stats = compute_trail_stats(t)
            stats['color'] = color_name
            traced_with_stats.append(stats)

        # Sort by height descending (tallest = most complete trail lines)
        traced_with_stats.sort(key=lambda t: t['height'], reverse=True)
        all_traced[color_name] = traced_with_stats

        print(f"  {color_name}: {len(traced_with_stats)} trails traced")
        # Print top trails
        for i, t in enumerate(traced_with_stats[:8]):
            print(f"    #{i+1}: height={t['height']:.1f}%, center=({t['center_x']:.1f}, {t['center_y']:.1f}), "
                  f"x=[{t['left_x']:.1f}-{t['right_x']:.1f}], {t['num_points']} pts")

    # Step 3: Assign to peaks
    print("\n[3] Assigning to peak regions...")
    all_paths_flat = []
    for color_name, paths in all_traced.items():
        all_paths_flat.extend(paths)

    assigned, unassigned = assign_to_peaks(all_paths_flat)
    for peak_id in ['snowshed', 'sunrise', 'bear-mountain', 'skye-peak',
                    'killington-peak', 'snowdon', 'ramshead']:
        peak_paths = assigned.get(peak_id, [])
        by_color = defaultdict(int)
        for p in peak_paths:
            by_color[p['color']] += 1
        color_str = ", ".join(f"{c}:{n}" for c, n in sorted(by_color.items()))
        # Count paths with height > 3%
        good = sum(1 for p in peak_paths if p['height'] > 3)
        print(f"  {peak_id}: {len(peak_paths)} total, {good} with >3% height ({color_str})")
    print(f"  Unassigned: {len(unassigned)}")

    # Step 4: Parse trail definitions
    print("\n[4] Parsing trail definitions...")
    trails_by_peak = parse_trails_ts()

    # Step 5: Match
    print("\n[5] Matching trails to extracted paths...")
    all_matches = {}
    for peak_id in trails_by_peak:
        peak_paths = assigned.get(peak_id, [])
        # Group by color
        by_color = defaultdict(list)
        for p in peak_paths:
            by_color[p['color']].append(p)

        matches = match_trails_in_peak(trails_by_peak[peak_id], by_color)
        all_matches.update(matches)
        print(f"  {peak_id}: {len(matches)}/{len(trails_by_peak[peak_id])} matched")

    # Step 6: Generate output
    print("\n[6] Generating trailPaths.ts...")
    ts_content = generate_trailpaths_ts(all_matches, trails_by_peak)
    with open("tools/cv_trailPaths.ts", 'w') as f:
        f.write(ts_content)
    print("  Written to tools/cv_trailPaths.ts")

    # Step 7: Visualize
    print("\n[7] Visualizing...")
    visualize(img, all_matches, w, h)

    # Summary
    print("\n" + "=" * 70)
    print("  MATCH DETAILS")
    print("=" * 70)
    peak_order = ['snowshed', 'sunrise', 'bear-mountain', 'skye-peak',
                  'killington-peak', 'snowdon', 'ramshead']
    for peak_id in peak_order:
        print(f"\n--- {peak_id} ---")
        for trail in trails_by_peak.get(peak_id, []):
            tid = trail['id']
            if tid in all_matches:
                p = all_matches[tid]
                simplified = simplify_trail_points(p['points'], target_points=10)
                print(f"  ✓ {tid} ({trail['expected_color']}): height={p['height']:.1f}%, "
                      f"center=({p['center_x']:.1f},{p['center_y']:.1f}), {len(simplified)} pts")
            else:
                print(f"  ✗ {tid} ({trail['expected_color']}): NOT MATCHED")


if __name__ == "__main__":
    main()
