#!/usr/bin/env python3
"""
Improved trail extraction pipeline:
1. Extract trail lines by color from the map image
2. Use aggressive morphological ops to connect fragmented segments
3. Find connected components = individual trail paths
4. Skeletonize each component to get center line
5. Assign paths to peak regions
6. Within each peak, sort and match to trail names
7. Output trailPaths.ts data
"""

import cv2
import numpy as np
from collections import defaultdict
import json
import re

MAP_PATH = "public/killington-trail-map.jpg"
TRAILS_PATH = "src/data/trails.ts"

# Peak regions on the map (x_min%, x_max%, y_min%, y_max%)
# Based on sign detection and visual analysis
PEAK_REGIONS = {
    'snowshed':        (0, 10, 40, 82),
    'sunrise':         (3, 16, 35, 62),
    'bear-mountain':   (14, 38, 15, 68),
    'skye-peak':       (28, 57, 5, 68),
    'killington-peak': (42, 66, 3, 62),
    'snowdon':         (62, 88, 10, 65),
    'ramshead':        (82, 100, 18, 70),
}

# Trail difficulty -> expected color on the map
# green/easy = yellow/green lines, blue/intermediate = cyan/blue, black/expert = pink/magenta
DIFFICULTY_TO_COLOR = {
    'green': 'yellow',
    'blue': 'cyan',
    'black': 'pink',
    'double-black': 'pink',
}


def load_image():
    img = cv2.imread(MAP_PATH)
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return img, hsv, w, h


def extract_masks(hsv):
    """Extract trail color masks with aggressive connection."""
    # Cyan/blue trails (intermediate)
    cyan = cv2.inRange(hsv, np.array([85, 45, 100]), np.array([118, 255, 255]))
    # Pink/magenta trails (advanced/expert)
    pink = cv2.inRange(hsv, np.array([140, 40, 100]), np.array([175, 255, 255]))
    # Yellow/green trails (beginner)
    yellow = cv2.inRange(hsv, np.array([18, 45, 100]), np.array([52, 255, 255]))
    # Red trails/markers
    red1 = cv2.inRange(hsv, np.array([0, 60, 100]), np.array([10, 255, 255]))
    red2 = cv2.inRange(hsv, np.array([170, 60, 100]), np.array([180, 255, 255]))
    red = cv2.bitwise_or(red1, red2)
    # Green (pure green, different from yellow-green)
    green = cv2.inRange(hsv, np.array([52, 50, 100]), np.array([85, 255, 255]))

    return {'cyan': cyan, 'pink': pink, 'yellow': yellow, 'red': red, 'green': green}


def connect_and_extract(mask, w, h, color_name, min_area=80, connect_radius=8):
    """
    Connect fragmented trail segments, then extract individual paths.
    Uses dilation to bridge gaps, then finds connected components,
    then skeletonizes each component for center-line paths.
    """
    # Aggressive closing to bridge gaps (trail labels, icons break lines)
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (connect_radius, connect_radius))
    connected = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close, iterations=2)

    # Small open to remove noise
    kernel_open = np.ones((2, 2), np.uint8)
    connected = cv2.morphologyEx(connected, cv2.MORPH_OPEN, kernel_open, iterations=1)

    # Find connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(connected, connectivity=8)

    paths = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < min_area:
            continue

        bx = stats[i, cv2.CC_STAT_LEFT]
        by = stats[i, cv2.CC_STAT_TOP]
        bw = stats[i, cv2.CC_STAT_WIDTH]
        bh = stats[i, cv2.CC_STAT_HEIGHT]

        # Skip very wide/short shapes (likely text or signs, not trails)
        if bw > 0 and bh > 0:
            aspect = bw / bh
            if aspect > 8 and bh < 20:
                continue  # likely text

        # Create mask for just this component
        comp_mask = (labels == i).astype(np.uint8) * 255

        # Skeletonize this component to get center line
        skel = skeletonize(comp_mask)
        skel_pts = cv2.countNonZero(skel)

        if skel_pts < 5:
            continue

        # Extract ordered path from skeleton
        path_points = order_skeleton_points(skel, w, h)

        if len(path_points) < 3:
            continue

        # Simplify path using Douglas-Peucker
        path_points = simplify_path(path_points, tolerance=0.3)

        cx = np.mean([p[0] for p in path_points])
        cy = np.mean([p[1] for p in path_points])

        paths.append({
            'points': path_points,
            'area': area,
            'color': color_name,
            'center_x': cx,
            'center_y': cy,
            'top_y': min(p[1] for p in path_points),
            'bot_y': max(p[1] for p in path_points),
            'left_x': min(p[0] for p in path_points),
            'right_x': max(p[0] for p in path_points),
            'height': max(p[1] for p in path_points) - min(p[1] for p in path_points),
        })

    # Sort by area descending
    paths.sort(key=lambda p: p['area'], reverse=True)
    return paths


