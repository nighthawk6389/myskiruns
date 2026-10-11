"""Crystal Mountain, the Northway panel: the inset image the resort's trail-maps page shows beside the trail map
(winter-2425-northway-map.jpg, served as a 1247 x 1105 WebP; the same as skimap.org's map 30456), the Northway lift's
terrain behind the main map's ridge, read on crops (../../names.py: each name and symbol, each run's black line as
points, routed along the painted one by ../../prepare.py). Read by tools/trailmap/pdf_resort.py."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('crystal_mountain', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)
_spec = importlib.util.spec_from_file_location('crystal_mountain_names', os.path.join(_here, '../../names.py'))
_names = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_names)
PANEL = os.path.basename(_here)

CLIP = (0, 0, 1, 1)  # unused: no PDF; the labels are given in map px (EXTRA)
SCALE = 1
SOURCE = (f'Crystal Mountain Northway inset image (crystalmountainresort.com): the lines read on crops and routed '
          'along the painted ones, tools/trailmap/resorts/crystal-mountain/prepare.py; percent of the map image')
GROUPED = True  # every line piece carries its trail's name (names.py)
SYMBOL_REACH = 0
END_REACH = 0  # the pieces are named by names.py, not by where they end
ALONG = 0

NAMES, AREA_OF, AS_PRINTED, PARKS = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED, set()
is_name = TOP.is_name


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in TOP.NOT_IN_REPORT')


JOIN, TWO_LINE, SPLIT = [], set(), {}
NO_STRETCH = set()
LABEL_LINE = set()
DROP = []
RENAME = dict(TOP.RENAME)
RENAME_AT = []
# every name at its label, with its symbol, spelled as the report spells it
EXTRA = [(TOP.spelled(n), x, y, s) for n, (x, y), s, *_ in _names.READING[PANEL]]
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = {}
GLADES = set()
RATING = {}
DEFAULT_SYMBOL = {}
NO_LINE = {}
