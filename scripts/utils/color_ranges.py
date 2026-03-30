"""HSV color range definitions for trail segmentation.

OpenCV uses H: 0-180, S: 0-255, V: 0-255.

Color scheme on the Killington trail map:
  - Green lines = easy trails
  - Blue/cyan lines = intermediate trails AND lift lines (distinguished by geometry)
  - Black/dark lines = advanced trails
  - Red/dark-red thin lines = expert/double-black trails
  - Pink/magenta thick lines = lift lines (NOT trails)
  - Yellow dashed = boundary lines
  - Cyan bright = lift lines
"""

import numpy as np

# Trail color ranges — lowered thresholds to capture more trails.
# Heuristic scoring handles the extra noise.
TRAIL_COLOR_RANGES = {
    "green": [
        # Easy trails — lowered saturation from 140→100 to catch fainter trails
        (np.array([35, 100, 60]), np.array([85, 255, 255])),
    ],
    "blue": [
        # Intermediate trails — wider range, lowered saturation from 90→60
        (np.array([90, 60, 50]), np.array([135, 255, 255])),
    ],
    "red": [
        # Expert/double-black trails — thin red/dark-red lines
        # Red hue wraps around 0/180
        (np.array([0, 70, 70]), np.array([12, 255, 255])),
        (np.array([165, 70, 70]), np.array([180, 255, 255])),
    ],
}

# Lift line color ranges — tracked separately, excluded from trail extraction
LIFT_COLOR_RANGES = {
    "magenta_lift": [
        # Pink/magenta lift lines — thick straight lines
        (np.array([140, 80, 80]), np.array([165, 255, 255])),
    ],
    "cyan_lift": [
        # Cyan lift lines
        (np.array([80, 100, 150]), np.array([95, 255, 255])),
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
    "red": (0, 0, 255),
    "black": (128, 128, 128),
    "magenta_lift": (255, 0, 255),
    "cyan_lift": (255, 255, 0),
    "yellow": (0, 255, 255),
}