def skeletonize(mask):
    """Thin a binary mask to 1-pixel skeleton."""
    skel = np.zeros_like(mask)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    temp = mask.copy()
    while True:
        eroded = cv2.erode(temp, element)
        opened = cv2.dilate(eroded, element)
        sub = cv2.subtract(temp, opened)
        skel = cv2.bitwise_or(skel, sub)
        temp = eroded.copy()
        if cv2.countNonZero(temp) == 0:
            break
    return skel


def order_skeleton_points(skel, w, h):
    """
    Order skeleton pixels into a path from top to bottom.
    Walk the skeleton from the topmost point, following connected pixels.
    """
    ys, xs = np.where(skel > 0)
    if len(xs) == 0:
        return []

    # Build adjacency: for each pixel, find its skeleton neighbors
    points = set(zip(xs.tolist(), ys.tolist()))

    # Start from the topmost point (or leftmost if tied)
    start_idx = np.lexsort((xs, ys))[0]
    start = (xs[start_idx], ys[start_idx])

    # Walk the skeleton using BFS/greedy from start
    visited = set()
    path = []
    current = start
    visited.add(current)
    path.append(current)

    while True:
        cx, cy = current
        # Find unvisited neighbors (8-connected)
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in points and (nx, ny) not in visited:
                    neighbors.append((nx, ny))

        if not neighbors:
            break

        # Prefer continuing in same direction, else pick the one going most downward
        if len(path) >= 2:
            prev = path[-2]
            dx_prev = current[0] - prev[0]
            dy_prev = current[1] - prev[1]
            # Score each neighbor by how well it continues the direction
            def direction_score(n):
                dx_n = n[0] - current[0]
                dy_n = n[1] - current[1]
                # Dot product with previous direction
                return dx_n * dx_prev + dy_n * dy_prev
            neighbors.sort(key=direction_score, reverse=True)
        else:
            # Prefer going down
            neighbors.sort(key=lambda n: n[1])

        next_pt = neighbors[0]
        visited.add(next_pt)
        path.append(next_pt)
        current = next_pt

    # Convert to percentages
    pct_path = [(round(x / w * 100, 1), round(y / h * 100, 1)) for x, y in path]

    # Subsample if too many points (keep ~15-25 points)
    if len(pct_path) > 25:
        step = len(pct_path) // 20
        sampled = pct_path[::step]
        if sampled[-1] != pct_path[-1]:
            sampled.append(pct_path[-1])
        pct_path = sampled

    return pct_path


