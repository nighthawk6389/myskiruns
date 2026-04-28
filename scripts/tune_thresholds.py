#!/usr/bin/env python3
"""Sweep classification thresholds against the existing score_logs baseline.

Reads scripts/output/score_logs.json (which contains per-heuristic scores for
every connected component) and finds (confident, probable, uncertain) threshold
triples that best preserve the *current* accept set after dropping dead/broken
heuristics.

The "baseline" is whatever the current pipeline classifies as confident or
probable using its existing total + classification fields. The "new total" is
recomputed by summing only the heuristics actually exposed in
scripts/utils/heuristics.py::score_component (anything else in the log is
treated as a phased-out heuristic and excluded).

Usage:
    python scripts/tune_thresholds.py
    python scripts/tune_thresholds.py --grid wide   # sweep more candidates
    python scripts/tune_thresholds.py --no-overlays # skip side-by-side render
"""

import argparse
import json
import sys
from itertools import product
from pathlib import Path

import cv2
import numpy as np

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
SCORE_LOGS = OUTPUT_DIR / "score_logs.json"
IMAGE_PATH = OUTPUT_DIR / "trailmap_300dpi.png"
TUNE_DIR = OUTPUT_DIR / "tune"

# These are the heuristics that survive the 02-segment-colors refactor.
# Anything else in score_logs (in_mountain, proximity, aspect_ratio, ...) is
# treated as removed.
ACTIVE_HEURISTICS = {
    "arc_length",
    "sinuosity",
    "smooth_curvature",
    "downhill",
    "stroke_width",
    "no_holes",
}

DEFAULT_GRID = {
    "confident": [3, 4, 5, 6],
    "probable": [2, 3, 4, 5],
    "uncertain": [1, 2, 3, 4],
}

WIDE_GRID = {
    "confident": [2, 3, 4, 5, 6],
    "probable": [1, 2, 3, 4, 5],
    "uncertain": [0, 1, 2, 3, 4],
}

# Same color codes used by 06_visualize.py
COLOR_BGR = {
    "green": (0, 200, 0),
    "blue": (255, 100, 0),
    "black": (32, 32, 32),
}


def load_components() -> list[dict]:
    """Load components from score_logs and recompute new_total over active heuristics."""
    raw = json.loads(SCORE_LOGS.read_text())
    components = []
    for color, entries in raw.items():
        for entry in entries:
            scores = entry["scores"]
            present_active = ACTIVE_HEURISTICS & set(scores.keys())
            new_total = sum(scores[h] for h in present_active)
            components.append({
                "id": entry["id"],
                "color": color,
                "old_total": entry["total"],
                "old_classification": entry["classification"],
                "new_total": new_total,
                "active_heuristics_present": sorted(present_active),
                "bbox": entry.get("bbox", {}),
            })
    return components


def baseline_accept_ids(components: list[dict]) -> set[str]:
    return {c["id"] for c in components
            if c["old_classification"] in ("confident", "probable")}


def evaluate_triple(components: list[dict], baseline: set[str],
                    confident: int, probable: int, uncertain: int) -> dict:
    """Apply a (confident, probable, uncertain) triple and score against baseline."""
    new_accept = set()
    for c in components:
        t = c["new_total"]
        if t >= probable:  # confident OR probable both pass into accept
            new_accept.add(c["id"])

    intersection = new_accept & baseline
    precision = len(intersection) / len(new_accept) if new_accept else 0.0
    recall = len(intersection) / len(baseline) if baseline else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) > 0 else 0.0)
    drift = len(new_accept) - len(baseline)
    added = new_accept - baseline
    dropped = baseline - new_accept
    return {
        "confident": confident,
        "probable": probable,
        "uncertain": uncertain,
        "n_accept": len(new_accept),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "drift": drift,
        "added": sorted(added),
        "dropped": sorted(dropped),
    }


def sweep(components: list[dict], grid: dict[str, list[int]]) -> list[dict]:
    baseline = baseline_accept_ids(components)
    results = []
    seen = set()
    for c, p, u in product(grid["confident"], grid["probable"], grid["uncertain"]):
        if not (c > p > u):
            continue
        key = (c, p, u)
        if key in seen:
            continue
        seen.add(key)
        results.append(evaluate_triple(components, baseline, c, p, u))
    return sorted(results, key=lambda r: (-r["f1"], abs(r["drift"])))


