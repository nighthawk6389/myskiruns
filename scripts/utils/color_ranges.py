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

# Trail color ranges
TRAIL_COLOR_RANGES = {
    "green": [
        # Easy trails — lowered saturation to catch fainter trails
        (np.array([35, 100, 60]), np.array([85, 255, 255])),
    ],
    "blue": [
        # Intermediate trails — S>=50 (was 60) to capture faint lines
        (np.array([85, 50, 40]), np.array([135, 255, 255])),
    ],
}

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
