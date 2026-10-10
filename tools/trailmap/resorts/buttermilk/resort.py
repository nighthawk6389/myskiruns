"""Buttermilk's 2025-26 trail map (aspensnowmass.com, its trail-map page: one Illustrator page, "layered", drawn like
Snowmass's): trail lines are vectors over a 100 dpi painting, blue, black and green strokes; names are white text on
a pill in the run's colour, set on the run's line. Read by tools/trailmap/pdf_resort.py; prepare.py extracts it."""
import json
import os

CLIP = (0, 0, 1143, 741)  # PDF points: the page (the legend and the logo left out of the reading: prepare.py)
SCALE = 3  # map px per PDF point
SOURCE = ('Buttermilk 2025-26 trail map PDF (aspensnowmass.com): 1.12 pt blue, black and green strokes, '
          'tools/trailmap/resorts/buttermilk/prepare.py; percent of the map image')
SYMBOL_REACH = 10  # pt (no symbols are read: the rating is the pill's colour)
END_REACH = 4  # pt from a name's end to the end of a line that runs into it
ALONG = 5  # pt: a name is printed on its own line or beside it, its pill along the line
ALONG_NEAREST = True
ALONG_SHORT = True
ALONG_FIRST = True  # names are set on their own line: that line is the name's
NO_STRETCH_BESIDE = True

# the printed bases, each with its elevation as printed: the trail report's lift areas
AREAS = [('west-buttermilk', 'West Buttermilk', 8693), ('tiehack', 'Tiehack', 8037), ('main', 'Main Buttermilk', 7870)]
_AREA_ID = {'Main': 'main', 'Tiehack': 'tiehack', 'West Buttermilk': 'west-buttermilk'}

# the resort's trail report (report.json: its grooming feed, every trail with its lift area and rating); its uphill
# routes are no runs
REPORT = [t for t in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
          if t[1] != 'Uphill Routes']
NAMES = sorted({n for n, _a, _r in REPORT})
AS_PRINTED = True  # names are shown as the report spells them
AREA_OF = {}
for _n, _a, _r in REPORT:
    if _a in _AREA_ID:
        AREA_OF.setdefault(_n, _AREA_ID[_a])
# the parks the map prints as runs (the report's Pipes/Parks), the report's Timberdoodle Glad (sic), and Ptarmigan
# Glade, printed but not on the report (above Tiehack's Ptarmigan)
AREA_OF.update({'Super Pipe': 'main', 'Uncle Chucks Glades': 'main', 'Spruce Face': 'main', 'Government': 'main',
                "Red's Rover": 'west-buttermilk', 'Timberdoodle Glade': 'tiehack', 'Ptarmigan Glade': 'tiehack',
                'Ridge Trail (Upper)': 'main', 'Ridge Trail (Lower)': 'main', "Jacob's Ladder": 'main'})


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


def is_name(label):
    return True  # prepare.py keeps the names (white text on a green, blue or black pill) only


# the rating is the pill's colour (the map has no expert terrain)
COLOR_SYMBOL = {'green': 'circle', 'blue': 'square', 'black': 'diamond'}
# names printed in parts (two or three lines), in reading order
# (two GLADEs: each part by where it is printed, map px)
JOIN = [('UNCLE', 'CHUCK\'S', 'GLADES'), ('MIDWAY', 'AVENUE'), ('TIMBER', 'DOODLE', ('GLADE', (1310, 872))),
        ('PTARMIGAN', ('GLADE', (1484, 768)))]
JOIN_GAP = 10
TWO_LINE = {' '.join(t if isinstance(t, str) else t[0] for t in p) for p in JOIN}
SPLIT = {}
NO_STRETCH = set()
LABEL_LINE = set()
DROP = []
# as the report names them (NAMES spells the rest by their letters): HOMESTEAD ROAD printed either side of the Summit
# Express, LOWER SAVIO either side of Homestead Road; SAVIO printed at the top is the report's Savio (Upper); RIDGE
# TRAIL printed in two parts, RIDGE on its green upper line and TRAIL on its blue lower one (the report lists a green
# and a blue Ridge Trail); the report's Timberdoodle Glad (sic)
RENAME = {'HOMESTEAD': 'Homestead Road', 'LOWER': 'Lower Savio', 'SAVIO': 'Savio (Upper)',
          'RIDGE': 'Ridge Trail (Upper)', 'TRAIL': 'Ridge Trail (Lower)', 'TIMBER DOODLE GLADE': 'Timberdoodle Glade',
          'SPRUCE': 'Spruce (Upper)', 'PTARMIGAN GLADE': 'Ptarmigan Glade', "JACOB'S LADDER": "Jacob's Ladder",
          'OREGON TRAIL (TO TIEHACK)': 'Oregon Trail'}
RENAME_AT = [((1805, 1072), 'ROAD', 'Homestead Road'), ((1763, 1120), 'SAVIO', 'Lower Savio')]
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = {'Uncle Chucks Glades': "Uncle Chuck's Glades"}  # (the report's typo)
GLADES = set()
# the terrain parks and pipes (the report's)
# (JACOB'S LADDER, printed as a black run in the park's dots, is the report's Alex's Alley (formerly Jacob's ladder):
# the map's name is kept)
PARKS = {n for n, _a, r in REPORT if r == 'TerrainPark'} | {"Jacob's Ladder"}
NO_LINE = {}
