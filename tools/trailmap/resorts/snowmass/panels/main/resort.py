"""Snowmass, the whole mountain (the page; its Hanging Valley inset is its own panel, and the legend is left out).
Trail lines are blue, black and green strokes, the expert runs a black line in a yellow casing; names are white text
on a pill in the run's colour, set on the run's own line. Read by tools/trailmap/pdf_resort.py; ../../prepare.py
extracts it."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location('snowmass', os.path.join(os.path.dirname(__file__), '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (0, 0, 1368, 520)  # PDF points: the page
SCALE = 3  # map px per PDF point
SOURCE = ('Snowmass 2025-26 trail map PDF (aspensnowmass.com): 1.12 pt blue, black and green strokes and the expert '
          "runs' yellow casings, tools/trailmap/resorts/snowmass/prepare.py; percent of the map image")
SYMBOL_REACH = 10  # pt (no symbols are read: the rating is the pill's colour)
END_REACH = 4  # pt from a name's end to the end of a line that runs into it
ALONG = 5  # pt: a name is printed on its own line or beside it, its pill along the line
ALONG_NEAREST = True
ALONG_SHORT = True  # also names of two or three letters (RIO, AMF)
ALONG_FIRST = True  # names are set on their own line: that line is the name's
NO_STRETCH_BESIDE = True

is_name = TOP.is_name
NAMES, AREA_OF, AS_PRINTED, area = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED, TOP.area
COLOR_SYMBOL = TOP.COLOR_SYMBOL
JOIN, JOIN_GAP, TWO_LINE, SPLIT = TOP.JOIN, TOP.JOIN_GAP, TOP.TWO_LINE, TOP.SPLIT
NO_STRETCH = set()
LABEL_LINE = set()
DROP = list(TOP.DROP)
RENAME = dict(TOP.RENAME, HEADWALL='Hanging Valley Headwall')
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = dict(TOP.DISPLAY)
GLADES = TOP.GLADES
PARKS = TOP.PARKS
NO_LINE = {}
