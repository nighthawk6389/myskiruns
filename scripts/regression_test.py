#!/usr/bin/env python3
"""Regression test for trail extraction pipeline.

Saves a snapshot of current metrics. On subsequent runs, compares against
the snapshot and fails if any metric regresses beyond a threshold.

Usage:
    python scripts/regression_test.py --save     # Save current metrics as baseline
    python scripts/regression_test.py --check    # Check against saved baseline
    python scripts/regression_test.py            # Both: check then save if passing
"""

import argparse
import json
import math
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
BASELINE_PATH = OUTPUT_DIR / "regression_baseline.json"
POLYLINES_PATH = OUTPUT_DIR / "extracted_polylines.json"
SYMBOLS_PATH = OUTPUT_DIR / "symbols.json"
META_PATH = OUTPUT_DIR / "image_meta.json"

# Thresholds for regression detection
REGRESSION_THRESHOLDS = {
    "blue_segments_min": 0.85,    # blue can drop at most 15% from baseline
    "green_segments_min": 0.80,
    "black_segments_min": 0.80,
    "total_segments_min": 0.85,
    "blue_mask_coverage_min": 0.80,  # mask pixel count can drop at most 20%
    "total_arc_length_min": 0.85,    # total polyline length can drop at most 15%
}

# Known-good trail presence checks: specific areas that MUST have polylines
REQUIRED_TRAILS = [
    {"name": "Solitude area", "x_pct": (0, 20), "y_pct": (10, 40), "min_blue": 1},
    {"name": "Skye Peak center", "x_pct": (40, 65), "y_pct": (10, 50), "min_blue": 5},
    {"name": "Killington Peak", "x_pct": (60, 85), "y_pct": (5, 55), "min_blue": 3},
    {"name": "Bear Mountain", "x_pct": (80, 100), "y_pct": (10, 65), "min_blue": 1},
    {"name": "Snowdon", "x_pct": (28, 52), "y_pct": (10, 60), "min_blue": 3},
]


