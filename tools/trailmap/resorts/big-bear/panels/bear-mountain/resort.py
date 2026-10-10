"""Big Bear Mountain Resort, the bear-mountain panel (the resort's 2025-26 image, 2500x1770): symbols from the interactive map's
groups (resorts-interactive.com map 1808) and names.py, the interactive map's lines as they are (the print draws none), put on the
print by ../../prepare.py. Read by tools/trailmap/pdf_resort.py."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('big_bear', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)
PANEL = 'bear-mountain'

CLIP = (0, 0, 2500, 1770)  # the whole image, in px: the map's units here are its pixels
SCALE = 1
# the interactive map's SVG units on the print (px): registered on its painting (register_pages.py --ref background.png --ref-scale 2.77742: 1951 inliers, median 0.22 px; the painting's own
# offset in the SVG folded in)
VICOMAP_AFFINE = (0.7033573, -0.0000097, 0.5472, 0.0000056, 0.7033661, -0.8539)
SOURCE = ("Big Bear Mountain Resort trail map (bear-mountain): the interactive map's lines as they are (the print draws n"
          'one), tools/trailmap/resorts/big-bear/prepare.py; percent of the map image')
GROUPED = True  # every symbol (and the interactive map's lines) carries its trail's name
MATCH_ENDS = False  # the runs have no lines: each piece is named by its group
SYMBOL_REACH = 40  # px: a label at its symbol, or names.py's label's end to the symbol printed by it
END_REACH = 0
ALONG = 0

is_name = TOP.is_name
NAMES, AREA_OF, AS_PRINTED = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED
area = TOP.area_of_panel(PANEL)
JOIN = []
TWO_LINE = set()
# the names in no group (names.py's labels): the run has no line on the print nor in the interactive map, so its
# overlay is the stretch along its printed name, from its symbol (Schweitzer's way)
import importlib.util as _u  # noqa: E402
_s = _u.spec_from_file_location('big_bear_names', os.path.join(_here, '../../names.py'))
_names = _u.module_from_spec(_s)
_s.loader.exec_module(_names)
LABEL_LINE = {e[0] for e in _names.LABELS.get(PANEL, [])} - {'Easy Street', "Outlaw's Alley"}  # (traced instead)
NO_STRETCH = {'Easy Street', "Outlaw's Alley"}  # traced along their slope instead (decisions.py)
DROP = []
# this mountain's Pipeline (the other mountain has one too: resort.py)
RENAME = {'Pipeline': 'Pipeline (Bear Mountain)'}
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
RATING = {}
DISPLAY = dict(TOP.DISPLAY)
GLADES = set()
PARKS = TOP.PARKS
DEFAULT_SYMBOL = TOP.DEFAULT_SYMBOL
NO_LINE = {}