def simplify_path(points, tolerance=0.3):
    """Douglas-Peucker path simplification."""
    if len(points) <= 3:
        return points

    pts = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
    epsilon = tolerance
    simplified = cv2.approxPolyDP(pts, epsilon, False)
    result = [(round(float(p[0][0]), 1), round(float(p[0][1]), 1)) for p in simplified]

    # Ensure minimum 3 points
    if len(result) < 3 and len(points) >= 3:
        return [points[0], points[len(points)//2], points[-1]]

    return result


def assign_to_peaks(paths):
    """Assign each extracted path to a peak region."""
    assigned = defaultdict(list)
    unassigned = []

    for path in paths:
        cx = path['center_x']
        cy = path['center_y']

        best_peak = None
        best_dist = float('inf')

        for peak_id, (x_min, x_max, y_min, y_max) in PEAK_REGIONS.items():
            # Check if center is within region (with some tolerance)
            margin = 3
            if (x_min - margin) <= cx <= (x_max + margin) and (y_min - margin) <= cy <= (y_max + margin):
                rcx = (x_min + x_max) / 2
                rcy = (y_min + y_max) / 2
                dist = np.sqrt((cx - rcx)**2 + (cy - rcy)**2)
                if dist < best_dist:
                    best_dist = dist
                    best_region = peak_id
                    best_peak = peak_id

        if best_peak:
            assigned[best_peak].append(path)
        else:
            unassigned.append(path)

    return assigned, unassigned


def parse_trails_ts():
    """Parse trails.ts to get trail definitions by peak."""
    with open(TRAILS_PATH, 'r') as f:
        content = f.read()

    trails_by_peak = defaultdict(list)
    # Match trail definitions
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


def match_trails_to_paths(trails, paths):
    """
    Match trail definitions to extracted paths within a peak region.
    Strategy: match by color (difficulty) and position.
    """
    matches = {}

    # Group paths by color
    paths_by_color = defaultdict(list)
    for p in paths:
        paths_by_color[p['color']].append(p)

    # Group trails by expected color
    trails_by_color = defaultdict(list)
    for t in trails:
        trails_by_color[t['expected_color']].append(t)

    # For each color group, sort trails and paths by x-position, then match
    for color in ['cyan', 'pink', 'yellow']:
        color_trails = sorted(trails_by_color.get(color, []),
                              key=lambda t: t.get('sort_key', t['id']))
        color_paths = sorted(paths_by_color.get(color, []),
                             key=lambda p: (p['center_x'], p['center_y']))

        # Also include green paths for yellow trails
        if color == 'yellow':
            green_paths = sorted(paths_by_color.get('green', []),
                                 key=lambda p: (p['center_x'], p['center_y']))
            color_paths = sorted(color_paths + green_paths,
                                 key=lambda p: (p['center_x'], p['center_y']))

        if not color_trails or not color_paths:
            continue

        # Simple greedy matching: for each trail, find nearest unmatched path
        used_paths = set()
        for trail in color_trails:
            best_path = None
            best_score = float('inf')

            for j, path in enumerate(color_paths):
                if j in used_paths:
                    continue
                # Score based on path size (prefer larger/longer paths)
                # and height (prefer paths with decent vertical extent)
                score = -path['area']  # negative because we want largest
                if path['height'] < 2:
                    score += 10000  # penalty for very short paths

                if score < best_score:
                    best_score = score
                    best_path = j

            if best_path is not None:
                used_paths.add(best_path)
                matches[trail['id']] = color_paths[best_path]

    return matches


def generate_ts_output(all_matches, trails_by_peak):
    """Generate the trailPaths.ts content from matched paths."""
    lines = []
    lines.append("// Trail path coordinate data for polyline overlays on the trail map image.")
    lines.append("// Each trail is keyed by trail ID and contains an array of segments.")
    lines.append("// Each segment is an array of [x, y] percentage coordinate pairs (0-100)")
    lines.append("// matching the SVG viewBox=\"0 0 100 100\" used in ImageMap.tsx.")
    lines.append("//")
    lines.append("// Coordinates extracted from trail map image using OpenCV color detection,")
    lines.append("// skeletonization, and path tracing.")
    lines.append("//")
    lines.append("// Image: killington-trail-map.jpg (4572x2704px)")
    lines.append("")
    lines.append("export type TrailPathSegment = [number, number][];")
    lines.append("")
    lines.append("export const trailPaths: Record<string, TrailPathSegment[]> = {")

    peak_order = ['snowshed', 'sunrise', 'bear-mountain', 'skye-peak',
                  'killington-peak', 'snowdon', 'ramshead']

    for peak_id in peak_order:
        trails = trails_by_peak.get(peak_id, [])
        lines.append(f"\n  // === {peak_id.upper().replace('-', ' ')} ===")

        for trail in trails:
            tid = trail['id']
            if tid in all_matches:
                path = all_matches[tid]
                pts = path['points']
                pts_str = ", ".join(f"[{x}, {y}]" for x, y in pts)
                lines.append(f"  '{tid}': [[{pts_str}]],")
            else:
                lines.append(f"  // '{tid}': no CV path extracted")

    lines.append("};")
    return "\n".join(lines)


def visualize_results(img, all_matches, w, h):
    """Draw extracted paths on the map for verification."""
    viz = img.copy()

    color_map = {
        'cyan': (255, 255, 0),
        'pink': (255, 0, 255),
        'yellow': (0, 255, 255),
        'red': (0, 0, 255),
        'green': (0, 255, 0),
    }

    for trail_id, path in all_matches.items():
        color = color_map.get(path['color'], (255, 255, 255))
        pts = [(int(x/100*w), int(y/100*h)) for x, y in path['points']]
        if len(pts) >= 2:
            cv2.polylines(viz, [np.array(pts)], False, color, 3, cv2.LINE_AA)
            # Label the trail
            mid = pts[len(pts)//2]
            cv2.putText(viz, trail_id[:15], (mid[0]+5, mid[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

    # Grid
    for pct in range(0, 101, 10):
        x = int(pct / 100 * w)
        y = int(pct / 100 * h)
        if x < w:
            cv2.line(viz, (x, 0), (x, h), (0, 0, 180), 1)
        if y < h:
            cv2.line(viz, (0, y), (w, y), (0, 0, 180), 1)

    small = cv2.resize(viz, (w // 2, h // 2))
    cv2.imwrite("tools/cv_matched_paths.jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print("Saved visualization to tools/cv_matched_paths.jpg")


def main():
    print("=" * 70)
    print("  Trail Path Extraction and Assignment Pipeline")
    print("=" * 70)

    img, hsv, w, h = load_image()
    print(f"Image: {w}x{h}")

    # Step 1: Extract color masks
    print("\n[Step 1] Extracting trail color masks...")
    masks = extract_masks(hsv)
    for name, mask in masks.items():
        print(f"  {name}: {cv2.countNonZero(mask):,} pixels")

    # Step 2: Connect fragments and extract paths per color
    print("\n[Step 2] Connecting fragments and extracting paths...")
    all_paths = []
    for color_name in ['cyan', 'pink', 'yellow', 'green']:
        paths = connect_and_extract(masks[color_name], w, h, color_name,
                                     min_area=100, connect_radius=10)
        print(f"  {color_name}: {len(paths)} paths extracted")
        # Print top 5
        for i, p in enumerate(paths[:5]):
            print(f"    #{i+1}: area={p['area']}, center=({p['center_x']:.1f}, {p['center_y']:.1f}), "
                  f"height={p['height']:.1f}%, {len(p['points'])} pts")
        all_paths.extend(paths)

    print(f"\n  Total paths: {len(all_paths)}")

    # Step 3: Assign to peak regions
    print("\n[Step 3] Assigning paths to peak regions...")
    assigned, unassigned = assign_to_peaks(all_paths)
    for peak_id in ['snowshed', 'sunrise', 'bear-mountain', 'skye-peak',
                    'killington-peak', 'snowdon', 'ramshead']:
        peak_paths = assigned.get(peak_id, [])
        print(f"  {peak_id}: {len(peak_paths)} paths")
        for color in ['cyan', 'pink', 'yellow', 'green']:
            count = sum(1 for p in peak_paths if p['color'] == color)
            if count:
                print(f"    {color}: {count}")
    print(f"  Unassigned: {len(unassigned)} paths")

    # Step 4: Parse trail definitions
    print("\n[Step 4] Parsing trail definitions from trails.ts...")
    trails_by_peak = parse_trails_ts()
    for peak_id, trails in trails_by_peak.items():
        print(f"  {peak_id}: {len(trails)} trails")

    # Step 5: Match trails to paths
    print("\n[Step 5] Matching trails to extracted paths...")
    all_matches = {}
    for peak_id in trails_by_peak:
        peak_paths = assigned.get(peak_id, [])
        peak_trails = trails_by_peak[peak_id]
        matches = match_trails_to_paths(peak_trails, peak_paths)
        all_matches.update(matches)
        matched = len(matches)
        total = len(peak_trails)
        print(f"  {peak_id}: {matched}/{total} trails matched")

    print(f"\n  Total matched: {len(all_matches)}/{sum(len(t) for t in trails_by_peak.values())} trails")

    # Step 6: Generate output
    print("\n[Step 6] Generating trailPaths.ts...")
    ts_content = generate_ts_output(all_matches, trails_by_peak)
    with open("tools/cv_trailPaths.ts", 'w') as f:
        f.write(ts_content)
    print("  Saved to tools/cv_trailPaths.ts")

    # Step 7: Visualize
    print("\n[Step 7] Generating visualization...")
    visualize_results(img, all_matches, w, h)

    # Step 8: Output summary with paths for manual review
    print("\n" + "=" * 70)
    print("  MATCHED TRAILS SUMMARY")
    print("=" * 70)
    for peak_id in ['snowshed', 'sunrise', 'bear-mountain', 'skye-peak',
                    'killington-peak', 'snowdon', 'ramshead']:
        print(f"\n--- {peak_id} ---")
        for trail in trails_by_peak.get(peak_id, []):
            tid = trail['id']
            if tid in all_matches:
                p = all_matches[tid]
                pts = p['points']
                pts_preview = " → ".join(f"({x},{y})" for x, y in pts[:4])
                if len(pts) > 4:
                    pts_preview += f" ... ({len(pts)} pts)"
                print(f"  ✓ {tid}: {p['color']}, {pts_preview}")
            else:
                print(f"  ✗ {tid}: NOT MATCHED ({trail['expected_color']})")

    print("\n" + "=" * 70)
    print("  Done!")
    print("=" * 70)


if __name__ == "__main__":
    main()
