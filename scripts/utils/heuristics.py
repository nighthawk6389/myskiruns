"""Geometric heuristic scoring for trail vs. non-trail classification.

Each heuristic contributes +1 to a confidence score (0-9 range).
Score 7-9: high confidence trail
Score 5-6: probable trail (flagged for review)
Score 3-4: low confidence (candidate for SAM 2 refinement)
Score 0-2: reject (noise/text)
"""

import math

import cv2
import numpy as np
from skimage.morphology import skeletonize


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


def score_component(mask_component: np.ndarray,
                    mountain_mask: np.ndarray | None = None,
                    all_other_skeletons: np.ndarray | None = None) -> dict:
    """Score a single connected component on all heuristics.

    Args:
        mask_component: Binary mask of just this component (cropped or full-size).
        mountain_mask: Optional binary mask of the mountain region (full-size).
        all_other_skeletons: Optional combined skeleton of all other accepted components.

    Returns dict with individual scores and total.
    """
    scores = {}

    # Compute skeleton
    skeleton = compute_skeleton(mask_component)
    arc_len = skeleton_arc_length(skeleton)
    endpoints, junctions = skeleton_endpoints_and_junctions(skeleton)
    points = ordered_skeleton_points(skeleton, endpoints)

    # 1. Arc length
    scores["arc_length"] = 1 if arc_len > 100 else 0

    # 2. Aspect ratio
    ys, xs = np.where(mask_component > 0)
    if len(ys) > 0:
        bbox_h = ys.max() - ys.min() + 1
        bbox_w = xs.max() - xs.min() + 1
        aspect = max(bbox_h, bbox_w) / max(min(bbox_h, bbox_w), 1)
        scores["aspect_ratio"] = 1 if aspect > 5 else 0
    else:
        scores["aspect_ratio"] = 0

    # 3. Sinuosity
    sinuosity = compute_sinuosity(points)
    scores["sinuosity"] = 1 if sinuosity > 1.1 else 0

    # 4. Smooth curvature
    max_angle = compute_max_angular_change(points)
    scores["smooth_curvature"] = 1 if max_angle < 70 else 0

    # 5. Downhill tendency
    endpoint_angle = compute_endpoint_angle(points)
    scores["downhill"] = 1 if endpoint_angle > 15 else 0

    # 6. Consistent stroke width
    mean_w, std_w = compute_stroke_width_stats(mask_component, skeleton)
    scores["stroke_width"] = 1 if std_w < 2.0 else 0

    # 7. No enclosed holes
    holes = count_holes(mask_component)
    scores["no_holes"] = 1 if holes == 0 else 0

    # 8. Within mountain region
    if mountain_mask is not None and len(ys) > 0:
        cy, cx = int(np.mean(ys)), int(np.mean(xs))
        if 0 <= cy < mountain_mask.shape[0] and 0 <= cx < mountain_mask.shape[1]:
            scores["in_mountain"] = 1 if mountain_mask[cy, cx] > 0 else 0
        else:
            scores["in_mountain"] = 0
    else:
        scores["in_mountain"] = 1  # assume in-mountain if no mask provided

    # 9. Proximity to other trails
    if all_other_skeletons is not None and len(endpoints) > 0:
        min_dist = float("inf")
        for ey, ex in endpoints:
            if 0 <= ey < all_other_skeletons.shape[0] and 0 <= ex < all_other_skeletons.shape[1]:
                # Check a window around the endpoint
                y_lo = max(0, ey - 50)
                y_hi = min(all_other_skeletons.shape[0], ey + 50)
                x_lo = max(0, ex - 50)
                x_hi = min(all_other_skeletons.shape[1], ex + 50)
                window = all_other_skeletons[y_lo:y_hi, x_lo:x_hi]
                if np.any(window > 0):
                    dist = cv2.distanceTransform(
                        255 - all_other_skeletons[y_lo:y_hi, x_lo:x_hi],
                        cv2.DIST_L2, 5
                    )
                    local_y, local_x = ey - y_lo, ex - x_lo
                    if 0 <= local_y < dist.shape[0] and 0 <= local_x < dist.shape[1]:
                        min_dist = min(min_dist, dist[local_y, local_x])
        scores["proximity"] = 1 if min_dist < 50 else 0
    else:
        scores["proximity"] = 1  # no comparison data = neutral

    total = sum(scores.values())

    if total >= 7:
        classification = "confident"
    elif total >= 5:
        classification = "probable"
    elif total >= 3:
        classification = "uncertain"
    else:
        classification = "reject"

    return {
        "scores": scores,
        "total": total,
        "classification": classification,
        "arc_length": arc_len,
        "sinuosity": sinuosity,
        "max_angular_change": max_angle,
        "endpoint_angle": endpoint_angle,
        "stroke_width_mean": mean_w,
        "stroke_width_std": std_w,
        "holes": holes,
        "num_points": len(points),
    }
