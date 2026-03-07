#!/usr/bin/env python3
"""
Match trail names to extracted paths using approximate label positions.

The trail name labels on the map appear AT SPECIFIC POSITIONS along each trail.
This script uses those label positions (determined from visual reading of the map)
to match each trail name to the closest sweepline-extracted path of the right color.

Process:
1. Re-run sweepline extraction to get all unnamed paths
2. For each trail, use its known label position to find the closest matching path
3. Output corrected trailPaths.ts
"""

import cv2
import numpy as np
import re
import json
from collections import defaultdict

MAP_PATH = "public/killington-trail-map.jpg"

# ============================================================================
# TRAIL LABEL POSITIONS
# Approximate (x%, y%) where each trail's name label appears on the map.
# Determined from visual reading of high-resolution map crops + agent analysis.
# These only need to be within ~3-5% accuracy for correct matching.
# ============================================================================

# Format: trail_id -> (label_x%, label_y%, expected_sweepline_color)
# expected_sweepline_color: 'cyan' for blue trails, 'pink' for black/double-black, 'yellow' for green

TRAIL_LABEL_POSITIONS = {
    # === SNOWSHED ===
    # Tiny beginner area at far left base. Manual fallback coords.
    'snowshed-slope': (7, 63, 'yellow'),
    'yodeler': (8, 63, 'yellow'),
    'idler': (6, 64, 'yellow'),
    'snow-play': (7, 66, 'yellow'),
    'snowshed-crossover': (7, 63, 'yellow'),

    # === SUNRISE ===
    # Left side of map, small area
    'sun-dog': (5, 48, 'yellow'),      # runs down left side of Sunrise
    'rendezvous': (13, 58, 'yellow'),   # lower right of Sunrise area
    'bear-cub': (11, 41, 'yellow'),     # near Sunrise summit
    'bear-view': (9, 39, 'cyan'),       # near Sunrise summit, blue trail
    'sunrise-connector': (10, 38, 'yellow'),  # near summit, connector

    # === BEAR MOUNTAIN ===
    # Bear Mtn face is centered around x=22-30%, y=28-55%
    'outer-limits': (24, 42, 'pink'),       # LEFT face of Bear Mtn, double-black
    'wildfire': (26, 36, 'pink'),           # upper left face
    'bear-claw': (30, 38, 'cyan'),          # center-right face, blue trail
    'growler': (31, 44, 'pink'),            # right of center, runs down
    'centerpiece': (22, 42, 'pink'),        # center of face
    'spacewalk': (20, 48, 'pink'),          # lower left area
    'bear-trax': (36, 64, 'cyan'),          # lower area near base
    'falls-brook': (33, 55, 'cyan'),        # mid-lower, blue trail
    'skye-burst-bear': (14, 31, 'cyan'),    # connector from Skye to Bear, upper
    'bear-mountain-liftline': (26, 50, 'pink'),  # liftline up center
    'the-stash': (35, 37, 'pink'),          # right side, terrain park
    'lower-wildfire': (25, 52, 'cyan'),     # lower section
    'bear-run': (28, 20, 'cyan'),           # near top/ridge

    # === SKYE PEAK ===
    # Large area, x=28-57%, y=5-68%
    # Upper Skye Peak (summit ~39%, 28%)
    'skyelark': (46, 48, 'cyan'),           # runs down center, major blue trail
    'upper-skyelark': (42, 34, 'cyan'),     # upper section
    'skyeburst': (38, 44, 'cyan'),          # left of Skyelark
    'upper-skyeburst': (38, 38, 'cyan'),    # upper section
    'skye-hawk': (35, 26, 'cyan'),          # upper left, near Sassafras ridge
    'skyebits': (52, 50, 'cyan'),           # right side
    'cruise-control': (40, 50, 'cyan'),     # mid-area, runs down
    'mouse-trap': (36, 40, 'cyan'),         # left side mid-mountain
    'somewhere': (45, 36, 'cyan'),          # center area
    'breakaway': (38, 22, 'cyan'),          # UPPER area near South Ridge
    'touch-down': (37, 62, 'cyan'),         # lower area
    'twister': (45, 42, 'cyan'),            # center, mid-mountain
    'catwalk': (39, 32, 'cyan'),            # upper traverse
    'upper-catwalk': (46, 62, 'cyan'),      # lower traverse
    'great-eastern': (43, 38, 'yellow'),    # green trail, mid-mountain
    'home-stretch': (36, 62, 'yellow'),     # green, lower area
    'lower-home-stretch': (37, 68, 'yellow'),  # green, base area
    'juggernaut': (50, 44, 'yellow'),       # green, right side
    'vertigo': (43, 46, 'pink'),            # major black trail, center
    'upper-vertigo': (44, 38, 'pink'),      # upper section
    'ovation': (50, 44, 'pink'),            # right side, double-black
    'panic-button': (42, 44, 'pink'),       # center area
    'dream-maker': (40, 44, 'pink'),        # left of center
    'dream-maker-headwall': (41, 42, 'pink'),  # upper section headwall
    'highline': (44, 58, 'pink'),           # lower area
    'pipe-dream': (36, 24, 'cyan'),         # upper area, blue
    'valley-plunge': (35, 66, 'cyan'),      # lower area
    'field-goal': (37, 66, 'cyan'),         # lower area near valley plunge
    'roundabout': (34, 26, 'cyan'),         # upper area
    'roundabout-glade': (35, 25, 'pink'),   # near roundabout, glade
    'tin-man': (44, 42, 'cyan'),            # center, small
    'skye-peak-liftline': (33, 48, 'pink'), # liftline
    'great-bear': (54, 56, 'cyan'),         # far right, lower
    'upper-great-bear': (48, 46, 'cyan'),   # right of center
    'woodward-peace-park': (48, 62, 'cyan'),  # right lower area

    # === KILLINGTON PEAK ===
    # Summit at ~55%, 5%. Trails radiate downward.
    'superstar': (56, 18, 'pink'),          # major trail, runs from summit
    'cascade': (60, 16, 'pink'),            # right side off summit
    'downdraft': (52, 14, 'pink'),          # left side off summit
    'double-dipper': (56, 30, 'pink'),      # mid-mountain
    'big-dipper-glade': (54, 18, 'pink'),   # near summit, glade
    'flume': (48, 26, 'pink'),              # left, lower
    'escapade': (54, 12, 'pink'),           # near summit
    'east-fall': (48, 24, 'pink'),          # left side
    'upper-east-fall': (64, 20, 'pink'),    # far right
    'rime': (50, 18, 'pink'),              # near summit
    'reason': (62, 18, 'pink'),            # far right, upper
    'julio': (58, 42, 'pink'),             # lower right
    'high-road': (52, 34, 'cyan'),         # blue, mid-mountain
    'north-way': (48, 32, 'cyan'),         # blue, left side
    'great-eastern-kp': (65, 18, 'yellow'), # green, right side
    'fis': (50, 16, 'pink'),              # near summit
    'lower-fis': (52, 28, 'cyan'),        # blue, mid
    'solitude': (52, 14, 'cyan'),         # blue, near summit
    'k1-gondola-run': (64, 22, 'cyan'),   # blue, far right
    'anarchy': (54, 15, 'pink'),          # near summit
    'upper-canyon': (64, 30, 'pink'),     # far right
    'lower-canyon': (55, 11, 'pink'),     # near summit
    'old-superstar': (58, 36, 'pink'),    # right side, lower
    'killington-liftline': (53, 46, 'pink'),  # liftline
    'superstar-glade': (55, 16, 'pink'),  # near summit, glade
    'header-kp': (60, 16, 'cyan'),        # blue, right side
    'mouse-run': (46, 18, 'cyan'),        # blue, far left
    'low-road': (52, 12, 'yellow'),       # green, near summit
    'the-mall': (54, 10, 'yellow'),       # green, at summit

    # === SNOWDON ===
    # Right side of map, x=62-88%, y=10-65%
    'great-northern': (74, 34, 'cyan'),    # major blue trail
    'bunny-buster': (80, 28, 'yellow'),    # green, right side
    'chute': (76, 30, 'pink'),             # black trail
    'conclusion': (76, 38, 'pink'),        # double-black
    'upper-fis': (84, 26, 'yellow'),       # green (confusingly named)
    'mountain-run': (64, 48, 'yellow'),    # green, lower left
    'mountain-training': (62, 54, 'yellow'),  # green, base area
    'snowdon-liftline': (80, 48, 'cyan'),  # blue, liftline
    'upper-snowdon': (70, 22, 'cyan'),     # blue, near summit
    'lower-snowdon': (72, 44, 'cyan'),     # blue, lower
    'bittersweet': (76, 32, 'cyan'),       # blue, mid
    'sass': (78, 24, 'cyan'),              # blue, upper
    'northstar': (74, 42, 'pink'),         # black trail
    'royal-flush': (72, 26, 'pink'),       # black, upper
    'upper-northbrook': (70, 42, 'cyan'),  # blue, mid
    'lower-northbrook': (68, 58, 'yellow'),  # green, lower
    'snowdon-glades': (64, 54, 'pink'),    # black, lower left

    # === RAMSHEAD ===
    # Far right, x=82-100%, y=18-70%
    'easy-street': (90, 40, 'yellow'),     # green, major beginner trail
    'swirl': (94, 34, 'yellow'),           # green
    'treezy': (84, 56, 'yellow'),          # green, lower
    'squeeze-play': (88, 40, 'yellow'),    # green
    'ramshead-run': (92, 30, 'yellow'),    # green
    'ramshead-liftline': (84, 46, 'cyan'), # blue, liftline
    'header': (88, 34, 'cyan'),            # blue
    'vagabond': (90, 32, 'cyan'),          # blue
    'caper': (86, 40, 'cyan'),             # blue
    'timberline': (86, 44, 'cyan'),        # blue
    'start-park': (94, 34, 'yellow'),      # green
}


