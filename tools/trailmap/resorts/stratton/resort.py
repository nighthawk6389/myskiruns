"""Stratton's 2025-26 trail map (James Niehues's painting): the resort's PDF (stratton.com, 251021_wintermap) is
flattened, the whole page one 3024 x 2880 image, the map image (BOX: the painting above the legend). Its vectors come
from the 2020-21 export of the same artwork (skimap.org map 20146: every run's line a 1 pt dashed stroke in green, blue
or black, the names live text, the symbols fills), registered on it (AFFINE). What this season prints otherwise (the
parks redrawn in the lower mountain, some names moved or renamed) is set out below (GONE, MOVED, NEW_SYMBOLS) and in
decisions.py (the lines no longer drawn, the lines drawn anew). prepare.py extracts it; read by
tools/trailmap/pdf_resort.py."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# the 2025-26 image's map (px: x0, y0, x1, y1): the painting, above the legend
BOX = (0, 0, 3024, 2061)
# the 2020-21 page (pt) on the 2025-26 image (px), registered with tools/trailmap/register_pages.py (SIFT matches on the
# page's render, RANSAC: 11561 inliers, median residual 0.14 px): x = a pt_x + b pt_y + c, y = d pt_x + e pt_y + f
AFFINE = (2.6417981, 0.0000539, -0.9870, 0.0000119, 2.6416134, 12.7874)
SCALE = (AFFINE[0] + AFFINE[4]) / 2  # map px per PDF point (the shear, under 0.2 px across the page, left out)
_x0, _y0 = (BOX[0] - AFFINE[2]) / AFFINE[0], (BOX[1] - AFFINE[5]) / AFFINE[4]
CLIP = (_x0, _y0, _x0 + (BOX[2] - BOX[0]) / SCALE, _y0 + (BOX[3] - BOX[1]) / SCALE)  # PDF points (2020-21)
# the 2020-21 page's legend (top left) and uphill-travel box (bottom right), pt: no runs
LEGEND = [(15, 15, 322, 215), (865, 668, 1152, 774)]
SOURCE = ("Stratton 2025-26 trail map: the 2020-21 export's 1 pt run strokes (skimap.org 20146) registered on the "
          "2025-26 PDF's image, tools/trailmap/resorts/stratton/prepare.py; percent of the map image")
SYMBOL_REACH = 10  # pt from a name's first or last character to its symbol
END_REACH = 8  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 4  # pt: a name printed beside its line
ALONG_NEAREST = True  # names printed between parallel lines: the nearest only

# the trail report (report.json: stratton.com's conditions feed, mtnpowder): every run with its area; the uphill routes
# are no runs
REPORT = [r for r in json.load(open(os.path.join(HERE, 'report.json')))['trails'] if r[1] != 'Uphill Travel']
# its areas, each with the highest elevation in it: the summit for the Upper Mountain and the glades (the Summit
# Gondola's top), the others the top of their highest lift (OpenStreetMap's lift lines on the USGS's 10 m elevation
# model, tools/trailmap/lift_tops.py): American Express for the Lower Mountain, Sunrise Express for Sun Bowl, Villager
# for the learning areas
AREAS = [('upper-mountain', 'Upper Mountain', 3875), ('lower-mountain', 'Lower Mountain', 2780),
         ('sun-bowl', 'Sun Bowl', 3094), ('glades', 'Glades', 3875), ('learning-areas', 'Learning Areas', 2286)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}
NAMES = sorted({n for n, *_r in REPORT})
AS_PRINTED = False
AREA_OF = {}
for _n, _a, *_r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])
PARKS = {n for n, _a, r in REPORT if r == 'TerrainPark'}
GLADES = {n for n, a, _r in REPORT if a == 'Glades'}


def is_name(label):
    """The runs' names: Brandon Grotesque Bold 6.5 pt (Downtowner's 6.7) in black; the lifts' are white."""
    return (label['font'] == 'BrandonGrotesque-Bold' and 6.4 < label['size'] < 6.8
            and tuple(label['color']) != (1.0, 1.0, 1.0))


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