def compute_metrics():
    """Compute current pipeline metrics."""
    data = json.loads(POLYLINES_PATH.read_text())
    meta = json.loads(META_PATH.read_text())
    w, h = meta["width"], meta["height"]
    accepted = data["accepted"]

    from collections import Counter
    color_counts = Counter(t["color"] for t in accepted)

    # Compute total arc length
    total_arc = 0
    for t in accepted:
        pts = t["points"]
        for i in range(1, len(pts)):
            dx = pts[i][0] - pts[i-1][0]
            dy = pts[i][1] - pts[i-1][1]
            total_arc += math.sqrt(dx*dx + dy*dy)

    # Check required trail areas
    area_checks = {}
    for req in REQUIRED_TRAILS:
        count = 0
        for t in accepted:
            if t["color"] != "blue":
                continue
            pts = t["points"]
            if not pts:
                continue
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            cx = sum(xs) / len(xs) / w * 100
            cy = sum(ys) / len(ys) / h * 100
            if (req["x_pct"][0] <= cx <= req["x_pct"][1] and
                    req["y_pct"][0] <= cy <= req["y_pct"][1]):
                count += 1
        area_checks[req["name"]] = {
            "blue_count": count,
            "required_min": req["min_blue"],
            "pass": count >= req["min_blue"],
        }

    # Blue mask pixel count (if mask exists)
    import cv2
    blue_mask_pixels = 0
    blue_mask_path = OUTPUT_DIR / "masks" / "blue_mask.png"
    if blue_mask_path.exists():
        import numpy as np
        bm = cv2.imread(str(blue_mask_path), cv2.IMREAD_GRAYSCALE)
        if bm is not None:
            blue_mask_pixels = int(np.count_nonzero(bm))

    # Compute precision using local contrast: does each polyline point sit on
    # a DRAWN LINE (high contrast vs surroundings) or diffuse terrain?
    # Blue/green: saturation contrast (S_trail - S_bg)
    # Black: value contrast (V_bg - V_trail)
    import cv2
    precision_by_color = {}
    img_path = OUTPUT_DIR / "trailmap_300dpi.png"
    if img_path.exists():
        orig_hsv = cv2.cvtColor(cv2.imread(str(img_path)), cv2.COLOR_BGR2HSV)
        ih, iw = orig_hsv.shape[:2]
        for color in ["green", "blue", "black"]:
            high_contrast, total_pts = 0, 0
            for t in accepted:
                if t["color"] != color:
                    continue
                for px, py in t["points"]:
                    total_pts += 1
                    py_i, px_i = int(py), int(px)
                    if not (3 <= px_i < iw - 3 and 3 <= py_i < ih - 3):
                        continue
                    ch = 2 if color == "black" else 1  # V for black, S for others
                    fg = float(orig_hsv[py_i-1:py_i+2, px_i-1:px_i+2, ch].mean())
                    ring = []
                    for adeg in range(0, 360, 45):
                        dx = int(40 * np.cos(np.radians(adeg)))
                        dy = int(40 * np.sin(np.radians(adeg)))
                        bx, by = px_i + dx, py_i + dy
                        if 1 <= bx < iw-1 and 1 <= by < ih-1:
                            ring.append(float(orig_hsv[by-1:by+2, bx-1:bx+2, ch].mean()))
                    if not ring:
                        continue
                    bg = np.mean(ring)
                    if color == "black":
                        c = bg - fg  # darker than surroundings
                    else:
                        c = fg - bg  # more saturated than surroundings
                    if c >= 10:
                        high_contrast += 1
            precision_by_color[color] = round(high_contrast / total_pts * 100, 1) if total_pts > 0 else 0

    # Symbol-based recall: what % of difficulty symbols have a polyline nearby?
    # This is our best proxy for true recall since symbols mark real trail locations.
    # Radius 75px: at 300dpi, 75px = 0.25 inches. On a standard trail map,
    # difficulty symbols are often placed slightly to the side of the trail line,
    # so 0.25" offset is reasonable.
    symbol_recall = {}
    if SYMBOLS_PATH.exists():
        symbols = json.loads(SYMBOLS_PATH.read_text())
        for color in ["green", "blue", "black"]:
            sym_positions = symbols.get(color, [])
            if not sym_positions:
                continue
            matched = 0
            radius = 75  # pixels — symbol should be within 75px of a trail polyline
            color_polylines = [t for t in accepted if t["color"] == color]
            for sx, sy in sym_positions:
                found = False
                for t in color_polylines:
                    for px, py in t["points"]:
                        if abs(px - sx) <= radius and abs(py - sy) <= radius:
                            found = True
                            break
                    if found:
                        break
                if found:
                    matched += 1
            symbol_recall[color] = {
                "matched": matched,
                "total": len(sym_positions),
                "recall_pct": round(matched / len(sym_positions) * 100, 1),
            }

    return {
        "green_segments": color_counts.get("green", 0),
        "blue_segments": color_counts.get("blue", 0),
        "black_segments": color_counts.get("black", 0),
        "total_segments": len(accepted),
        "total_arc_length": round(total_arc, 1),
        "blue_mask_pixels": blue_mask_pixels,
        "area_checks": area_checks,
        "precision": precision_by_color,
        "symbol_recall": symbol_recall,
        "gap_pairs": 0,
        "short_polylines": sum(1 for t in accepted if t["num_points"] <= 3),
    }


def save_baseline(metrics):
    """Save metrics as the regression baseline."""
    BASELINE_PATH.write_text(json.dumps(metrics, indent=2))
    print(f"Saved baseline to {BASELINE_PATH}")
    print(f"  Green: {metrics['green_segments']}, Blue: {metrics['blue_segments']}, "
          f"Black: {metrics['black_segments']}, Total: {metrics['total_segments']}")
    print(f"  Total arc length: {metrics['total_arc_length']:.0f}px")
    print(f"  Blue mask pixels: {metrics['blue_mask_pixels']}")
    for name, check in metrics["area_checks"].items():
        status = "PASS" if check["pass"] else "FAIL"
        print(f"  {name}: {check['blue_count']} blue polylines [{status}]")
    if "precision" in metrics:
        for color, prec in metrics["precision"].items():
            print(f"  {color} precision: {prec:.1f}%")
    if "symbol_recall" in metrics:
        for color, sr in metrics["symbol_recall"].items():
            print(f"  {color} symbol recall: {sr['matched']}/{sr['total']} ({sr['recall_pct']:.1f}%)")


