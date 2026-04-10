#!/usr/bin/env python3
"""Step 3b: Automated SAM 2 refinement of CV-extracted trail polylines.

Uses the CV pipeline's polylines (from 03_extract_polylines.py) as prompt
points for SAM 2, which produces clean, continuous trail masks. The SAM masks
are then skeletonized back into refined polylines.

Why this helps:
- SAM understands object boundaries → trails separated from background
- SAM bridges text gaps → continuous trails instead of fragments
- SAM ignores color → works for faded/desaturated trail sections
- SAM masks are cleaner → fewer false positives from terrain noise

Pipeline:
1. Load CV polylines as prompt candidates
2. For each polyline, sample points along it as SAM positive prompts
3. Add negative prompts from nearby non-trail areas
4. Run SAM 2 prediction → get a clean mask per trail
5. Skeletonize each mask → refined polyline
6. Filter and merge refined polylines
7. Output replaces or augments the CV polylines

Requirements:
    pip install sam2 torch torchvision

Usage:
    python 03b_sam_refine.py              # Refine all CV polylines
    python 03b_sam_refine.py --color blue # Refine only blue trails
    python 03b_sam_refine.py --interactive # Fall back to interactive mode
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
REFINED_PATH = OUTPUT_DIR / "refined_polylines.json"
MASKS_DIR = OUTPUT_DIR / "masks"

# SAM 2 model config — tiny is fast enough for CPU
SAM2_CONFIG = "sam2_hiera_t"
SAM2_CHECKPOINT = "sam2_hiera_tiny.pt"

# How many prompt points to sample per polyline
POINTS_PER_TRAIL = 8
# Distance for negative prompt points (pixels away from trail)
NEGATIVE_OFFSET = 60
# Minimum mask area to accept (filters out failed predictions)
MIN_MASK_AREA = 200
# Maximum mask area (filters out masks that capture too much)
MAX_MASK_AREA_RATIO = 0.02  # max 2% of image


def load_cv_polylines():
    """Load polylines from the CV pipeline."""
    if not POLYLINES_PATH.exists():
        print("ERROR: No extracted_polylines.json. Run 03_extract_polylines.py first.")
        sys.exit(1)
    data = json.loads(POLYLINES_PATH.read_text())
    return data


def sample_prompt_points(polyline_pts, num_points=POINTS_PER_TRAIL):
    """Sample evenly-spaced points along a polyline for SAM prompts.

    Returns array of (x, y) points.
    """
    if len(polyline_pts) <= num_points:
        return np.array(polyline_pts, dtype=np.float32)

    # Sample evenly by arc length
    indices = np.linspace(0, len(polyline_pts) - 1, num_points, dtype=int)
    return np.array([polyline_pts[i] for i in indices], dtype=np.float32)


def generate_negative_points(positive_pts, img_h, img_w, offset=NEGATIVE_OFFSET):
    """Generate negative prompt points perpendicular to the trail.

    Places points offset pixels to each side of the trail midpoint,
    perpendicular to the trail direction. This tells SAM "this area
    is NOT part of the trail."
    """
    negatives = []
    if len(positive_pts) < 2:
        return np.empty((0, 2), dtype=np.float32)

    # Sample a few negative points along the trail
    step = max(1, len(positive_pts) // 3)
    for i in range(1, len(positive_pts) - 1, step):
        px, py = positive_pts[i]
        # Get trail direction from neighbors
        prev = positive_pts[max(0, i - 1)]
        nxt = positive_pts[min(len(positive_pts) - 1, i + 1)]
        dx = nxt[0] - prev[0]
        dy = nxt[1] - prev[1]
        length = max(np.sqrt(dx**2 + dy**2), 1)
        # Perpendicular direction
        perp_x = -dy / length * offset
        perp_y = dx / length * offset
        # Add points on both sides
        for sign in [1, -1]:
            nx = int(px + sign * perp_x)
            ny = int(py + sign * perp_y)
            if 0 <= nx < img_w and 0 <= ny < img_h:
                negatives.append([nx, ny])

    return np.array(negatives, dtype=np.float32) if negatives else np.empty((0, 2), dtype=np.float32)


def mask_to_polyline(mask):
    """Convert a binary mask to an ordered polyline via skeletonization.

    Returns list of [x, y] points, or empty list if mask is too small.
    """
    from skimage.morphology import skeletonize

    skeleton = skeletonize(mask > 0).astype(np.uint8) * 255
    if np.count_nonzero(skeleton) < 3:
        return []

    # Find connected components of skeleton
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(skeleton)
    if num_labels < 2:
        return []

    # Take the largest skeleton component
    largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    skel_mask = (labels == largest).astype(np.uint8) * 255

    # Order skeleton points by tracing
    ys, xs = np.where(skel_mask > 0)
    if len(ys) < 3:
        return []

    # Simple ordering: start from the topmost point and trace via nearest-neighbor
    points = list(zip(xs.tolist(), ys.tolist()))
    ordered = [points.pop(np.argmin([p[1] for p in points]))]  # start from top

    while points:
        last = ordered[-1]
        dists = [(p[0] - last[0])**2 + (p[1] - last[1])**2 for p in points]
        nearest_idx = np.argmin(dists)
        if dists[nearest_idx] > 100**2:  # gap too large, stop
            break
        ordered.append(points.pop(nearest_idx))

    if len(ordered) < 3:
        return []

    # Simplify with Douglas-Peucker
    pts_array = np.array(ordered, dtype=np.float32).reshape(-1, 1, 2)
    simplified = cv2.approxPolyDP(pts_array, 2.0, closed=False)
    return [[int(p[0][0]), int(p[0][1])] for p in simplified]


def refine_polyline_with_sam(predictor, trail, img_h, img_w):
    """Refine a single polyline using SAM 2.

    Args:
        predictor: SAM2ImagePredictor with image already set
        trail: dict with 'points' (list of [x,y]) and 'color'
        img_h, img_w: image dimensions

    Returns:
        Refined trail dict, or None if SAM fails
    """
    pts = trail["points"]
    if len(pts) < 2:
        return None

    # Sample positive prompt points along the polyline
    pos_points = sample_prompt_points(pts)

    # Generate negative points perpendicular to trail
    neg_points = generate_negative_points(pts, img_h, img_w)

    # Combine prompts
    if len(neg_points) > 0:
        all_points = np.vstack([pos_points, neg_points])
        labels = np.array([1] * len(pos_points) + [0] * len(neg_points))
    else:
        all_points = pos_points
        labels = np.ones(len(pos_points), dtype=int)

    # Run SAM prediction
    masks, scores, _ = predictor.predict(
        point_coords=all_points,
        point_labels=labels,
        multimask_output=True,
    )

    # Select best mask
    best_idx = np.argmax(scores)
    mask = masks[best_idx]
    score = scores[best_idx]
    area = np.count_nonzero(mask)

    # Validate mask
    max_area = int(img_h * img_w * MAX_MASK_AREA_RATIO)
    if area < MIN_MASK_AREA:
        return None
    if area > max_area:
        # Mask too large — SAM captured the whole mountain
        # Try with more negative points or single-mask mode
        masks2, scores2, _ = predictor.predict(
            point_coords=all_points,
            point_labels=labels,
            multimask_output=False,
        )
        mask = masks2[0]
        score = scores2[0]
        area = np.count_nonzero(mask)
        if area > max_area or area < MIN_MASK_AREA:
            return None

    # Convert mask to polyline
    refined_pts = mask_to_polyline(mask)
    if len(refined_pts) < 3:
        return None

    return {
        "id": trail["id"] + "_sam",
        "color": trail["color"],
        "points": refined_pts,
        "num_points": len(refined_pts),
        "score": 8,  # high confidence — SAM-refined
        "classification": "sam_refined",
        "sam_score": float(score),
        "sam_mask_area": area,
        "original_id": trail["id"],
    }


def refine_all(predictor, polylines_data, colors=None):
    """Refine all polylines (or specific colors) with SAM 2.

    Args:
        predictor: SAM2ImagePredictor with image set
        polylines_data: dict from extracted_polylines.json
        colors: list of colors to refine, or None for all

    Returns:
        List of refined trail dicts
    """
    accepted = polylines_data["accepted"]
    img_w = polylines_data["image_width"]
    img_h = polylines_data["image_height"]

    if colors:
        candidates = [t for t in accepted if t["color"] in colors]
    else:
        candidates = accepted

    print(f"\nRefining {len(candidates)} polylines with SAM 2...")
    refined = []
    failed = 0

    for i, trail in enumerate(candidates):
        result = refine_polyline_with_sam(predictor, trail, img_h, img_w)
        if result:
            refined.append(result)
            status = f"OK ({result['num_points']} pts, score={result['sam_score']:.2f})"
        else:
            failed += 1
            status = "FAILED"

        if (i + 1) % 10 == 0 or i == len(candidates) - 1:
            print(f"  [{i+1}/{len(candidates)}] {trail['id']}: {status}")

    print(f"\nRefined: {len(refined)}, Failed: {failed}")
    return refined


def main():
    parser = argparse.ArgumentParser(description="SAM 2 automated trail refinement")
    parser.add_argument("--color", type=str, help="Only refine this color (green/blue/black)")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode (click to prompt)")
    parser.add_argument("--checkpoint", type=str, default=SAM2_CHECKPOINT,
                        help=f"Path to SAM 2 checkpoint (default: {SAM2_CHECKPOINT})")
    args = parser.parse_args()

    if not IMAGE_PATH.exists():
        print("ERROR: Run 01_convert_pdf.py first.")
        sys.exit(1)

    # Check SAM 2 availability
    try:
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor
    except ImportError:
        print("ERROR: SAM 2 not installed. Install with:")
        print("  pip install sam2 torch torchvision")
        sys.exit(1)

    # Load image
    print("Loading image...")
    img = cv2.imread(str(IMAGE_PATH))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print(f"  {img.shape[1]}x{img.shape[0]}")

    # Load CV polylines
    polylines_data = load_cv_polylines()
    print(f"Loaded {len(polylines_data['accepted'])} CV polylines")

    # Load SAM 2 model
    print(f"\nLoading SAM 2 ({SAM2_CONFIG})...")
    # Search for checkpoint in common locations
    ckpt_paths = [
        args.checkpoint,
        SCRIPT_DIR / args.checkpoint,
        Path.home() / ".cache" / "torch" / "hub" / "checkpoints" / args.checkpoint,
    ]
    ckpt_path = None
    for p in ckpt_paths:
        if Path(p).exists():
            ckpt_path = str(p)
            break

    if ckpt_path is None:
        print(f"ERROR: Checkpoint not found. Searched:")
        for p in ckpt_paths:
            print(f"  {p}")
        print(f"\nDownload from: https://dl.fbaipublicfiles.com/segment_anything_2/072824/{args.checkpoint}")
        sys.exit(1)

    print(f"  Using checkpoint: {ckpt_path}")
    sam2 = build_sam2(SAM2_CONFIG, ckpt_path)
    predictor = SAM2ImagePredictor(sam2)

    print("Computing image embedding...")
    predictor.set_image(img_rgb)
    print("  Embedding ready!")

    # Refine
    colors = [args.color] if args.color else None
    refined = refine_all(predictor, polylines_data, colors=colors)

    # Save refined polylines
    output = {
        "image_width": polylines_data["image_width"],
        "image_height": polylines_data["image_height"],
        "accepted": refined,
        "uncertain": [],
        "source": "sam2_refined",
        "original_count": len(polylines_data["accepted"]),
        "refined_count": len(refined),
    }

    REFINED_PATH.write_text(json.dumps(output, indent=2))
    print(f"\nSaved {len(refined)} refined polylines to {REFINED_PATH}")

    # Generate comparison overlay
    print("\nGenerating comparison overlay...")
    overlay = img.copy()
    # Draw original in thin gray
    for t in polylines_data["accepted"]:
        pts = [(int(p[0]), int(p[1])) for p in t["points"]]
        for j in range(1, len(pts)):
            cv2.line(overlay, pts[j-1], pts[j], (128, 128, 128), 1)
    # Draw refined in color
    color_bgr = {"green": (0, 200, 0), "blue": (255, 128, 0), "black": (80, 80, 80)}
    for t in refined:
        color = color_bgr.get(t["color"], (0, 255, 255))
        pts = [(int(p[0]), int(p[1])) for p in t["points"]]
        for j in range(1, len(pts)):
            cv2.line(overlay, pts[j-1], pts[j], color, 3)

    overlay_path = OUTPUT_DIR / "overlay_sam_refined.jpg"
    cv2.imwrite(str(overlay_path), overlay)
    print(f"Saved comparison overlay to {overlay_path}")


if __name__ == "__main__":
    main()