def run_sweepline():
    """Run the sweepline extraction and return all paths."""
    img = cv2.imread(MAP_PATH)
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Extract masks (same as sweepline_extract.py)
    cyan = cv2.inRange(hsv, np.array([88, 60, 130]), np.array([115, 255, 255]))
    pink = cv2.inRange(hsv, np.array([145, 50, 130]), np.array([172, 255, 255]))
    yellow = cv2.inRange(hsv, np.array([20, 80, 150]), np.array([48, 255, 255]))

    kernel = np.ones((2, 2), np.uint8)
    for mask in [cyan, pink, yellow]:
        cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1, dst=mask)

    masks = {'cyan': cyan, 'pink': pink, 'yellow': yellow}

    all_paths = []
    for color_name, mask in masks.items():
        paths = sweepline_trace(mask, w, h, band_height_px=6,
                                min_cluster_width=4, max_gap_bands=5)
        for p in paths:
            pts = p['points']
            if len(pts) < 3:
                continue
            xs = [pt[0] for pt in pts]
            ys = [pt[1] for pt in pts]
            all_paths.append({
                'points': pts,
                'color': color_name,
                'center_x': np.mean(xs),
                'center_y': np.mean(ys),
                'top_y': min(ys),
                'bot_y': max(ys),
                'left_x': min(xs),
                'right_x': max(xs),
                'height': max(ys) - min(ys),
                'num_points': len(pts),
            })

    return all_paths, img, w, h


