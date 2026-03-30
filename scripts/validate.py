#!/usr/bin/env python3
"""Automated validation of trail extraction pipeline.

Measures coverage, quality, and identifies gaps. Run after Steps 1-3 + 6.

Usage:
    python scripts/validate.py              # Full validation report
    python scripts/validate.py --visual     # Also produce visual diff images
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
IMAGE_PATH = OUTPUT_DIR / "trailmap_300dpi.png"
POLYLINES_PATH = OUTPUT_DIR / "extracted_polylines.json"
META_PATH = OUTPUT_DIR / "image_meta.json"
READABLE_DIR = OUTPUT_DIR / "readable"

# Known trail counts from trails.ts
EXPECTED_TRAILS = {
    "green": 21,   # easy trails
    "blue": 55,    # intermediate trails (includes some that might show as cyan)
    "black": 27,   # advanced trails (black diamonds)
    "red": 12,     # expert/double-black trails (if detected as red)
    # Note: some double-blacks may show as black or red on the map
}
TOTAL_EXPECTED = 133  # total trails in trails.ts (excluding terrain parks/glades that may not have lines)

# Difficulty mapping: trail color -> expected map color(s)
# Some colors overlap — blue trails and cyan lifts are similar
DIFFICULTY_TO_COLORS = {
    "green": ["green"],
    "blue": ["blue"],
    "black": ["black"],
    "double-black": ["red", "black"],  # could appear as either
}


def load_data():
    meta = json.loads(META_PATH.read_text())
    polylines = json.loads(POLYLINES_PATH.read_text())
    return meta, polylines


def coverage_analysis(polylines: dict, meta: dict):
    """Analyze how well the extracted polylines cover the trail map."""
    accepted = polylines["accepted"]
    uncertain = polylines.get("uncertain", [])
    img_w, img_h = meta["width"], meta["height"]

    print("=" * 60)
    print("COVERAGE ANALYSIS")
    print("=" * 60)

    # Count by color
    from collections import Counter
    color_counts = Counter(t["color"] for t in accepted)
    print(f"\nExtracted polylines by color:")
    total = 0
    for color in ["green", "blue", "red", "black"]:
        count = color_counts.get(color, 0)
        expected = EXPECTED_TRAILS.get(color, "?")
        ratio = f"{count}/{expected}" if isinstance(expected, int) else f"{count}"
        status = ""
        if isinstance(expected, int):
            if count >= expected * 0.8:
                status = "GOOD"
            elif count >= expected * 0.5:
                status = "PARTIAL"
            else:
                status = "LOW"
        print(f"  {color:10s}: {ratio:>8s} segments  {status}")
        total += count

    print(f"  {'TOTAL':10s}: {total:>4d}/{TOTAL_EXPECTED} segments")
    print(f"  Uncertain:  {len(uncertain)} (candidates for SAM 2)")

    # Coverage percentage
    coverage_pct = total / TOTAL_EXPECTED * 100 if TOTAL_EXPECTED > 0 else 0
    print(f"\n  Overall coverage: {coverage_pct:.1f}%")

    if coverage_pct >= 80:
        print("  Status: GOOD - most trails detected")
    elif coverage_pct >= 60:
        print("  Status: PARTIAL - many trails detected, some missing")
    else:
        print("  Status: LOW - significant trails missing, consider adjusting thresholds")

    return coverage_pct


def quality_analysis(polylines: dict, meta: dict):
    """Analyze quality of extracted polylines."""
    accepted = polylines["accepted"]

    print("\n" + "=" * 60)
    print("QUALITY ANALYSIS")
    print("=" * 60)

    # Point count distribution
    point_counts = [t["num_points"] for t in accepted]
    if not point_counts:
        print("\n  No polylines to analyze!")
        return

    print(f"\n  Points per polyline:")
    print(f"    Min: {min(point_counts)}")
    print(f"    Max: {max(point_counts)}")
    print(f"    Mean: {sum(point_counts)/len(point_counts):.1f}")
    print(f"    Median: {sorted(point_counts)[len(point_counts)//2]}")

    # Very short polylines (might be noise)
    short = sum(1 for p in point_counts if p <= 3)
    if short > 0:
        print(f"\n  WARNING: {short} polylines have <=3 points (may be noise)")

    # Score distribution
    scores = [t.get("score", 0) for t in accepted]
    from collections import Counter
    score_dist = Counter(scores)
    print(f"\n  Heuristic score distribution:")
    for s in sorted(score_dist.keys()):
        bar = "#" * score_dist[s]
        print(f"    Score {s}: {score_dist[s]:3d} {bar}")

    # Classification distribution
    classes = Counter(t.get("classification", "unknown") for t in accepted)
    print(f"\n  Classifications:")
    for cls, count in classes.most_common():
        print(f"    {cls}: {count}")


def spatial_coverage(polylines: dict, meta: dict):
    """Check spatial distribution — are all areas of the mountain covered?"""
    accepted = polylines["accepted"]
    img_w, img_h = meta["width"], meta["height"]

    print("\n" + "=" * 60)
    print("SPATIAL COVERAGE")
    print("=" * 60)

    # Divide image into peak regions and check each has polylines
    regions = {
        "Snowshed (far left)": {"x": (0, 16), "y": (30, 100)},
        "Sunrise": {"x": (10, 25), "y": (25, 100)},
        "Ramshead": {"x": (18, 38), "y": (15, 100)},
        "Snowdon": {"x": (30, 52), "y": (10, 100)},
        "Skye Peak": {"x": (42, 72), "y": (5, 100)},
        "Killington Peak": {"x": (60, 88), "y": (0, 100)},
        "Bear Mountain (far right)": {"x": (80, 100), "y": (10, 100)},
    }

    for region_name, bounds in regions.items():
        count = 0
        for trail in accepted:
            pts = trail["points"]
            if not pts:
                continue
            # Centroid as percentage
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            cx = sum(xs) / len(xs) / img_w * 100
            cy = sum(ys) / len(ys) / img_h * 100
            if bounds["x"][0] <= cx <= bounds["x"][1] and bounds["y"][0] <= cy <= bounds["y"][1]:
                count += 1

        status = "OK" if count >= 5 else "LOW" if count >= 2 else "EMPTY"
        print(f"  {region_name:30s}: {count:3d} polylines  [{status}]")


def gap_analysis(polylines: dict, meta: dict):
    """Identify trails with gaps (fragmented into multiple segments)."""
    accepted = polylines["accepted"]
    img_w, img_h = meta["width"], meta["height"]

    print("\n" + "=" * 60)
    print("GAP / FRAGMENTATION ANALYSIS")
    print("=" * 60)

    # For each color, find polylines whose endpoints are close to each other
    # (suggesting they're fragments of the same trail)
    from collections import defaultdict
    colors = defaultdict(list)
    for trail in accepted:
        pts = trail["points"]
        if len(pts) < 2:
            continue
        start = pts[0]
        end = pts[-1]
        colors[trail["color"]].append({
            "id": trail["id"],
            "start": start,
            "end": end,
        })

    gap_pairs = 0
    for color, trails in colors.items():
        for i in range(len(trails)):
            for j in range(i + 1, len(trails)):
                # Check if end of trail i is near start of trail j (or vice versa)
                for end_a, start_b in [(trails[i]["end"], trails[j]["start"]),
                                       (trails[i]["end"], trails[j]["end"]),
                                       (trails[i]["start"], trails[j]["start"]),
                                       (trails[i]["start"], trails[j]["end"])]:
                    dist = ((end_a[0] - start_b[0])**2 + (end_a[1] - start_b[1])**2) ** 0.5
                    if dist < 30:  # within 30 pixels
                        gap_pairs += 1
                        break

    print(f"\n  Potential gap pairs (endpoints within 30px): {gap_pairs}")
    if gap_pairs > 10:
        print("  NOTE: Many close endpoints suggest trails broken by text overlaps.")
        print("  Consider increasing gap-fill kernel size in 02_segment_colors.py")
    elif gap_pairs > 0:
        print("  Some gaps detected. Merge step in 03_extract_polylines.py should handle most.")
    else:
        print("  No obvious gaps detected.")


def create_visual_diff(meta: dict, polylines: dict):
    """Create a visual coverage map showing where polylines are vs. empty areas."""
    READABLE_DIR.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(str(IMAGE_PATH))
    if img is None:
        return

    img_w, img_h = meta["width"], meta["height"]
    accepted = polylines["accepted"]

    # Draw coverage heatmap
    coverage_map = np.zeros((img_h, img_w), dtype=np.uint8)
    color_map_bgr = {
        "green": (0, 255, 0),
        "blue": (255, 100, 0),
        "red": (0, 0, 255),
        "black": (200, 200, 200),
    }

    overlay = img.copy()
    for trail in accepted:
        color = color_map_bgr.get(trail["color"], (255, 255, 255))
        pts = np.array(trail["points"], dtype=np.int32)
        if len(pts) < 2:
            continue
        cv2.polylines(overlay, [pts], False, color, 4, cv2.LINE_AA)
        # Mark coverage
        cv2.polylines(coverage_map, [pts], False, 255, 20)

    # Blend
    result = cv2.addWeighted(img, 0.5, overlay, 0.5, 0)

    # Mark uncovered areas in red tint
    uncovered = coverage_map == 0
    # Only in the mountain area (rough mask: not sky, not parking lot)
    mountain_y_start = int(0.08 * img_h)
    mountain_y_end = int(0.85 * img_h)
    mountain_x_start = int(0.02 * img_w)
    mountain_x_end = int(0.98 * img_w)

    scale = 1800 / img_w
    w, h = int(img_w * scale), int(img_h * scale)
    result_small = cv2.resize(result, (w, h))

    path = READABLE_DIR / "validation_coverage.jpg"
    cv2.imwrite(str(path), result_small, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"\n  Saved coverage visualization to {path}")


def print_summary(coverage_pct: float):
    """Print final summary with recommendations."""
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    if coverage_pct < 50:
        print("  1. CRITICAL: Very low coverage. Check HSV thresholds in color_ranges.py")
        print("     Run: python scripts/02_segment_colors.py --tune")
        print("  2. Inspect masks in output/masks/ to see what's being detected")
    elif coverage_pct < 70:
        print("  1. Lower saturation thresholds in color_ranges.py")
        print("  2. Increase gap-fill kernel size in 02_segment_colors.py")
        print("  3. Consider running SAM 2 for missed trails")
    elif coverage_pct < 90:
        print("  1. Good coverage. Use SAM 2 (03b_sam_refine.py) for remaining trails")
        print("  2. Check spatial coverage — some peak areas may need attention")
    else:
        print("  1. Excellent coverage! Proceed to trail identification (Step 4)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--visual", action="store_true", help="Generate visual diff images")
    args = parser.parse_args()

    if not POLYLINES_PATH.exists():
        print("ERROR: Run steps 1-3 first. No extracted_polylines.json found.")
        sys.exit(1)

    meta, polylines = load_data()

    coverage_pct = coverage_analysis(polylines, meta)
    quality_analysis(polylines, meta)
    spatial_coverage(polylines, meta)
    gap_analysis(polylines, meta)

    if args.visual:
        print("\nGenerating visual diff...")
        create_visual_diff(meta, polylines)

    print_summary(coverage_pct)


if __name__ == "__main__":
    main()
