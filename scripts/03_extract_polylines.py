#!/usr/bin/env python3
"""Step 3: Extract ordered polylines from color masks with heuristic scoring.

Combines skeletonization, heuristic filtering, and polyline simplification.
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from skimage.morphology import skeletonize

from utils.heuristics import (
    score_component,
    skeleton_endpoints_and_junctions,
    ordered_skeleton_points,
    compute_skeleton,
)
from utils.polyline_utils import (
    simplify_points,
    order_top_to_bottom,
    merge_collinear_segments,
    compute_arc_length,
    compute_span,
)

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
MASKS_DIR = OUTPUT_DIR / "masks"
SKELETONS_DIR = OUTPUT_DIR / "skeletons"
MOUNTAIN_MASK_PATH = OUTPUT_DIR / "masks" / "mountain_mask.png"
IMAGE_PATH = OUTPUT_DIR / "trailmap_300dpi.png"
META_PATH = OUTPUT_DIR / "image_meta.json"

# Trail colors to process (excludes lift lines and boundaries)
# Black includes both advanced (single black diamond) and expert (double black diamond)
TRAIL_COLORS = ["green", "blue", "black"]

# Minimum confidence score to keep a component
MIN_SCORE_ACCEPT = 5  # "probable" or better
MIN_SCORE_UNCERTAIN = 3  # keep for SAM 2 refinement


def load_mask(color_name: str) -> np.ndarray | None:
    path = MASKS_DIR / f"{color_name}_mask.png"
    if not path.exists():
        return None
    return cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)


def extract_components(mask: np.ndarray) -> list:
    """Extract individual connected components from a mask.

    Returns list of (component_mask, bbox, area) tuples.
    Each component_mask is the same size as the input mask.
    """
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
    components = []
    for i in range(1, num_labels):  # skip background (0)
        area = stats[i, cv2.CC_STAT_AREA]
        if area < 50:  # trail line 5px wide, 10px long = 50px area
            continue
        component_mask = ((labels == i) * 255).astype(np.uint8)
        bbox = {
            "x": int(stats[i, cv2.CC_STAT_LEFT]),
            "y": int(stats[i, cv2.CC_STAT_TOP]),
            "w": int(stats[i, cv2.CC_STAT_WIDTH]),
            "h": int(stats[i, cv2.CC_STAT_HEIGHT]),
        }
        components.append((component_mask, bbox, area))
    return components


def extract_all_branches_from_skeleton(skeleton: np.ndarray, max_branches: int = 20) -> list:
    """Extract ALL branches from a skeleton as separate polylines.

    Instead of following only the longest path (losing branches at junctions),
    this traces every segment between endpoints/junctions as a separate polyline.
    Returns list of lists of (y, x) tuples, up to max_branches.
    """
    skel = (skeleton > 0).astype(np.uint8)
    visited = np.zeros_like(skel, dtype=bool)
    all_segments = []

    endpoints, junctions = skeleton_endpoints_and_junctions(skeleton)
    junction_set = set(junctions)

    # Start from endpoints first
    starts = list(endpoints)
    if not starts:
        ys, xs = np.where(skel > 0)
        if len(ys) == 0:
            return []
        starts = [(ys[0], xs[0])]

    def trace_from(start_pt):
        """Trace a path from start_pt until endpoint, junction, or dead end."""
        segment = [start_pt]
        if not visited[start_pt[0], start_pt[1]]:
            visited[start_pt[0], start_pt[1]] = True
        current = start_pt
        while True:
            y, x = current
            found = False
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dy == 0 and dx == 0:
                        continue
                    ny, nx = y + dy, x + dx
                    if (0 <= ny < skel.shape[0] and 0 <= nx < skel.shape[1]
                            and skel[ny, nx] > 0 and not visited[ny, nx]):
                        visited[ny, nx] = True
                        current = (ny, nx)
                        segment.append(current)
                        found = True
                        if (ny, nx) in junction_set:
                            return segment, True  # hit junction
                        break
                if found:
                    break
            if not found:
                return segment, False  # dead end
        return segment, False

    for start in starts:
        if visited[start[0], start[1]]:
            continue
        seg, hit_junc = trace_from(start)
        if len(seg) >= 2:
            all_segments.append(seg)
        if len(all_segments) >= max_branches:
            break

    # Trace unvisited branches from junctions
    for junc in junctions:
        if len(all_segments) >= max_branches:
            break
        y, x = junc
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dy == 0 and dx == 0:
                    continue
                ny, nx = y + dy, x + dx
                if (0 <= ny < skel.shape[0] and 0 <= nx < skel.shape[1]
                        and skel[ny, nx] > 0 and not visited[ny, nx]):
                    seg, _ = trace_from((ny, nx))
                    seg.insert(0, junc)
                    if len(seg) >= 2:
                        all_segments.append(seg)
                    if len(all_segments) >= max_branches:
                        break

    return all_segments


def extract_polyline_from_skeleton(skeleton: np.ndarray) -> list:
    """Extract the longest polyline from a skeleton. Legacy wrapper."""
    branches = extract_all_branches_from_skeleton(skeleton)
    if not branches:
        return []
    return max(branches, key=len)


def process_color(color_name: str, mask: np.ndarray, mountain_mask=None) -> dict:
    """Process a color mask: skeletonize, trace connected components as polylines.

    Simple approach: skeleton of mask → connected components → each traced as a polyline.
    No heuristic scoring — precision filter validates quality downstream.
    """
    print(f"\n  Processing {color_name}...")

    results = {"accepted": [], "uncertain": [], "rejected": []}
    score_log = []

    # Skeletonize the ENTIRE mask at once (much faster than per-component)
    skeleton = compute_skeleton(mask)
    skel_px = np.count_nonzero(skeleton)
    print(f"    Skeleton: {skel_px:,} pixels")

    # Get connected components of the skeleton
    num_l, lbl, st, cent = cv2.connectedComponentsWithStats(skeleton)
    components_used = 0

    for i in range(1, num_l):
        area = st[i, cv2.CC_STAT_AREA]
        if area < 5:  # skip tiny dots
            continue

        comp_id = f"{color_name}_{i:04d}"
        x = st[i, cv2.CC_STAT_LEFT]
        y = st[i, cv2.CC_STAT_TOP]
        cw = st[i, cv2.CC_STAT_WIDTH]
        ch = st[i, cv2.CC_STAT_HEIGHT]

        # Get the skeleton pixels for this component, ordered as a path
        comp_skel = ((lbl == i) * 255).astype(np.uint8)
        ys, xs = np.where(comp_skel > 0)
        if len(ys) < 3:
            continue

        # For simple (non-branching) skeletons, just sort by y then x
        # For branching skeletons, extract branches
        endpoints, junctions = skeleton_endpoints_and_junctions(comp_skel)

        if len(junctions) == 0:
            # No branches — trace single path
            points = ordered_skeleton_points(comp_skel, endpoints)
            if len(points) >= 3:
                points = order_top_to_bottom(points)
                results["accepted"].append({
                    "id": comp_id,
                    "color": color_name,
                    "points": points,
                    "score": 5,
                    "classification": "accepted",
                    "area": area,
                    "bbox": {"x": int(x), "y": int(y), "w": int(cw), "h": int(ch)},
                })
                components_used += 1
        else:
            # Has branches — extract all paths
            branches = extract_all_branches_from_skeleton(comp_skel)
            branches.sort(key=len, reverse=True)
            # Keep longest + any branch >= 15 points
            selected = [branches[0]] if branches else []
            for b in branches[1:]:
                if len(b) >= 15:
                    selected.append(b)

            for bi, points in enumerate(selected):
                if len(points) < 3:
                    continue
                points = order_top_to_bottom(points)
                bid = f"{comp_id}_{bi}" if len(selected) > 1 else comp_id
                results["accepted"].append({
                    "id": bid,
                    "color": color_name,
                    "points": points,
                    "score": 5,
                    "classification": "accepted",
                    "area": area,
                    "bbox": {"x": int(x), "y": int(y), "w": int(cw), "h": int(ch)},
                })
            if selected:
                components_used += 1

    print(f"    Components used: {components_used}/{num_l-1}, "
          f"Polylines: {len(results['accepted'])}")

    return results, score_log


def main():
    if not IMAGE_PATH.exists():
        print("ERROR: Run 01_convert_pdf.py and 02_segment_colors.py first.")
        sys.exit(1)

    meta = json.loads(META_PATH.read_text())
    img_w, img_h = meta["width"], meta["height"]
    print(f"Image: {img_w}x{img_h}")

    SKELETONS_DIR.mkdir(parents=True, exist_ok=True)

    all_accepted = []
    all_uncertain = []
    all_score_logs = {}

    for color in TRAIL_COLORS:
        mask = load_mask(color)
        if mask is None:
            print(f"  Skipping {color} (no mask found)")
            continue

        results, score_log = process_color(color, mask)
        all_score_logs[color] = score_log

        # Simplify polylines — moderate epsilon balances point count and path accuracy
        for trail in results["accepted"]:
            num_pts = len(trail["points"])
            if num_pts > 200:
                epsilon = 2.0
            elif num_pts > 50:
                epsilon = 1.5
            else:
                epsilon = 1.0
            trail["points"] = simplify_points(trail["points"], epsilon=epsilon)

        all_accepted.extend(results["accepted"])
        all_uncertain.extend(results["uncertain"])

    # PRE-MERGE structural filter: remove noise polylines BEFORE merging
    # Uses LOCAL CONTRAST to distinguish drawn trail lines from terrain.
    # Trail lines are more saturated (blue/green) or darker (black) than
    # their immediate surroundings. Terrain noise has same color as surroundings.
    print(f"\nPre-merge structural filter (local contrast)...")
    if IMAGE_PATH.exists():
        orig_img = cv2.imread(str(IMAGE_PATH))
        orig_hsv = cv2.cvtColor(orig_img, cv2.COLOR_BGR2HSV)

        pre_filtered = []
        removed_pre = 0
        for trail in all_accepted:
            pts = trail["points"]
            # Sample up to 20 evenly-spaced points for efficiency
            step = max(1, len(pts) // 20)
            fg_vals = []
            bg_vals = []
            for py, px in pts[::step]:  # internal format is (y, x)
                py_i, px_i = int(py), int(px)
                if not (3 <= px_i < img_w - 3 and 3 <= py_i < img_h - 3):
                    continue
                # Foreground: 3x3 window at the point
                if trail["color"] == "black":
                    fg_vals.append(float(orig_hsv[py_i-1:py_i+2, px_i-1:px_i+2, 2].mean()))
                else:
                    fg_vals.append(float(orig_hsv[py_i-1:py_i+2, px_i-1:px_i+2, 1].mean()))
                # Background: ring 20px away, sample 8 directions
                ring_vals = []
                for angle_deg in range(0, 360, 45):
                    dx = int(40 * np.cos(np.radians(angle_deg)))
                    dy = int(40 * np.sin(np.radians(angle_deg)))
                    bx, by = px_i + dx, py_i + dy
                    if 1 <= bx < img_w - 1 and 1 <= by < img_h - 1:
                        if trail["color"] == "black":
                            ring_vals.append(float(orig_hsv[by-1:by+2, bx-1:bx+2, 2].mean()))
                        else:
                            ring_vals.append(float(orig_hsv[by-1:by+2, bx-1:bx+2, 1].mean()))
                if ring_vals:
                    bg_vals.append(np.mean(ring_vals))

            if not fg_vals or not bg_vals:
                removed_pre += 1
                continue

            fg_mean = np.mean(fg_vals)
            bg_mean = np.mean(bg_vals)
            if trail["color"] == "black":
                # Black trails: darker than surroundings (V_bg - V_trail)
                contrast = bg_mean - fg_mean
                min_contrast = 8
            else:
                # Blue/green trails: more saturated than surroundings (S_trail - S_bg)
                contrast = fg_mean - bg_mean
                min_contrast = 12

            if contrast >= min_contrast:
                pre_filtered.append(trail)
            else:
                removed_pre += 1
        all_accepted = pre_filtered
        print(f"  Removed {removed_pre} low-contrast polylines before merge")
        print(f"  Remaining: {len(all_accepted)}")

    # Multi-pass merge: per-color O(n²) merge
    # Skip colors with >500 segments (too slow), but merge others
    print(f"\nMerging segments (multi-pass, per-color)...")
    for pass_num, (dist_thresh, angle_thresh) in enumerate([
        (20, 30),   # Pass 1: conservative — close + collinear
        (40, 45),   # Pass 2: moderate — wider distance + angle
        (60, 60),   # Pass 3: aggressive — catch remaining gaps
    ], 1):
        merged_any = False
        for color in TRAIL_COLORS:
            color_segments = [t for t in all_accepted if t["color"] == color]
            if len(color_segments) <= 1:
                continue
            if len(color_segments) > 1000:
                if pass_num == 1:
                    print(f"  Skipping {color} merge ({len(color_segments)} segments)")
                continue
            points_list = [t["points"] for t in color_segments]
            merged = merge_collinear_segments(
                points_list,
                angle_threshold=angle_thresh,
                distance_threshold=dist_thresh,
            )
            if len(merged) < len(color_segments):
                merged_any = True
                # Build score lookup to inherit best score
                score_by_pts = {}
                for seg in color_segments:
                    if seg["points"]:
                        key = (tuple(seg["points"][0]), tuple(seg["points"][-1]))
                        score_by_pts[key] = max(seg["score"], score_by_pts.get(key, 0))
                # Remove old entries and add merged
                all_accepted = [t for t in all_accepted if t["color"] != color]
                for i, pts in enumerate(merged):
                    best_score = 0
                    for seg in color_segments:
                        if seg["points"] and seg["points"][0] in pts:
                            best_score = max(best_score, seg["score"])
                    all_accepted.append({
                        "id": f"{color}_m{pass_num}_{i:03d}",
                        "color": color,
                        "points": pts,
                        "score": best_score,
                        "classification": "merged",
                        "area": 0,
                        "bbox": {},
                    })
        counts = {c: len([t for t in all_accepted if t["color"] == c]) for c in TRAIL_COLORS}
        counts_str = ", ".join(f"{c}={n}" for c, n in counts.items())
        print(f"  Pass {pass_num} (dist={dist_thresh}, angle={angle_thresh}): {counts_str}")
        if not merged_any:
            break

    # Post-merge filtering: remove noise and low-contrast merged results
    print(f"\nPost-merge filtering...")
    before_count = len(all_accepted)

    # Size-dependent contrast filter: short polylines are likely noise and
    # need high contrast to survive. Long polylines are real trails that may
    # cross small terrain gaps, so they get a lower threshold.
    if IMAGE_PATH.exists():
        orig_img_pm = cv2.imread(str(IMAGE_PATH))
        orig_hsv_pm = cv2.cvtColor(orig_img_pm, cv2.COLOR_BGR2HSV)
        post_contrast_removed = 0
        post_filtered = []
        for trail in all_accepted:
            pts = trail["points"]
            arc = compute_arc_length(pts)
            step = max(1, len(pts) // 20)
            fg_v, bg_v = [], []
            for py, px in pts[::step]:
                py_i, px_i = int(py), int(px)
                if not (3 <= px_i < img_w - 3 and 3 <= py_i < img_h - 3):
                    continue
                ch = 2 if trail["color"] == "black" else 1
                fg_v.append(float(orig_hsv_pm[py_i-1:py_i+2, px_i-1:px_i+2, ch].mean()))
                ring = []
                for adeg in range(0, 360, 45):
                    dx = int(40 * np.cos(np.radians(adeg)))
                    dy = int(40 * np.sin(np.radians(adeg)))
                    bx, by = px_i + dx, py_i + dy
                    if 1 <= bx < img_w-1 and 1 <= by < img_h-1:
                        ring.append(float(orig_hsv_pm[by-1:by+2, bx-1:bx+2, ch].mean()))
                if ring:
                    bg_v.append(np.mean(ring))
            if fg_v and bg_v:
                fg_m, bg_m = np.mean(fg_v), np.mean(bg_v)
                c = (bg_m - fg_m) if trail["color"] == "black" else (fg_m - bg_m)
                # Short polylines (<150px arc): need high contrast (likely noise)
                # Long polylines (>=150px): lower threshold (real trails with gaps)
                if trail["color"] == "black":
                    min_c = 15 if arc < 150 else 5
                else:
                    min_c = 20 if arc < 150 else 8
                if c < min_c:
                    post_contrast_removed += 1
                    continue
            post_filtered.append(trail)
        all_accepted = post_filtered
        print(f"  Removed {post_contrast_removed} low-contrast polylines after merge")

    filtered = []
    removed_short = 0
    removed_tiny_span = 0

    for trail in all_accepted:
        pts = trail["points"]

        # Filter 1: minimum span (straight-line distance between endpoints)
        # Black trails (double diamonds) are often short steep runs
        min_span = 20 if trail["color"] == "black" else 30
        span = compute_span(pts)
        if span < min_span:
            removed_tiny_span += 1
            continue

        # Filter 2: minimum arc length
        min_arc = 30 if trail["color"] == "black" else 50
        arc = compute_arc_length(pts)
        if arc < min_arc:
            removed_short += 1
            continue

        filtered.append(trail)

    all_accepted = filtered
    print(f"  Removed {removed_tiny_span} tiny-span polylines")
    print(f"  Removed {removed_short} short-arc polylines")
    print(f"  Before: {before_count}, After: {len(all_accepted)}")

    # Per-point precision filtering in two passes:
    # 1. Endpoint trimming: remove leading/trailing low-contrast points
    # 2. Whole-polyline filter: remove polylines with <75% precision
    if IMAGE_PATH.exists():
        orig_img_pp = cv2.imread(str(IMAGE_PATH))
        orig_hsv_pp = cv2.cvtColor(orig_img_pp, cv2.COLOR_BGR2HSV)

        def point_contrast(py, px, color):
            """Compute local contrast for a single point."""
            py_i, px_i = int(py), int(px)
            if not (3 <= px_i < img_w - 3 and 3 <= py_i < img_h - 3):
                return None
            ch = 2 if color == "black" else 1
            fg = float(orig_hsv_pp[py_i-1:py_i+2, px_i-1:px_i+2, ch].mean())
            ring = []
            for adeg in range(0, 360, 45):
                dx = int(40 * np.cos(np.radians(adeg)))
                dy = int(40 * np.sin(np.radians(adeg)))
                bx, by = px_i + dx, py_i + dy
                if 1 <= bx < img_w-1 and 1 <= by < img_h-1:
                    ring.append(float(orig_hsv_pp[by-1:by+2, bx-1:bx+2, ch].mean()))
            if not ring:
                return None
            bg = np.mean(ring)
            return (bg - fg) if color == "black" else (fg - bg)

        # Pass 1: Endpoint trimming — trim leading/trailing low-contrast points
        trimmed_count = 0
        for trail in all_accepted:
            pts = trail["points"]
            if len(pts) < 6:
                continue
            # Compute contrast for all points
            contrasts = [point_contrast(py, px, trail["color"]) for py, px in pts]
            # Trim from start: remove up to 30% of points if contrast < 8
            max_trim = len(pts) // 3
            start_trim = 0
            for i in range(min(max_trim, len(contrasts))):
                if contrasts[i] is not None and contrasts[i] < 8:
                    start_trim = i + 1
                else:
                    break
            # Trim from end
            end_trim = len(pts)
            for i in range(len(contrasts) - 1, max(len(pts) - max_trim - 1, -1), -1):
                if contrasts[i] is not None and contrasts[i] < 8:
                    end_trim = i
                else:
                    break
            if start_trim > 0 or end_trim < len(pts):
                new_pts = pts[start_trim:end_trim]
                if len(new_pts) >= 3:
                    trail["points"] = new_pts
                    trimmed_count += 1
        print(f"  Trimmed endpoints on {trimmed_count} polylines")

        # Pass 2: Remove polylines with <75% per-point precision
        pp_removed = 0
        pp_filtered = []
        for trail in all_accepted:
            pts = trail["points"]
            if len(pts) < 4:
                pp_filtered.append(trail)
                continue
            high_c, total = 0, 0
            for py, px in pts:
                c = point_contrast(py, px, trail["color"])
                if c is None:
                    continue
                total += 1
                if c >= 10:
                    high_c += 1
            # Per-color thresholds: black trails (adaptive threshold) have
            # inherently lower per-point contrast, so use a lower threshold.
            min_prec = 0.75 if trail["color"] == "black" else 0.78
            if total > 0 and high_c / total < min_prec:
                pp_removed += 1
                continue
            pp_filtered.append(trail)
        all_accepted = pp_filtered
        print(f"  Removed {pp_removed} low-precision polylines")

    # Base-area filter: remove polylines in the bottom of the image that are
    # tracing roads, parking lots, or base-area features rather than ski trails.
    # Ski trails end at base lodges around y=70-75%. Below that, blue/green
    # markings are typically access roads, signage, or map decorations.
    # We use a graduated approach:
    #   - Above 65% y: keep everything (definitely on-mountain)
    #   - 65-80% y: keep only if high contrast (real trails stand out)
    #   - Below 80% y: remove (base area / parking / roads)
    base_removed = 0
    base_filtered = []
    for trail in all_accepted:
        pts = trail["points"]
        cy = np.mean([py for py, px in pts])
        y_pct = cy / img_h * 100
        if y_pct <= 65:
            base_filtered.append(trail)
        elif y_pct <= 80:
            # In transition zone: keep only if polyline has strong contrast
            # (real trails connecting to base have vivid color)
            if IMAGE_PATH.exists() and trail["color"] != "black":
                step = max(1, len(pts) // 15)
                fg_v, bg_v = [], []
                for py, px in pts[::step]:
                    py_i, px_i = int(py), int(px)
                    if not (3 <= px_i < img_w - 3 and 3 <= py_i < img_h - 3):
                        continue
                    ch = 1  # saturation for blue/green
                    fg_v.append(float(orig_hsv_pp[py_i-1:py_i+2, px_i-1:px_i+2, ch].mean()))
                    ring = []
                    for adeg in range(0, 360, 45):
                        dx = int(40 * np.cos(np.radians(adeg)))
                        dy = int(40 * np.sin(np.radians(adeg)))
                        bx, by = px_i + dx, py_i + dy
                        if 1 <= bx < img_w-1 and 1 <= by < img_h-1:
                            ring.append(float(orig_hsv_pp[by-1:by+2, bx-1:bx+2, ch].mean()))
                    if ring:
                        bg_v.append(np.mean(ring))
                if fg_v and bg_v:
                    contrast = np.mean(fg_v) - np.mean(bg_v)
                    if contrast >= 20:  # high contrast = real trail
                        base_filtered.append(trail)
                    else:
                        base_removed += 1
                else:
                    base_filtered.append(trail)
            else:
                base_filtered.append(trail)  # keep black trails in transition zone
        else:
            base_removed += 1  # below 80% = remove
    all_accepted = base_filtered
    print(f"  Removed {base_removed} base-area polylines")

    # Symbol extension pass: AFTER all filtering, extend/add polylines for
    # unmatched difficulty symbols. Symbols are definitive trail markers, so
    # we trust them even if the trail line was too faint for the contrast filter.
    print(f"\nSymbol extension pass (post-filter)...")
    symbols_path = OUTPUT_DIR / "symbols.json"
    if symbols_path.exists():
        sym_data = json.loads(symbols_path.read_text())
        symbol_extensions = 0
        symbol_stubs = 0
        for color in TRAIL_COLORS:
            sym_positions = sym_data.get(color, [])
            if not sym_positions:
                continue
            color_polylines = [t for t in all_accepted if t["color"] == color]
            for sx, sy in sym_positions:
                # Check if already matched at 50px
                found = False
                for t in color_polylines:
                    for py, px in t["points"]:
                        if abs(px - sx) <= 50 and abs(py - sy) <= 50:
                            found = True
                            break
                    if found:
                        break
                if found:
                    continue

                # Unmatched symbol — find nearest polyline endpoint within 200px
                best_dist = float('inf')
                best_trail = None
                best_end = None  # 'start' or 'end'
                for t in color_polylines:
                    if not t["points"]:
                        continue
                    # Check start point
                    py0, px0 = t["points"][0]
                    d0 = ((px0 - sx)**2 + (py0 - sy)**2)**0.5
                    if d0 < best_dist:
                        best_dist = d0
                        best_trail = t
                        best_end = 'start'
                    # Check end point
                    py1, px1 = t["points"][-1]
                    d1 = ((px1 - sx)**2 + (py1 - sy)**2)**0.5
                    if d1 < best_dist:
                        best_dist = d1
                        best_trail = t
                        best_end = 'end'

                if best_trail is not None and best_dist <= 250:
                    # Extend the nearest polyline toward the symbol
                    sym_pt = (sy, sx)  # internal (y, x) format
                    if best_end == 'start':
                        best_trail["points"].insert(0, sym_pt)
                    else:
                        best_trail["points"].append(sym_pt)
                    symbol_extensions += 1
                else:
                    # Too far from any polyline — skip (don't create stubs,
                    # they hurt precision without adding useful geometry)
                    symbol_stubs += 1
        print(f"  Extended {symbol_extensions} polylines, {symbol_stubs} symbols too far")

    # Save results
    print(f"\nTotal accepted: {len(all_accepted)}")
    print(f"Total uncertain: {len(all_uncertain)}")

    # Convert to serializable format
    output = {
        "image_width": img_w,
        "image_height": img_h,
        "accepted": [],
        "uncertain": [],
    }

    for trail in all_accepted:
        output["accepted"].append({
            "id": trail["id"],
            "color": trail["color"],
            "points": [[int(x), int(y)] for y, x in trail["points"]],  # convert to [x,y]
            "num_points": len(trail["points"]),
            "score": trail["score"],
            "classification": trail["classification"],
        })

    for trail in all_uncertain:
        output["uncertain"].append({
            "id": trail["id"],
            "color": trail["color"],
            "points": [[int(x), int(y)] for y, x in trail["points"]],
            "num_points": len(trail["points"]),
            "score": trail["score"],
        })

    output_path = OUTPUT_DIR / "extracted_polylines.json"
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nSaved polylines to {output_path}")

    # Save score logs for debugging
    log_path = OUTPUT_DIR / "score_logs.json"
    # Make score logs serializable
    serializable_logs = {}
    for color, logs in all_score_logs.items():
        serializable_logs[color] = []
        for log in logs:
            serializable_log = {}
            for k, v in log.items():
                if isinstance(v, (np.integer, np.floating)):
                    serializable_log[k] = float(v)
                elif isinstance(v, np.ndarray):
                    serializable_log[k] = v.tolist()
                else:
                    serializable_log[k] = v
            serializable_logs[color].append(serializable_log)
    log_path.write_text(json.dumps(serializable_logs, indent=2))
    print(f"Saved score logs to {log_path}")


if __name__ == "__main__":
    main()