def sweepline_trace(mask, w, h, band_height_px=6, min_cluster_width=4, max_gap_bands=5):
    """Trace trails using horizontal band sweepline."""
    num_bands = h // band_height_px
    active_trails = []
    completed_trails = []

    for band_idx in range(num_bands):
        y_start = band_idx * band_height_px
        y_end = min(y_start + band_height_px, h)
        y_center = (y_start + y_end) / 2
        y_pct = y_center / h * 100

        band = mask[y_start:y_end, :]
        col_projection = np.any(band > 0, axis=0).astype(np.uint8)

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
                    clusters.append({'x_pct': cx_pct, 'width': run_width})
        if in_run:
            run_width = w - run_start
            if run_width >= min_cluster_width:
                cx = (run_start + w) / 2
                clusters.append({'x_pct': cx / w * 100, 'width': run_width})

        used_clusters = set()
        for trail in active_trails:
            trail['gap'] += 1
            best_cluster = None
            best_dist = float('inf')
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

        for ci, cluster in enumerate(clusters):
            if ci not in used_clusters:
                active_trails.append({
                    'points': [(round(cluster['x_pct'], 1), round(y_pct, 1))],
                    'last_x': cluster['x_pct'],
                    'gap': 0,
                })

        still_active = []
        for trail in active_trails:
            if trail['gap'] > max_gap_bands:
                if len(trail['points']) >= 4:
                    completed_trails.append(trail)
            else:
                still_active.append(trail)
        active_trails = still_active

    for trail in active_trails:
        if len(trail['points']) >= 4:
            completed_trails.append(trail)

    return completed_trails


