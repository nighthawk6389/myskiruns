"""Jackson Hole Mountain Resort's 2025-26 trail map (jacksonhole.com's winter trail map page: one 3000x1900 PNG, James
Niehues's painting; no PDF, no interactive map). names.py is the map read on zoomed crops: each name with its label
and its run's line as points, which prepare.py routes along the painted line. Read by tools/trailmap/pdf_resort.py."""
import json
import os
import re

CLIP = (0, 0, 3000, 1900)  # the whole image, in px: the map's units are its pixels
SCALE = 1
SOURCE = ("Jackson Hole Mountain Resort trail map 2025-26 (jacksonhole.com, PNG): the lines read on crops and routed "
          'along the painted ones, tools/trailmap/resorts/jackson-hole/prepare.py; percent of the map image')
GROUPED = True  # every line piece carries its trail's name (names.py)
MATCH_ENDS = False
SYMBOL_REACH = 0
END_REACH = 0  # the pieces are named by names.py, not by where they end
ALONG = 0

# the map's two mountains, each with its summit's elevation as printed
AREAS = [('rendezvous', 'Rendezvous Mountain', 10450), ('apres-vous', 'Après Vous Mountain', 8481)]
# Après Vous Mountain: east of the line from the Teton lift's summit down the Teton and Teewinot lifts' west side
# (its runs, Werner's, Hanna's, Teewinot's, Saratoga Bowl's, and the Teewinot lift's at the base)
_DIVIDE = [(1960, 280), (1960, 1040), (1640, 1330), (1560, 1520)]

# the trail report (report.json: the feed jacksonhole.com's report pages load): names and ratings, no areas
REPORT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
NAMES = sorted({n for n, _a, _r in REPORT})
AS_PRINTED = True  # names.py names each run as the report spells it (the others as printed)
AREA_OF = {}


def key(name):
    """A name with case, spaces and punctuation left out (pdf_resort.py's spelling_key)."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


def area(c):
    """Après Vous Mountain east of _DIVIDE, else Rendezvous Mountain."""
    x, y = c
    for (x0, y0), (x1, y1) in zip(_DIVIDE, _DIVIDE[1:]):
        if y0 <= y <= y1:
            xd = x0 + (x1 - x0) * (y - y0) / ((y1 - y0) or 1)
            return 'apres-vous' if x > xd else 'rendezvous'
    return 'rendezvous'


def is_name(label):
    return True


# the name's colour is its rating; the report's ratings (double black diamonds, the resort's double blue squares,
# advanced intermediate: blue in the app) come first
COLOR_SYMBOL = {'green': 'circle', 'blue': 'square', 'black': 'diamond'}
_SYMBOL = {'Green': 'circle', 'Blue': 'square', 'DoubleBlue': 'square', 'Black': 'diamond',
           'DoubleBlack': 'double-diamond'}
RATING = {n: _SYMBOL[r] for n, _a, r in REPORT if r in _SYMBOL}
JOIN = []
TWO_LINE = set()
# the stretch along the printed name: the base area's runs (printed in the slow zones' hatching), and the chutes
# printed with no line of their own
LABEL_LINE = {"Eagle's Rest", 'Pooh Bear', 'Antelope Flats', 'Werner (Lower)', 'Teewinot (Lower)',
              "Eagle's Rest Cutoff", 'Way Home', 'Alta Chute 1', 'Alta Chute 2', 'Alta Chute 3'}
NO_STRETCH = set()
DROP = []
RENAME = {}
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = {}
GLADES = {'Grizzly Glade', 'Washakie Glade', 'Moran Woods', 'Woolsey Woods'}
# the terrain parks: the report's, and the print's pills (Eagle's Rest's and Antelope Flats') and the Stash's icons
PARKS = {n for n, _a, r in REPORT if r == 'TerrainPark'} | {"Eagle's Rest Terrain Park",
                                                             'Antelope Flats Terrain Park'}
DEFAULT_SYMBOL = {n: 'square' for n in PARKS}
NO_LINE = {}
