"""HSV color range definitions for trail segmentation.

OpenCV uses H: 0-180, S: 0-255, V: 0-255.
These ranges are initial estimates — tune interactively with 02_segment_colors.py --tune.
"""

import numpy as np

# Each entry: list of (lower_hsv, upper_hsv) tuples.
# Multiple ranges handle wrap-around hues (e.g., red/magenta spans 170-180 and 0-10).

COLOR_RANGES = {
    "green": [
        # Vivid greens — aggressive saturation to avoid terrain
        (np.array([35, 140, 80]), np.array([85, 255, 255])),
    ],
    "blue": [
        # Intermediate trail blue
        (np.array([95, 90, 70]), np.array([130, 255, 255])),
    ],
    "magenta": [
        # Expert trails — pink/magenta, wraps around hue 0/180
        (np.array([140, 80, 80]), np.array([180, 255, 255])),
        (np.array([0, 80, 80]), np.array([10, 255, 255])),
    ],
    "cyan": [
        # Lift lines — narrow hue band between blue and green
        (np.array([80, 100, 150]), np.array([95, 255, 255])),
    ],
    "yellow": [
        # Some maps use yellow for boundaries or certain trails
        (np.array([15, 100, 100]), np.array([35, 255, 255])),
    ],
}

# Colors used for visualization overlays
VIS_COLORS_BGR = {
    "green": (0, 255, 0),
    "blue": (255, 0, 0),
    "magenta": (255, 0, 255),
    "cyan": (255, 255, 0),
    "yellow": (0, 255, 255),
    "black": (128, 128, 128),  # gray for visibility
}
