"""Big Bear Mountain Resort, the snow-summit panel (the resort's 2025-26 image, 2500x1859): symbols from the interactive map's
groups (resorts-interactive.com map 1818) and names.py, the print's own lines (prepare.py: colour masks, skeleton pieces), named by the symbol at each run's top, put on the
print by ../../prepare.py. Read by tools/trailmap/pdf_resort.py."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('big_bear', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)
PANEL = 'snow-summit'

CLIP = (0, 0, 2500, 1859)  # the whole image, in px: the map's units here are its pixels
SCALE = 1
# the interactive map's SVG units on the print (px): registered on its painting (register_pages.py --ref background.jpeg --ref-scale 2.77764: 1753 inliers, median 0.25 px; the painting's own
# offset in the SVG folded in)
VICOMAP_AFFINE = (0.4721829, 0.0000057, -7.1178, -0.0000010, 0.4722086, -0.4801)
SOURCE = ("Big Bear Mountain Resort trail map (snow-summit): the print's own lines (prepare.py: colour masks, skeleton pi"
          "eces), named by the symbol at each run's top, tools/trailmap/resorts/big-bear/prepare.py; percent of the map image")
GROUPED = True  # every symbol (and the interactive map's lines) carries its trail's name
MATCH_ENDS = True  # a run's symbol is printed just above its line's top end: the line ending there takes its name
SYMBOL_REACH = 6  # px: each label is at its symbol
END_REACH = 40  # px from a run's symbol to its line's top end
ALONG = 0
# prepare.py's line detection: the legend and logo box and the sky left out, the largest glyph treated as text (px), the
# shortest piece kept (px)
EXCLUDE = [(1730, 1190, 1995, 1625), (0, 0, 2500, 300)]  # and the sky (distant trees in its blue)
TEXT_MAX = 40
MIN_LEN = 25

is_name = TOP.is_name
NAMES, AREA_OF, AS_PRINTED = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED
area = TOP.area_of_panel(PANEL)
JOIN = []
TWO_LINE = set()
LABEL_LINE = set()
# the labels are points (at their symbols): no stretch along them
NO_STRETCH = set(TOP.NAMES)
DROP = []
# the print's TIMBER RIDGE, one line with one square (the interactive map's Upper; its Lower has no symbol)
RENAME = {'Timber Ridge (Upper)': 'Timber Ridge'}
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
# names printed with two ratings: the report's (Miracle Mile (Upper): two squares and a diamond, black; Side Chute and
# Olympic: diamonds and a double diamond, double black)
RATING = {'Miracle Mile (Upper)': 'diamond', 'Side Chute': 'double-diamond', 'Olympic': 'double-diamond'}
DISPLAY = dict(TOP.DISPLAY)
GLADES = set()
PARKS = TOP.PARKS | {'Westridge Park', 'ZZYZX Park'}
DEFAULT_SYMBOL = TOP.DEFAULT_SYMBOL
NO_LINE = {}
