#!/usr/bin/env python3
"""POC: gauge whether OCR on this map can recover trail names with enough
accuracy to be worth wiring into the pipeline.

Reads scripts/output/text_regions.json (per-character bboxes from
02_segment_colors.py), groups them into word clusters, crops the original
trail map at each cluster, runs easyocr, and fuzzy-matches each result
against the canonical trail-name list.

Reports:
- N clusters tested
- N producing OCR text at all
- N where OCR text fuzzy-matches a real trail name (>= match threshold)
- 10 example matches with confidence

Decision rule (per the plan): if 6+ of 10 hand-picked test cases yield
fuzzy match >= 0.7, proceed with C.2/C.3. Here we widen the test set to
the largest 30 clusters and report the success rate so the user can decide.
"""

import argparse
import sys
from difflib import SequenceMatcher
from pathlib import Path

import cv2
import json
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from utils.trail_catalog import all_trails  # noqa: E402

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
IMAGE_PATH = OUTPUT_DIR / "trailmap_300dpi.png"
TEXT_REGIONS_PATH = OUTPUT_DIR / "text_regions.json"
POC_DUMP_DIR = OUTPUT_DIR / "ocr_poc"

MATCH_THRESHOLD = 0.7  # fuzzy ratio needed to count as "matched"


def cluster_text_regions(regions: list[dict],
                         dilate: int = 12) -> list[dict]:
    """Group character-level bboxes into word-level clusters.

    Builds a binary canvas of dilated bboxes, runs connected-components,
    and returns one cluster per CC with its bounding rectangle and
    contained character count.
    """
    if not regions:
        return []
    max_x = max(r["x"] + r["w"] for r in regions) + 2 * dilate
    max_y = max(r["y"] + r["h"] for r in regions) + 2 * dilate
    canvas = np.zeros((max_y, max_x), dtype=np.uint8)
    for r in regions:
        cv2.rectangle(canvas,
                      (r["x"] - dilate // 2, r["y"] - dilate // 2),
                      (r["x"] + r["w"] + dilate // 2,
                       r["y"] + r["h"] + dilate // 2),
                      255, -1)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(canvas)

    # Map each region to its cluster label
    region_label = []
    for r in regions:
        cy = r["y"] + r["h"] // 2
        cx = r["x"] + r["w"] // 2
        region_label.append(int(labels[cy, cx]))

    clusters = []
    for cc_id in range(1, num_labels):
        member_count = sum(1 for L in region_label if L == cc_id)
        if member_count < 2:
            continue  # singleton — almost certainly not a word
        x = int(stats[cc_id, cv2.CC_STAT_LEFT])
        y = int(stats[cc_id, cv2.CC_STAT_TOP])
        w = int(stats[cc_id, cv2.CC_STAT_WIDTH])
        h = int(stats[cc_id, cv2.CC_STAT_HEIGHT])
        # Filter unrealistic clusters (huge or tiny aspect ratios)
        if w > 500 or h > 80 or w < 15:
            continue
        clusters.append({
            "x": x, "y": y, "w": w, "h": h,
            "char_count": member_count,
        })

    # Sort largest-first so we test "biggest, most likely real label" cases
    clusters.sort(key=lambda c: -c["char_count"])
    return clusters


import re


def _normalize(text: str) -> str:
    """Lowercase, drop apostrophes, collapse non-alpha to spaces."""
    return re.sub(r"[^a-z]+", " ", text.lower().replace("'", "")).strip()


def _word_seqs(text: str) -> list[str]:
    """All contiguous 1- to 3-word sub-strings of `text` (for substring matching)."""
    words = _normalize(text).split()
    seqs = []
    for n in (1, 2, 3):
        for i in range(0, len(words) - n + 1):
            seqs.append(" ".join(words[i: i + n]))
    return seqs


def fuzzy_match_trail(text: str, trails: list[dict]) -> tuple[dict | None, float]:
    """Return best (trail, ratio) or (None, ratio) if below threshold.

    Tries every contiguous word sub-sequence of the OCR text against every
    trail's normalized name. This catches embedded matches like
    "EXPRESS C SKYEBURST" -> "Skyeburst" or "HBROOK" -> "Northbrook".
    """
    if not text:
        return None, 0.0
    seqs = _word_seqs(text)
    if not seqs:
        return None, 0.0
    best = None
    best_ratio = 0.0
    for trail in trails:
        norm_name = _normalize(trail["name"])
        for seq in seqs:
            ratio = SequenceMatcher(None, seq, norm_name).ratio()
            # Bonus: if either fully contains the other, treat as strong match
            if norm_name and (seq.find(norm_name) >= 0 or norm_name.find(seq) >= 0):
                ratio = max(ratio, 0.85)
            if ratio > best_ratio:
                best_ratio = ratio
                best = trail
    return (best, best_ratio) if best_ratio >= MATCH_THRESHOLD else (None, best_ratio)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-test", type=int, default=30,
                        help="Number of clusters to test")
    parser.add_argument("--cluster-size", choices=["large", "trail-like", "all"],
                        default="trail-like",
                        help="'large' = biggest clusters (mostly buildings), "
                             "'trail-like' = mid-sized 4-12 char (likely trail names), "
                             "'all' = no filtering")
    parser.add_argument("--dump-crops", action="store_true",
                        help="Save each cropped cluster to output/ocr_poc/")
    parser.add_argument("--paragraph", action="store_true",
                        help="Use easyocr's paragraph mode (joins chars per line)")
    args = parser.parse_args()

    if not TEXT_REGIONS_PATH.exists():
        print(f"ERROR: {TEXT_REGIONS_PATH} not found. Run 02_segment_colors.py first.")
        sys.exit(1)
    if not IMAGE_PATH.exists():
        print(f"ERROR: {IMAGE_PATH} not found.")
        sys.exit(1)

    print("Loading easyocr (this can take ~30s on first run, downloads weights ~75 MB)...")
    import easyocr
    reader = easyocr.Reader(["en"], gpu=False, verbose=False)

    print("Loading text regions and image...")
    regions = json.loads(TEXT_REGIONS_PATH.read_text())
    image = cv2.imread(str(IMAGE_PATH))
    print(f"  {len(regions)} character regions, image {image.shape[1]}x{image.shape[0]}")

    print("Clustering character bboxes into word groups...")
    clusters = cluster_text_regions(regions)
    print(f"  -> {len(clusters)} word-sized clusters (singletons dropped)")

    if args.cluster_size == "large":
        test_set = clusters[: args.n_test]
    elif args.cluster_size == "trail-like":
        # Mid-sized clusters more likely to be trail names than building/peak labels.
        # Trail names on this map run ~4-12 characters; bigger clusters are
        # building/road labels, smaller are noise.
        candidates = [c for c in clusters if 4 <= c["char_count"] <= 12]
        test_set = candidates[: args.n_test]
    else:
        test_set = clusters[: args.n_test]
    trails = all_trails()
    print(f"\nTesting top {len(test_set)} clusters by character count.\n")

    if args.dump_crops:
        POC_DUMP_DIR.mkdir(parents=True, exist_ok=True)

    matched = 0
    any_text = 0
    sample_rows = []
    pad = 6
    for idx, c in enumerate(test_set):
        x0 = max(0, c["x"] - pad)
        y0 = max(0, c["y"] - pad)
        x1 = min(image.shape[1], c["x"] + c["w"] + pad)
        y1 = min(image.shape[0], c["y"] + c["h"] + pad)
        crop = image[y0:y1, x0:x1]
        if crop.size == 0:
            continue

        # Upscale small crops 2x — OCR engines do better with larger glyphs
        if crop.shape[0] < 30 or crop.shape[1] < 60:
            crop = cv2.resize(crop, None, fx=2.5, fy=2.5,
                              interpolation=cv2.INTER_CUBIC)

        results = reader.readtext(
            crop,
            paragraph=args.paragraph,
            detail=1,
            text_threshold=0.5,
            low_text=0.3,
        )

        if not results:
            text, ocr_conf = "", 0.0
        else:
            # Concatenate detected pieces in reading order
            results.sort(key=lambda r: r[0][0][0])  # sort by x of top-left
            if args.paragraph:
                # paragraph mode returns 2-tuples (bbox, text)
                text = " ".join(str(r[1]) for r in results)
                ocr_conf = 1.0
            else:
                text = " ".join(str(r[1]) for r in results)
                ocr_conf = float(np.mean([r[2] for r in results]))

        if text.strip():
            any_text += 1

        trail, ratio = fuzzy_match_trail(text, trails)
        if trail is not None:
            matched += 1

        sample_rows.append({
            "idx": idx,
            "bbox": (c["x"], c["y"], c["w"], c["h"]),
            "char_count": c["char_count"],
            "ocr_text": text,
            "ocr_conf": ocr_conf,
            "matched_trail_id": trail["id"] if trail else "",
            "match_ratio": ratio,
        })

        if args.dump_crops:
            tag = trail["id"] if trail else (text or "no_text").replace(" ", "_")[:30]
            cv2.imwrite(str(POC_DUMP_DIR / f"{idx:02d}_{tag}.png"), crop)

    print(f"{'idx':>3}  {'chars':>5}  {'ocr_text':<28}  {'conf':>5}  "
          f"{'matched':<25}  {'ratio':>6}")
    print("  " + "-" * 80)
    for r in sample_rows:
        text_disp = (r["ocr_text"] or "<no text>")[:28]
        print(f"{r['idx']:>3}  {r['char_count']:>5}  {text_disp:<28}  "
              f"{r['ocr_conf']:>5.2f}  {r['matched_trail_id']:<25}  {r['match_ratio']:>6.2f}")

    print()
    print(f"Tested:                {len(sample_rows)}")
    print(f"Got OCR text at all:   {any_text} ({100 * any_text / max(len(sample_rows), 1):.0f}%)")
    print(f"Fuzzy-matched a trail: {matched} ({100 * matched / max(len(sample_rows), 1):.0f}%)")
    print()
    if matched / max(len(sample_rows), 1) >= 0.5:
        print("=> POC PASSES (>=50% match rate). Proceed with C.2 / C.3.")
    elif matched / max(len(sample_rows), 1) >= 0.3:
        print("=> POC MARGINAL (30-50%). Try --paragraph and --dump-crops, "
              "consider per-cluster pre-rotation, or paddleocr.")
    else:
        print("=> POC FAILS (<30%). Reassess approach before building C.2/C.3.")


if __name__ == "__main__":
    main()