# what the 2020-21 page prints that this season's map no longer does (prepare.py leaves them out), each near a point
# (map px): the Progression Park, gone
GONE = {'labels': [('PROGRESSION', (2028, 1433)), ('PARK', (2042, 1440))],
        'symbols': [(1978, 1077), (2108, 1154), (2084, 1553)]}  # Beeline's and Betwixt's squares, Village Walk's circle
# labels this season prints elsewhere or shorter (the parks' names lost their PARK), read on crops of this season's
# image: the 2020-21 label near a point (map px) -> its text now, with its first and last character's centres (map
# px); its characters are spaced along that line as they were
MOVED = [
    (('BEELINE', (2014, 1098)), 'BEELINE', (2025, 1105), (2075, 1130)),
    (('BETWIXT', (2130, 1191)), 'BETWIXT', (2130, 1197), (2165, 1242)),
    (('SUNTANNER PARK', (2113, 1288)), 'SUNTANNER', (2068, 1238), (2133, 1303)),
    (('TYROLIENNE PARK', (2186, 1533)), 'TYROLIENNE', (2165, 1522), (2237, 1573)),  # the learning area's (a circle)
    (('VILLAGE WALK', (2133, 1591)), 'VILLAGE WALK', (2075, 1562), (2162, 1627)),
    (('EAST BYRNES SIDE PARK', (2427, 1443)), 'EAST BYRNES SIDE', (2388, 1375), (2460, 1494)),
    (('SHORTCUT BIG BEN PARK', (1222, 1149)), 'SHORTCUT BIG BEN', (1202, 1212), (1248, 1067)),
    (('BIG BEN PARK', (909, 1505)), 'BIG BEN', (866, 1524), (915, 1502)),
]
# labels new this season, as MOVED's: text, first and last character's centres (map px)
NEW_LABELS = [('TYROLIENNE', (2058, 1453), (2133, 1510))]  # the park's, by its pill
# symbols new this season (map px): Suntanner's square, Tyrolienne's and Village Walk's circles, Shortcut Big Ben's square
NEW_SYMBOLS = [('square', (2060, 1228)), ('circle', (2155, 1515)), ('circle', (2066, 1554)), ('square', (1190, 1226))]

# names printed in two parts (on two lines), in reading order
JOIN = [('DIAMOND IN', 'THE ROUGH'), ('DANIEL’S', 'WEB'), ('MIKE’S', 'CUT THROUGH')]
JOIN_GAP = 12  # pt
TWO_LINE = {'DIAMOND IN THE ROUGH', 'DANIEL’S WEB', 'MIKE’S CUT THROUGH'}
SPLIT = {}
NO_STRETCH = set()
# printed with no line, or a line only beside part of the name: the stretch along the name (the parks' pills and their
# names in the lower mountain; Suntanner's and Shortcut Big Ben's lines broken by their names)
LABEL_LINE = {'Beeline', 'Betwixt', 'East Byrnes Side', 'Tyrolienne Park', 'Big Ben', 'Shortcut Gentle Ben',
              'Suntanner', 'Shortcut Big Ben'}
DROP = []
# the map's spellings that the report spells otherwise
RENAME = {'CHUTE': 'The Chute', 'GRIZZLY BEAR': 'Upper Grizzly Bear', 'LOWER GRIZZLY': 'Lower Grizzly Bear',
          'JANEWAY JCT.': 'Janeway Junction', 'LIFTLINE CUT-THRU': 'Liftline Cut Through', 'NO. 6': 'Number 6',
          'OLD #8': 'Old Number 8'}
RENAME_AT = [((2095, 1481), 'TYROLIENNE', 'Tyrolienne Park')]  # the park's, by its pill (the other the learning area)
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
RATING = {}
# names printed with no symbol: the report's rating (the parks blue, as the playbook's convention)
DEFAULT_SYMBOL = {'Beeline': 'square', 'Betwixt': 'square', 'Big Ben': 'circle', 'East Byrnes Side': 'square',
                  'Tyrolienne Park': 'square'}
DISPLAY = {}
NO_LINE = {"MIKE’S CUT THROUGH": 'A leader from its name points into the trees below Mike\'s Way: no line drawn, marker at its name'}