def check_regression(metrics):
    """Check current metrics against baseline. Returns True if passing."""
    if not BASELINE_PATH.exists():
        print("No baseline found. Run with --save first.")
        return True

    baseline = json.loads(BASELINE_PATH.read_text())
    passed = True
    print("Regression check against baseline:")

    # Check segment counts
    for color in ["green", "blue", "black", "total"]:
        key = f"{color}_segments"
        min_key = f"{color}_segments_min"
        current = metrics[key]
        base = baseline[key]
        threshold = REGRESSION_THRESHOLDS.get(min_key, 0.80)
        min_allowed = int(base * threshold)
        status = "PASS" if current >= min_allowed else "FAIL"
        if status == "FAIL":
            passed = False
        print(f"  {color:8s}: {current:3d} (baseline: {base}, min: {min_allowed}) [{status}]")

    # Check arc length
    current_arc = metrics["total_arc_length"]
    base_arc = baseline["total_arc_length"]
    min_arc = base_arc * REGRESSION_THRESHOLDS["total_arc_length_min"]
    arc_status = "PASS" if current_arc >= min_arc else "FAIL"
    if arc_status == "FAIL":
        passed = False
    print(f"  arc_len: {current_arc:.0f} (baseline: {base_arc:.0f}, min: {min_arc:.0f}) [{arc_status}]")

    # Check blue mask coverage
    current_bm = metrics["blue_mask_pixels"]
    base_bm = baseline.get("blue_mask_pixels", 0)
    if base_bm > 0:
        min_bm = int(base_bm * REGRESSION_THRESHOLDS["blue_mask_coverage_min"])
        bm_status = "PASS" if current_bm >= min_bm else "FAIL"
        if bm_status == "FAIL":
            passed = False
        print(f"  blue_px: {current_bm} (baseline: {base_bm}, min: {min_bm}) [{bm_status}]")

    # Check required trail areas
    print("  Required trail areas:")
    for name, check in metrics["area_checks"].items():
        status = "PASS" if check["pass"] else "FAIL"
        if not check["pass"]:
            passed = False
        print(f"    {name}: {check['blue_count']} blue (need >={check['required_min']}) [{status}]")

    # Check precision
    if "precision" in metrics and "precision" in baseline:
        print("  Precision (% polyline points on trail pixels):")
        for color in ["green", "blue", "black"]:
            curr_p = metrics["precision"].get(color, 0)
            base_p = baseline["precision"].get(color, 0)
            min_p = base_p * 0.85  # precision can drop at most 15%
            p_status = "PASS" if curr_p >= min_p else "FAIL"
            if p_status == "FAIL":
                passed = False
            print(f"    {color}: {curr_p:.1f}% (baseline: {base_p:.1f}%, min: {min_p:.1f}%) [{p_status}]")

    # Check symbol-based recall
    if "symbol_recall" in metrics:
        print("  Symbol-based recall (% of difficulty symbols near a polyline):")
        for color in ["green", "blue", "black"]:
            sr = metrics["symbol_recall"].get(color, {})
            if not sr:
                continue
            curr_r = sr["recall_pct"]
            # Check against baseline if available, otherwise use absolute threshold
            base_sr = baseline.get("symbol_recall", {}).get(color, {})
            if base_sr:
                min_r = base_sr["recall_pct"] * 0.85
                r_status = "PASS" if curr_r >= min_r else "FAIL"
                if r_status == "FAIL":
                    passed = False
                print(f"    {color}: {curr_r:.1f}% ({sr['matched']}/{sr['total']}) "
                      f"(baseline: {base_sr['recall_pct']:.1f}%, min: {min_r:.1f}%) [{r_status}]")
            else:
                print(f"    {color}: {curr_r:.1f}% ({sr['matched']}/{sr['total']})")

    if passed:
        print("\nAll regression checks PASSED.")
    else:
        print("\nREGRESSION DETECTED! Some checks failed.")

    return passed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", action="store_true", help="Save current as baseline")
    parser.add_argument("--check", action="store_true", help="Check against baseline")
    args = parser.parse_args()

    if not POLYLINES_PATH.exists():
        print("ERROR: No extracted_polylines.json. Run the pipeline first.")
        sys.exit(1)

    metrics = compute_metrics()

    if args.check and not args.save:
        passed = check_regression(metrics)
        sys.exit(0 if passed else 1)

    if args.save and not args.check:
        save_baseline(metrics)
        return

    # Default: check then save if passing
    if BASELINE_PATH.exists():
        passed = check_regression(metrics)
        if passed:
            print("\nUpdating baseline...")
            save_baseline(metrics)
        else:
            print("\nBaseline NOT updated due to regression.")
            sys.exit(1)
    else:
        print("No baseline exists. Saving current metrics as baseline.")
        save_baseline(metrics)


if __name__ == "__main__":
    main()
