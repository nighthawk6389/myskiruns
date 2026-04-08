"""HSV color range definitions for trail segmentation.

OpenCV uses H: 0-180, S: 0-255, V: 0-255.

Color scheme on the Killington trail map:
  - Green lines = easy trails (green circles)
  - Blue lines = intermediate trails (blue squares)
  - Black lines = advanced AND expert trails (black/double-black diamonds)
  - Magenta/pink thick straight lines = ski lifts (NOT trails)
  - Yellow dashed = boundary lines
  - Sky at top of image = blue/cyan, must be masked out
"""

import numpy as np

# Trail color ranges — LOW confidence (includes terrain, needs filtering)
TRAIL_COLOR_RANGES = {
    "green": [
        (np.array([35, 90, 60]), np.array([85, 255, 255])),
    ],
    "blue": [
        # Raised S from 50→90 to reduce terrain flood; multi-scale extends with S>=50
        (np.array([80, 90, 40]), np.array([135, 255, 255])),
        (np.array([75, 90, 40]), np.array([82, 255, 255])),
    ],
}

# Trail color ranges — HIGH confidence (trail lines only, minimal terrain)
TRAIL_COLOR_RANGES_HIGH = {
    "green": [
        (np.array([35, 130, 60]), np.array([85, 255, 255])),
    ],
    "blue": [
        (np.array([80, 130, 40]), np.array([135, 255, 255])),
        (np.array([75, 130, 40]), np.array([82, 255, 255])),
    ],
}

# Extended LOW ranges for multi-scale fill (same as main ranges)
TRAIL_COLOR_RANGES_LOW = TRAIL_COLOR_RANGES

# Lift line color ranges — tracked separately, excluded from trail extraction
LIFT_COLOR_RANGES = {
    "magenta_lift": [
        # Pink/magenta lift lines — thick straight lines
        (np.array([140, 80, 80]), np.array([175, 255, 255])),
    ],
}

# Boundary / non-trail color ranges
OTHER_COLOR_RANGES = {
    "yellow": [
        # Boundary/property lines
        (np.array([15, 100, 100]), np.array([35, 255, 255])),
    ],
}

# Combined for backward compatibility
COLOR_RANGES = {**TRAIL_COLOR_RANGES, **LIFT_COLOR_RANGES, **OTHER_COLOR_RANGES}

# Colors used for visualization overlays (BGR)
VIS_COLORS_BGR = {
    "green": (0, 255, 0),
    "blue": (255, 0, 0),
    "black": (128, 128, 128),
    "magenta_lift": (255, 0, 255),
    "yellow": (0, 255, 255),
}