def render_overlay(image: np.ndarray, components: list[dict],
                   added: set[str], dropped: set[str],
                   path: Path) -> None:
    """Render an annotated image highlighting components added/dropped vs baseline.

    Yellow = added (admitted by new thresholds, not by old).
    Red    = dropped (admitted by old, not by new).
    Faint  = unchanged (still accepted under both).
    """
    canvas = image.copy()
    overlay = canvas.copy()

    by_id = {c["id"]: c for c in components}
    baseline = {cid for cid, c in by_id.items()
                if c["old_classification"] in ("confident", "probable")}

    for cid, c in by_id.items():
        bbox = c.get("bbox") or {}
        if not bbox:
            continue
        x, y, w, h = bbox.get("x", 0), bbox.get("y", 0), bbox.get("w", 0), bbox.get("h", 0)
        if w <= 0 or h <= 0:
            continue
        if cid in added:
            color = (0, 255, 255)  # yellow
            thick = 3
        elif cid in dropped:
            color = (0, 0, 255)    # red
            thick = 3
        elif cid in baseline:
            color = COLOR_BGR.get(c["color"], (180, 180, 180))
            thick = 1
        else:
            continue
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, thick)

    blended = cv2.addWeighted(overlay, 0.85, canvas, 0.15, 0)

    # Legend at top-left
    legend_y = 40
    for label, color in [
        (f"Added ({len(added)})", (0, 255, 255)),
        (f"Dropped ({len(dropped)})", (0, 0, 255)),
        ("Unchanged (baseline)", (200, 200, 200)),
    ]:
        cv2.rectangle(blended, (20, legend_y - 20), (50, legend_y), color, -1)
        cv2.putText(blended, label, (60, legend_y - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        legend_y += 32

    cv2.imwrite(str(path), blended)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid", choices=["default", "wide"], default="default")
    parser.add_argument("--no-overlays", action="store_true")
    parser.add_argument("--top", type=int, default=8,
                        help="Number of triples to print")
    parser.add_argument("--render-top", type=int, default=3,
                        help="Number of overlays to render")
    args = parser.parse_args()

    if not SCORE_LOGS.exists():
        print(f"ERROR: {SCORE_LOGS} not found. Run scripts/03_extract_polylines.py first.")
        sys.exit(1)

    components = load_components()
    baseline = baseline_accept_ids(components)
    grid = WIDE_GRID if args.grid == "wide" else DEFAULT_GRID

    # Tell the user what we treat as the active heuristic set
    sample = next(iter(components), {})
    present = sample.get("active_heuristics_present", [])
    print(f"Loaded {len(components)} components from {SCORE_LOGS.name}")
    print(f"Active heuristics in this sweep: {present}")
    print(f"Baseline accepted (current pipeline): {len(baseline)}")
    print(f"Sweeping {len(grid['confident']) * len(grid['probable']) * len(grid['uncertain'])} "
          f"raw triples (filtered to those with confident > probable > uncertain)\n")

    results = sweep(components, grid)
    if not results:
        print("ERROR: No valid triples in the sweep grid.")
        sys.exit(1)

    print(f"{'rank':>4}  {'cnf':>3} {'prb':>3} {'unc':>3}  {'n':>4}  "
          f"{'prec':>6} {'recall':>6} {'F1':>6}  {'drift':>6}")
    print("  " + "-" * 60)
    for rank, r in enumerate(results[:args.top], 1):
        print(f"{rank:>4}  {r['confident']:>3} {r['probable']:>3} {r['uncertain']:>3}  "
              f"{r['n_accept']:>4}  "
              f"{r['precision']:>6.3f} {r['recall']:>6.3f} {r['f1']:>6.3f}  "
              f"{r['drift']:>+6d}")

    print("\nTop pick details:")
    for rank, r in enumerate(results[:3], 1):
        print(f"\n  #{rank}: confident={r['confident']} probable={r['probable']} "
              f"uncertain={r['uncertain']}")
        print(f"     n_accept={r['n_accept']}  drift={r['drift']:+d}  F1={r['f1']:.3f}")
        if r["added"]:
            print(f"     ADDED ({len(r['added'])}): {', '.join(r['added'][:8])}"
                  f"{'...' if len(r['added']) > 8 else ''}")
        if r["dropped"]:
            print(f"     DROPPED ({len(r['dropped'])}): {', '.join(r['dropped'][:8])}"
                  f"{'...' if len(r['dropped']) > 8 else ''}")

    if not args.no_overlays:
        if not IMAGE_PATH.exists():
            print(f"\n(skip overlays: {IMAGE_PATH.name} not found)")
        else:
            TUNE_DIR.mkdir(parents=True, exist_ok=True)
            image = cv2.imread(str(IMAGE_PATH))
            print(f"\nRendering top-{args.render_top} overlay diffs to {TUNE_DIR}/")
            for rank, r in enumerate(results[:args.render_top], 1):
                tag = f"c{r['confident']}p{r['probable']}u{r['uncertain']}"
                out = TUNE_DIR / f"overlay_rank{rank}_{tag}.jpg"
                render_overlay(image, components, set(r["added"]),
                               set(r["dropped"]), out)
                print(f"  rank {rank}: {out.name}")

    print("\nNext step: pick a triple, then update CONFIDENT_THRESHOLD / "
          "PROBABLE_THRESHOLD / UNCERTAIN_THRESHOLD in scripts/utils/heuristics.py.")


if __name__ == "__main__":
    main()
