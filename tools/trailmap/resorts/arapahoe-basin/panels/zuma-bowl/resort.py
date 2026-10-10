"""Arapahoe Basin, the zuma-bowl panel: the Zuma Bowl painting (Montezuma Bowl, framed at the page's top right).
Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('arapahoe_basin', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (598.8, 0, 1296, 523)  # PDF points: the Zuma Bowl frame
SCALE = 3.5  # map px per PDF point
SOURCE = ('Arapahoe Basin 2025-26 trail map PDF (arapahoebasin.com), Zuma Bowl: 0.75 pt black and blue strokes'
          ', tools/trailmap/resorts/arapahoe-basin/prepare.py; percent of the map image')
SYMBOL_REACH = 12  # pt from a name's first or last letter (or its middle) to its symbol
SYMBOL_CENTRE = True  # (as on the frontside panel)
END_REACH = 8
ALONG = 5
ALONG_NEAREST = True
ALONG_FIRST = True
NO_STRETCH_BESIDE = True

NAMES, AREA_OF, AS_PRINTED = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED
is_name = TOP.is_name


def area(c):
    return 'montezuma-bowl'


# names printed in parts (on two lines), in reading order
JOIN = [("ELEPHANT'S", 'TRUNK'), ('PLACER', 'JUNCTION'), ('ZUMA HIKE', 'BACKTRAIL')]
TWO_LINE = {' '.join(p) for p in JOIN}
JOIN_GAP = 10
NO_STRETCH = set()
# runs the map draws no line for, the name printed down the run from its symbol: the stretch along the name is the
# run's overlay; the chutes, glades and trees with no line, and PLACER JUNCTION (on two lines), are markers
LABEL_LINE = {'Bierstadt', 'Black Bear', 'Crags', 'Durrance', 'End Zone', 'Eureka', 'Grays', 'Groswold',
              'Independence', 'Jump', 'Log Roll', 'Max', 'Northern Spy', 'Schauffler', 'Shining Light',
              "Tieze's Claim", 'Torreys', 'Winning Card'}
# labels that name no run: the hike-back trail (an uphill walk) and the letters of the area title's box
DROP = [(t, None) for t in ('ZUMA HIKE BACKTRAIL', 'EA', 'TE', 'NO')]
# ELEPHANT'S TRUNK, printed once: the report's Elephant's Trunk - Upper and - Lower are one trail here
RENAME = {**TOP.RENAME, "ELEPHANT'S TRUNK": "Elephant's Trunk"}
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
RATING = {}
DISPLAY = dict(TOP.DISPLAY)
GLADES = set()
PARKS = set()
NO_LINE = {}
