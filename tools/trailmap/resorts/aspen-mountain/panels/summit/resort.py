"""Aspen Mountain, the inset of the summit (top right: the top of the mountain drawn larger). Trail lines are blue and
black strokes, the extreme terrain a black line in a yellow casing; names are white text on a pill in the run's
colour, set on the run's own line. Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location('aspen_mountain',
                                               os.path.join(os.path.dirname(__file__), '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (507, 1, 810, 233)  # PDF points
SCALE = 6  # map px per PDF point
SOURCE = ('Aspen Mountain 2025-26 trail map PDF (aspensnowmass.com): its blue and black strokes and the extreme '
          "terrain's yellow casings, tools/trailmap/resorts/aspen-mountain/prepare.py; percent of the map image")
SYMBOL_REACH = 5  # pt (no symbols are read: the rating is the pill's colour)
END_REACH = 2.5  # pt from a name's end to the end of a line that runs into it
ALONG = 3  # pt: a name is printed on its own line or beside it, its pill along the line
ALONG_NEAREST = True
ALONG_SHORT = True
ALONG_FIRST = True  # names are set on their own line: that line is the name's
NO_STRETCH_BESIDE = True

is_name = TOP.is_name
NAMES, AREA_OF, AS_PRINTED, area = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED, TOP.area
COLOR_SYMBOL = TOP.COLOR_SYMBOL
# names printed in parts, in reading order (a part is its text, or (text, (x, y)): the label near that point, map px)
JOIN = [('HERO’S', 'CHUTES #1'), ('HERO’S', 'CHUTES #2'), ('PANCAKE HOUSE', 'GLADE'),
        (('MIDNIGHT', (1469, 432)), 'GLADES'), ('PUMP', 'HOUSE HILL'), ('FACE', 'OF BELL'), ('BELL', 'MEADOW')]
TWO_LINE = {' '.join(t if isinstance(t, str) else t[0] for t in p) for p in JOIN}
SPLIT = TOP.SPLIT
JOIN_GAP = 5.5  # pt
NO_STRETCH = set()
LABEL_LINE = set()
DROP = []
RENAME = dict(TOP.RENAME)
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = dict(TOP.DISPLAY)
GLADES = TOP.GLADES
PARKS = TOP.PARKS
NO_LINE = {}
