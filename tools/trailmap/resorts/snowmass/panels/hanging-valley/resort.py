"""Snowmass, the Hanging Valley inset (the top of the page: Hanging Valley drawn larger than on the main map, with the
names of runs the main map leaves unnamed). Trail lines are thinner black strokes and the expert runs' yellow casings
(in two yellows), Turkey Trot blue; names are white text on a pill in the run's colour, set on the run's own line.
Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location('snowmass', os.path.join(os.path.dirname(__file__), '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (362, 0, 555, 129)  # PDF points: the inset
SCALE = 6  # map px per PDF point (the inset's type is half the main map's)
SOURCE = ('Snowmass 2025-26 trail map PDF (aspensnowmass.com): 1.12 pt blue, black and green strokes and the expert '
          "runs' yellow casings, tools/trailmap/resorts/snowmass/prepare.py; percent of the map image")
SYMBOL_REACH = 5  # pt (no symbols are read: the rating is the pill's colour)
END_REACH = 2  # pt from a name's end to the end of a line that runs into it
ALONG = 2.5  # pt: a name is printed on its own line or beside it, its pill along the line
ALONG_NEAREST = True
ALONG_SHORT = True  # also names of two or three letters (RIO, AMF)
ALONG_FIRST = True  # names are set on their own line: that line is the name's
NO_STRETCH_BESIDE = True

is_name = TOP.is_name
NAMES, AREA_OF, AS_PRINTED, area = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED, TOP.area
COLOR_SYMBOL = TOP.COLOR_SYMBOL
JOIN, TWO_LINE, SPLIT = TOP.JOIN, TOP.TWO_LINE, TOP.SPLIT
JOIN_GAP = 4.5  # pt (half the main map's type)
NO_STRETCH = set()
LABEL_LINE = set()
DROP = list(TOP.DROP)
RENAME = dict(TOP.RENAME, HEADWALL='Hanging Valley Headwall')
RENAME_AT = []
# the cased traverse along the boundary below High Pass prints no name: the report's High Pass (Lower BD), Hanging
# Valley's double black (decisions.py names its line), rated as its casing shows
EXTRA = [('High Pass (Lower BD)', 700, 177, 'double-diamond')]
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = dict(TOP.DISPLAY)
GLADES = TOP.GLADES
PARKS = TOP.PARKS
NO_LINE = {}
