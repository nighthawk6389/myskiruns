"""Big Bear Mountain Resort, the snow-valley panel (the resort's 2025-26 image, 1965x2400): symbols from the interactive map's
groups (resorts-interactive.com map 1825) and names.py, the interactive map's lines as they are (the print draws none), put on the
print by ../../prepare.py. Read by tools/trailmap/pdf_resort.py."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('big_bear', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)
PANEL = 'snow-valley'

CLIP = (0, 0, 1965, 2400)  # the whole image, in px: the map's units here are its pixels
SCALE = 1
# the interactive map's SVG units on the print (px): registered on its painting (register_pages.py --ref background.jpg --ref-scale 2.77778 --clip 0,0,3083,3776 (the painting, not
# its summit inset): 1963 inliers, median 0.19 px)
VICOMAP_AFFINE = (0.6392070, 0.0000107, -6.2775, -0.0000081, 0.6386182, -13.2388)
SOURCE = ("Big Bear Mountain Resort trail map (snow-valley): the interactive map's lines as they are (the print draws non"
          'e), tools/trailmap/resorts/big-bear/prepare.py; percent of the map image')
GROUPED = True  # every symbol (and the interactive map's lines) carries its trail's name
MATCH_ENDS = False  # the runs have no lines: each piece is named by its group
SYMBOL_REACH = 50  # px: a label at its symbol, or names.py's label's end to the symbol printed by it
END_REACH = 0
ALONG = 0

is_name = TOP.is_name
NAMES, AREA_OF, AS_PRINTED = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED
area = TOP.area_of_panel(PANEL)
JOIN = []
TWO_LINE = set()
# runs whose interactive-map line is a stub or two off the run (audit): a stretch along the printed name as well
LABEL_LINE = {'Bubble Gum', 'Lower Wine Rock', 'Quickie', 'Thunder Mountain', 'Upper Wine Rock', 'West Run'}
NO_STRETCH = set()
DROP = []
# this mountain's Pipeline (the other mountain has one too: resort.py)
RENAME = {'Pipeline': 'Pipeline (Snow Valley)'}
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
