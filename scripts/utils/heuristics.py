"""Geometric heuristic scoring for trail vs. non-trail classification.

Each heuristic contributes +1 to a confidence score (0-6 range).
Classification thresholds are exposed as module constants below so they can
be tuned via scripts/tune_thresholds.py.
"""

import math

import cv2
import numpy as np
from skimage.morphology import skeletonize


# Classification thresholds. Tune via scripts/tune_thresholds.py.
# These values were picked from a sweep against score_logs.json: probable=3
# exactly preserves the pre-refactor accept set (F1=1.000, drift=0). The 5/3/1
# spacing mirrors the original 7/5/3 (2-point gaps between tiers).
CONFIDENT_THRESHOLD = 5  # >= this score => "confident"
PROBABLE_THRESHOLD = 3   # >= this score => "probable" (this is the accept cutoff)
UNCERTAIN_THRESHOLD = 1  # >= this score => "uncertain"; below => "reject"


def compute_skeleton(mask_component: np.ndarray) -> np.ndarray:
    """Skeletonize a single connected component mask to 1px-wide lines."""
    binary = (mask_component > 0).astype(bool)
    skeleton = skeletonize(binary)
    return (skeleton.astype(np.uint8) * 255)


def skeleton_arc_length(skeleton: np.ndarray) -> float:
    """Count the number of white pixels in the skeleton (approximate arc length)."""
    return float(np.count_nonzero(skeleton))


def skeleton_endpoints_and_junctions(skeleton: np.ndarray):
    """Find endpoints (1 neighbor) and junctions (3+ neighbors) on a skeleton.

    Returns: (endpoints, junctions) as lists of (y, x) tuples.
    """
    skel = (skeleton > 0).astype(np.uint8)
    # Count neighbors using convolution (8-connectivity)
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.uint8)
    neighbors = cv2.filter2D(skel, -1, kernel)
    neighbors = neighbors * skel  # only count for skeleton pixels

    endpoint_mask = (neighbors == 1) & (skel > 0)
    junction_mask = (neighbors >= 3) & (skel > 0)

    endpoints = list(zip(*np.where(endpoint_mask)))
    junctions = list(zip(*np.where(junction_mask)))

    return endpoints, junctions


def ordered_skeleton_points(skeleton: np.ndarray, endpoints: list) -> list:
    """Walk the skeleton from an endpoint, recording ordered points.

    Returns list of (y, x) points in order along the skeleton.
    """
    if not endpoints:
        # No endpoints — might be a loop; find any skeleton pixel
        ys, xs = np.where(skeleton > 0)
        if len(ys) == 0:
            return []
        start = (ys[0], xs[0])
    else:
        start = endpoints[0]

    skel = (skeleton > 0).astype(np.uint8)
    visited = np.zeros_like(skel, dtype=bool)
    points = [start]
    visited[start[0], start[1]] = True

    current = start
    while True:
        y, x = current
        # Check 8-connected neighbors
        found_next = False
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dy == 0 and dx == 0:
                    continue
                ny, nx = y + dy, x + dx
                if (0 <= ny < skel.shape[0] and 0 <= nx < skel.shape[1]
                        and skel[ny, nx] > 0 and not visited[ny, nx]):
                    visited[ny, nx] = True
                    current = (ny, nx)
                    points.append(current)
                    found_next = True
                    break
            if found_next:
                break
        if not found_next:
            break

    return points


def compute_sinuosity(points: list) -> float:
    """Sinuosity = arc_length / straight_line_distance.

    Returns 1.0 for perfectly straight, >1.0 for curved.
    """
    if len(points) < 2:
        return 1.0

    # Arc length (sum of consecutive distances)
    arc_length = 0.0
    for i in range(1, len(points)):
        dy = points[i][0] - points[i - 1][0]
        dx = points[i][1] - points[i - 1][1]
        arc_length += math.sqrt(dy * dy + dx * dx)

    # Straight-line distance between endpoints
    dy = points[-1][0] - points[0][0]
    dx = points[-1][1] - points[0][1]
    straight = math.sqrt(dy * dy + dx * dx)

    if straight < 1.0:
        return 1.0

    return arc_length / straight


