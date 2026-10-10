"""Whitefish Mountain Resort, the front-side panel: names.py's reading of it (labels and their runs' lines, snapped by
../../prepare.py). Read by tools/trailmap/pdf_resort.py."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('whitefish', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)
_spec = importlib.util.spec_from_file_location('whitefish_names', os.path.join(_here, '../../names.py'))
_names = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_names)
PANEL = 'front-side'

CLIP = (0, 0, 1, 1)  # unused: no PDF; the labels are given in map px (EXTRA)
SCALE = 1
SOURCE = ('Whitefish Mountain Resort trail map (skiwhitefish.com, web JPEG), front-side: the lines read on crops and '
          'snapped onto the painted ones, tools/trailmap/resorts/whitefish/prepare.py; percent of the map image')
GROUPED = True  # every line piece carries its trail's name (names.py)
SYMBOL_REACH = 0
END_REACH = 0  # the pieces are named by names.py, not by where they end
ALONG = 0

is_name = TOP.is_name
NAMES, AREA_OF, AS_PRINTED = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED
area = TOP.area_of_panel(PANEL)
COLOR_SYMBOL = TOP.COLOR_SYMBOL
JOIN, TWO_LINE, SPLIT = TOP.JOIN, TOP.TWO_LINE, TOP.SPLIT
NO_STRETCH = set()
LABEL_LINE = set()
DROP = []
RENAME = dict(TOP.RENAME)
RENAME_AT = []
# every name at its label, with its symbol (a park's: none), spelled as the report spells it (as pdf_resort.py spells
# the pieces' names: by their letters)
_spelled = {TOP.key(n): n for n in NAMES}


def _name(n):
    n = TOP.RENAME.get(n, n)
    return _spelled.get(TOP.key(n), n)


EXTRA = [(_name(n), x, y) if s == 'park' else (_name(n), x, y, s) for n, (x, y), s, *_ in _names.READING.get(PANEL, [])]
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = dict(TOP.DISPLAY)
GLADES = TOP.GLADES
PARKS = TOP.PARKS | {_name(n) for n, _at, s, *_ in _names.READING.get(PANEL, []) if s == 'park'}
RATING = TOP.RATING
NO_LINE = {}
