"""Utilities for polyline extraction, simplification, and ordering."""

import math

import cv2
import numpy as np


def simplify_points(points: list, epsilon: float = 2.0) -> list:
    """Simplify a polyline using Douglas-Peucker algorithm.

    Args:
        points: List of (y, x) tuples.
        epsilon: Approximation accuracy. Higher = fewer points.

    Returns: Simplified list of (y, x) tuples.
    """
    if len(points) < 3:
        return points

    # cv2.approxPolyDP expects shape (N, 1, 2) in (x, y) format
    pts_array = np.array([[x, y] for y, x in points], dtype=np.float32).reshape(-1, 1, 2)
    simplified = cv2.approxPolyDP(pts_array, epsilon, closed=False)
    # Convert back to (y, x) tuples
    return [(int(pt[0][1]), int(pt[0][0])) for pt in simplified]


def order_top_to_bottom(points: list) -> list:
    """Ensure points are ordered from top (lower y = summit) to bottom (higher y = base)."""
    if len(points) < 2:
        return points
    if points[0][0] > points[-1][0]:  # first point has higher y (lower on image)
        return list(reversed(points))
    return points


def points_to_percentage(points: list, img_width: int, img_height: int) -> list:
    """Convert pixel (y, x) points to percentage [x%, y%] coordinates."""
    return [
        [round(x / img_width * 100, 3), round(y / img_height * 100, 3)]
        for y, x in points
    ]


def points_to_svg_path(pct_points: list) -> str:
    """Convert percentage points to an SVG path `d` string with quadratic Bezier smoothing."""
    if not pct_points:
        return ""
    if len(pct_points) == 1:
        return f"M {pct_points[0][0]} {pct_points[0][1]}"

    d = f"M {pct_points[0][0]} {pct_points[0][1]}"

    if len(pct_points) == 2:
        d += f" L {pct_points[1][0]} {pct_points[1][1]}"
        return d

    # Use quadratic Bezier curves for smooth rendering
    for i in range(1, len(pct_points)):
        # Control point is the previous point, end point is midpoint
        # (or the actual point for the last segment)
        if i < len(pct_points) - 1:
            # Mid-point between current and next
            mx = (pct_points[i][0] + pct_points[i + 1][0]) / 2
            my = (pct_points[i][1] + pct_points[i + 1][1]) / 2
            d += f" Q {pct_points[i][0]} {pct_points[i][1]} {round(mx, 3)} {round(my, 3)}"
        else:
            d += f" Q {pct_points[i - 1][0]} {pct_points[i - 1][1]} {pct_points[i][0]} {pct_points[i][1]}"

    return d


def compute_arc_length(points: list) -> float:
    """Compute total arc length of a polyline in pixels."""
    total = 0.0
    for i in range(1, len(points)):
        dy = points[i][0] - points[i - 1][0]
        dx = points[i][1] - points[i - 1][1]
        total += math.sqrt(dy * dy + dx * dx)
    return total


def compute_span(points: list) -> float:
    """Straight-line distance between first and last point."""
    if len(points) < 2:
        return 0.0
    dy = points[-1][0] - points[0][0]
    dx = points[-1][1] - points[0][1]
    return math.sqrt(dy * dy + dx * dx)


def merge_collinear_segments(segments: list, angle_threshold: float = 30.0,
                             distance_threshold: float = 20.0) -> list:
    """Merge segments that meet at junction points and are roughly collinear.

    Args:
        segments: List of lists of (y, x) points.
        angle_threshold: Max angle difference (degrees) to consider collinear.
        distance_threshold: Max pixel distance between endpoints to consider connected.

    Returns: Merged list of segments.
    """
    if len(segments) <= 1:
        return segments

    def endpoint_direction(points, from_end=False):
        """Get direction vector at an endpoint (using last few points)."""
        n = min(5, len(points))
        if from_end:
            dy = points[-1][0] - points[-n][0]
            dx = points[-1][1] - points[-n][1]
        else:
            dy = points[n - 1][0] - points[0][0]
            dx = points[n - 1][1] - points[0][1]
        return math.atan2(dy, dx)

    def endpoint_distance(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    merged = list(segments)
    changed = True

    while changed:
        changed = False
        for i in range(len(merged)):
            for j in range(i + 1, len(merged)):
                if merged[i] is None or merged[j] is None:
                    continue

                seg_a = merged[i]
                seg_b = merged[j]

                # Check all 4 endpoint combinations
                combos = [
                    (seg_a[-1], seg_b[0], "end_a_start_b"),
                    (seg_a[-1], seg_b[-1], "end_a_end_b"),
                    (seg_a[0], seg_b[0], "start_a_start_b"),
                    (seg_a[0], seg_b[-1], "start_a_end_b"),
                ]

                for pa, pb, combo_type in combos:
                    dist = endpoint_distance(pa, pb)
                    if dist > distance_threshold:
                        continue

                    # Check angle compatibility
                    if combo_type == "end_a_start_b":
                        angle_a = endpoint_direction(seg_a, from_end=True)
                        angle_b = endpoint_direction(seg_b, from_end=False)
                    elif combo_type == "end_a_end_b":
                        angle_a = endpoint_direction(seg_a, from_end=True)
                        angle_b = endpoint_direction(list(reversed(seg_b)), from_end=False)
                    elif combo_type == "start_a_start_b":
                        angle_a = endpoint_direction(list(reversed(seg_a)), from_end=True)
                        angle_b = endpoint_direction(seg_b, from_end=False)
                    else:  # start_a_end_b
                        angle_a = endpoint_direction(list(reversed(seg_a)), from_end=True)
                        angle_b = endpoint_direction(list(reversed(seg_b)), from_end=False)

                    angle_diff = abs(angle_a - angle_b)
                    if angle_diff > math.pi:
                        angle_diff = 2 * math.pi - angle_diff
                    angle_diff_deg = math.degrees(angle_diff)

                    if angle_diff_deg < angle_threshold:
                        # Merge
                        if combo_type == "end_a_start_b":
                            merged[i] = seg_a + seg_b
                        elif combo_type == "end_a_end_b":
                            merged[i] = seg_a + list(reversed(seg_b))
                        elif combo_type == "start_a_start_b":
                            merged[i] = list(reversed(seg_a)) + seg_b
                        else:
                            merged[i] = seg_b + seg_a

                        merged[j] = None
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break

        merged = [s for s in merged if s is not None]

    return merged