def compute_max_angular_change(points: list, step: int = 10) -> float:
    """Max angular change between consecutive direction vectors.

    Uses a step size to avoid noise from pixel-level jitter.
    Returns angle in degrees.
    """
    if len(points) < step * 3:
        return 0.0

    max_change = 0.0
    prev_angle = None
    for i in range(0, len(points) - step, step):
        dy = points[i + step][0] - points[i][0]
        dx = points[i + step][1] - points[i][1]
        angle = math.atan2(dy, dx)
        if prev_angle is not None:
            change = abs(angle - prev_angle)
            # Normalize to [0, pi]
            if change > math.pi:
                change = 2 * math.pi - change
            max_change = max(max_change, change)
        prev_angle = angle

    return math.degrees(max_change)


def compute_endpoint_angle(points: list) -> float:
    """Angle of the line between first and last point, from horizontal.

    Returns angle in degrees (0 = horizontal, 90 = vertical).
    """
    if len(points) < 2:
        return 0.0
    dy = points[-1][0] - points[0][0]
    dx = points[-1][1] - points[0][1]
    angle = math.atan2(abs(dy), abs(dx))
    return math.degrees(angle)


def compute_stroke_width_stats(mask_component: np.ndarray,
                               skeleton: np.ndarray) -> tuple:
    """Compute mean and std of stroke width using distance transform.

    Returns (mean_width, std_width).
    """
    dist = cv2.distanceTransform(mask_component, cv2.DIST_L2, 5)
    skel_pixels = skeleton > 0
    if not np.any(skel_pixels):
        return 0.0, 0.0
    widths = dist[skel_pixels]
    return float(np.mean(widths)), float(np.std(widths))


def count_holes(mask_component: np.ndarray) -> int:
    """Count the number of holes in a connected component.

    Uses contour hierarchy — holes are inner contours.
    """
    contours, hierarchy = cv2.findContours(
        mask_component, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
    )
    if hierarchy is None:
        return 0
    # Holes are contours whose parent is an outer contour
    holes = 0
    for i in range(len(contours)):
        if hierarchy[0][i][3] >= 0:  # has a parent = inner contour = hole
            holes += 1
    return holes


def classify(total: int) -> str:
    """Map a numeric total score to a classification label."""
    if total >= CONFIDENT_THRESHOLD:
        return "confident"
    if total >= PROBABLE_THRESHOLD:
        return "probable"
    if total >= UNCERTAIN_THRESHOLD:
        return "uncertain"
    return "reject"


def score_component(mask_component: np.ndarray) -> dict:
    """Score a single connected component on all heuristics.

    Args:
        mask_component: Binary mask of just this component (cropped or full-size).

    Returns dict with individual scores and total. The 6 heuristics each
    contribute 0 or 1; total range is 0-6. See `classify()` for the
    label mapping.
    """
    scores = {}

    # Compute skeleton
    skeleton = compute_skeleton(mask_component)
    arc_len = skeleton_arc_length(skeleton)
    endpoints, _ = skeleton_endpoints_and_junctions(skeleton)
    points = ordered_skeleton_points(skeleton, endpoints)

    # 1. Arc length
    scores["arc_length"] = 1 if arc_len > 100 else 0

    # 2. Sinuosity
    sinuosity = compute_sinuosity(points)
    scores["sinuosity"] = 1 if sinuosity > 1.1 else 0

    # 3. Smooth curvature
    max_angle = compute_max_angular_change(points)
    scores["smooth_curvature"] = 1 if max_angle < 70 else 0

    # 4. Downhill tendency
    endpoint_angle = compute_endpoint_angle(points)
    scores["downhill"] = 1 if endpoint_angle > 15 else 0

    # 5. Consistent stroke width
    mean_w, std_w = compute_stroke_width_stats(mask_component, skeleton)
    scores["stroke_width"] = 1 if std_w < 2.0 else 0

    # 6. No enclosed holes
    holes = count_holes(mask_component)
    scores["no_holes"] = 1 if holes == 0 else 0

    total = sum(scores.values())

    return {
        "scores": scores,
        "total": total,
        "classification": classify(total),
        "arc_length": arc_len,
        "sinuosity": sinuosity,
        "max_angular_change": max_angle,
        "endpoint_angle": endpoint_angle,
        "stroke_width_mean": mean_w,
        "stroke_width_std": std_w,
        "holes": holes,
        "num_points": len(points),
    }