def simplify_path(points, target_points=12):
    """Simplify a path to ~target_points using Douglas-Peucker."""
    if len(points) <= target_points:
        return points

    pts = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
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

    if len(result) < 3:
        result = [points[0], points[len(points)//2], points[-1]]

    return result


def distance_to_path(label_x, label_y, path):
    """
    Compute distance from a label position to a path.
    Uses minimum distance from label to any point on the path,
    plus a penalty for being far from the path's center.
    """
    pts = path['points']

    # Minimum distance to any path point
    min_dist = float('inf')
    for px, py in pts:
        d = np.sqrt((label_x - px)**2 + (label_y - py)**2)
        if d < min_dist:
            min_dist = d

    # Also check distance to path center
    center_dist = np.sqrt((label_x - path['center_x'])**2 +
                          (label_y - path['center_y'])**2)

    # Weighted combination: prefer paths where the label is near the path
    return 0.6 * min_dist + 0.4 * center_dist


def match_trails_to_paths(all_paths):
    """
    Match each trail to the closest extracted path using label positions.
    Uses the Hungarian algorithm for globally optimal assignment within
    each color group, avoiding the greedy ordering problem.
    """
    from scipy.optimize import linear_sum_assignment

    matches = {}

    # Group trails and paths by color for independent matching
    for color in ['cyan', 'pink', 'yellow']:
        # Trails expecting this color
        color_trails = [(tid, *pos) for tid, pos in TRAIL_LABEL_POSITIONS.items()
                        if pos[2] == color]
        if not color_trails:
            continue

        # Paths of this color
        color_paths = [(i, p) for i, p in enumerate(all_paths) if p['color'] == color]
        if not color_paths:
            continue

        n_trails = len(color_trails)
        n_paths = len(color_paths)

        # Build cost matrix: distance from each trail label to each path
        # Shape: (n_trails, n_paths)
        cost = np.full((n_trails, n_paths), 1e6)

        for ti, (tid, lx, ly, _) in enumerate(color_trails):
            for pi, (path_idx, path) in enumerate(color_paths):
                cost[ti, pi] = distance_to_path(lx, ly, path)

        # Solve the assignment problem
        trail_indices, path_indices = linear_sum_assignment(cost)

        for ti, pi in zip(trail_indices, path_indices):
            tid = color_trails[ti][0]
            path_idx, path = color_paths[pi]
            dist = cost[ti, pi]

            if dist < 1e5:  # Valid match
                matches[tid] = {
                    'path': path,
                    'distance': dist,
                }

    return matches


def generate_trailpaths_ts(matches):
    """Generate corrected trailPaths.ts content."""
    lines = []
    lines.append("// Trail path coordinate data for polyline overlays on the trail map image.")
    lines.append("// Each trail is keyed by trail ID and contains an array of segments.")
    lines.append("// Each segment is an array of [x, y] percentage coordinate pairs (0-100)")
    lines.append("// matching the SVG viewBox=\"0 0 100 100\" used in ImageMap.tsx.")
    lines.append("//")
    lines.append("// Coordinates extracted from trail map image via OpenCV sweepline analysis.")
    lines.append("// Trail names matched to paths using label position proximity matching.")
    lines.append("// Image: killington-trail-map.jpg (4572x2704px)")
    lines.append("")
    lines.append("export type TrailPathSegment = [number, number][];")
    lines.append("")
    lines.append("export const trailPaths: Record<string, TrailPathSegment[]> = {")

    # Load trail info for peak grouping
    with open("src/data/trails.ts", 'r') as f:
        content = f.read()
    trails_by_peak = defaultdict(list)
    pattern = r"\{\s*id:\s*'([^']+)',\s*name:\s*'([^']*)'(?:.*?peak:\s*'([^']+)')"
    for match in re.finditer(pattern, content, re.DOTALL):
        trail_id, name, peak = match.groups()
        trails_by_peak[peak].append((trail_id, name))

    peak_order = ['snowshed', 'sunrise', 'bear-mountain', 'skye-peak',
                  'killington-peak', 'snowdon', 'ramshead']

    matched = 0
    total = 0

    for peak_id in peak_order:
        trails = trails_by_peak.get(peak_id, [])
        lines.append(f"\n  // === {peak_id.upper().replace('-', ' ')} ===")

        for trail_id, name in trails:
            total += 1
            if trail_id in matches:
                matched += 1
                path = matches[trail_id]['path']
                simplified = simplify_path(path['points'], target_points=12)
                pts_str = ", ".join(f"[{x}, {y}]" for x, y in simplified)
                lines.append(f"  '{trail_id}': [[{pts_str}]],")
            else:
                lines.append(f"  // '{trail_id}': no path matched")

    lines.append("};")

    print(f"\n  Matched {matched}/{total} trails")
    return "\n".join(lines)


def visualize_matches(img, matches, w, h):
    """Generate visualization of matched paths."""
    viz = img.copy()

    colors = {
        'cyan': (255, 255, 0),
        'pink': (255, 0, 255),
        'yellow': (0, 255, 255),
    }

    for trail_id, match_info in matches.items():
        path = match_info['path']
        color = colors.get(path['color'], (255, 255, 255))
        pts = [(int(x/100*w), int(y/100*h)) for x, y in path['points']]
        if len(pts) >= 2:
            cv2.polylines(viz, [np.array(pts)], False, color, 3, cv2.LINE_AA)

        # Draw label position
        if trail_id in TRAIL_LABEL_POSITIONS:
            lx, ly, _ = TRAIL_LABEL_POSITIONS[trail_id]
            lpx = int(lx / 100 * w)
            lpy = int(ly / 100 * h)
            cv2.circle(viz, (lpx, lpy), 5, (0, 0, 255), -1)

    # Grid
    for pct in range(0, 101, 10):
        x = int(pct / 100 * w)
        y = int(pct / 100 * h)
        if x < w:
            cv2.line(viz, (x, 0), (x, h), (0, 0, 180), 1)
        if y < h:
            cv2.line(viz, (0, y), (w, y), (0, 0, 180), 1)

    small = cv2.resize(viz, (w // 2, h // 2))
    cv2.imwrite("tools/label_matched_paths.jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print("Saved visualization to tools/label_matched_paths.jpg")


def main():
    print("=" * 70)
    print("  Label-Position Trail Name Matching")
    print("=" * 70)

    # Step 1: Extract all paths
    print("\n[1] Running sweepline extraction...")
    all_paths, img, w, h = run_sweepline()
    by_color = defaultdict(int)
    for p in all_paths:
        by_color[p['color']] += 1
    print(f"  Total paths: {len(all_paths)}")
    for c, n in sorted(by_color.items()):
        print(f"    {c}: {n}")

    # Step 2: Match trails to paths
    print("\n[2] Matching trails to paths by label position proximity...")
    matches = match_trails_to_paths(all_paths)

    # Print match details
    print("\n" + "=" * 70)
    print("  MATCH DETAILS")
    print("=" * 70)

    for trail_id in sorted(TRAIL_LABEL_POSITIONS.keys()):
        label_x, label_y, expected_color = TRAIL_LABEL_POSITIONS[trail_id]
        if trail_id in matches:
            m = matches[trail_id]
            path = m['path']
            dist = m['distance']
            print(f"  ✓ {trail_id:<30} label=({label_x:>5.1f},{label_y:>5.1f}) → "
                  f"path_center=({path['center_x']:>5.1f},{path['center_y']:>5.1f}) "
                  f"dist={dist:>5.1f} h={path['height']:>5.1f}% {path['color']}")
        else:
            print(f"  ✗ {trail_id:<30} label=({label_x:>5.1f},{label_y:>5.1f}) → NO MATCH")

    # Step 3: Generate output
    print("\n[3] Generating trailPaths.ts...")
    ts_content = generate_trailpaths_ts(matches)
    with open("src/data/trailPaths.ts", 'w') as f:
        f.write(ts_content)
    print("  Written to src/data/trailPaths.ts")

    # Step 4: Visualize
    print("\n[4] Visualizing...")
    visualize_matches(img, matches, w, h)

    # Step 5: Save match data
    match_data = {}
    for tid, m in matches.items():
        match_data[tid] = {
            'label_position': list(TRAIL_LABEL_POSITIONS[tid][:2]),
            'path_center': [round(m['path']['center_x'], 1), round(m['path']['center_y'], 1)],
            'distance': round(m['distance'], 1),
            'height': round(m['path']['height'], 1),
            'color': m['path']['color'],
        }
    with open("tools/label_match_data.json", 'w') as f:
        json.dump(match_data, f, indent=2)

    print("\n  Done!")


if __name__ == "__main__":
    main()
