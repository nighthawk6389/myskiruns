"""Beaver Creek's 2025-26 trail map (VistaMap's painting, Gary Milliken): the resort publishes it only as an image on
Vail Resorts' CDN (scene7 20251006_BC_winter-trail_map_001, 4990x4453 px); skimap.org keeps the 2023-24 export of
the same artwork as a vector PDF (map 25267, 2023-10-04: trail lines as strokes, names as outlined glyphs, symbols
as fills, the painting as vectors too). The map image is the 2025-26 image (its map, above the partners' band:
BOX); the lines, names and symbols are the 2023 PDF's, registered on it (AFFINE). prepare.py extracts it; read by
tools/trailmap/pdf_resort.py."""
import json
import os
import re

# the 2025-26 image's map (px: x0, y0, x1, y1): all of it above the partners' band
BOX = (0, 0, 4990, 3983)
# the 2023 PDF's page (pt) on the 2025-26 image (px), registered with tools/trailmap/register_pages.py (SIFT matches
# on the page's render, RANSAC: 2664 inliers, median residual 0.092 px): x = a pt_x + b pt_y + c, y = d pt_x + e pt_y
# + f
AFFINE = (4.2776363, 0.0001465, -16.0784, 0.0000212, 4.2780610, -6.8338)
SCALE = (AFFINE[0] + AFFINE[4]) / 2  # map px per PDF point (the shear, under 0.2 px across the page, left out)
_x0, _y0 = (BOX[0] - AFFINE[2]) / AFFINE[0], (BOX[1] - AFFINE[5]) / AFFINE[4]
CLIP = (_x0, _y0, _x0 + (BOX[2] - BOX[0]) / SCALE, _y0 + (BOX[3] - BOX[1]) / SCALE)  # PDF points
SOURCE = ('Beaver Creek 2025-26 trail map: the 2023 PDF (skimap.org 25267), its 0.66 pt green, blue and black strokes '
          'registered on the 2025-26 image (Vail Resorts\' CDN), tools/trailmap/resorts/beaver-creek/prepare.py; '
          'percent of the map image')
SYMBOL_REACH = 12  # pt from a name's first or last character (or its middle) to its symbol
END_REACH = 6  # pt from a name's end (or its symbol, on the line) to the end of the line
ALONG = 4  # pt: a name printed beside its line, about a character's height off it


def is_name(label):
    """The trail names: the names' layer (drawn after the lines, before the kids' adventure zones' list box from 239800
    on, the notices and the partners); its elevations (eIevatiun: l and o in the elevations' font read as I and u) are
    no names."""
    return 230000 < label['seq'] < 237000 and not re.search(r"eIevat|\d'\d", label['text'])


# the resort's trail report (report.json: the terrain feed as Common Crawl captured it on 2026-02-07, every run with
# its area and rating), its typos fixed (Holden SKiway, Gosawk Connector, Kestrel's double spaces)
REPORT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
REPORT_FIX = {'Holden SKiway': 'Holden Skiway', 'Gosawk Connector': 'Goshawk Connector'}
REPORT = [(REPORT_FIX.get(n, ' '.join(n.split())), a, r) for n, a, r in REPORT]
NAMES = sorted({n for n, _a, _r in REPORT})
AS_PRINTED = True  # names are shown as the report spells them, else as RENAME puts them (the map prints capitals)
# the report's areas, each with the highest elevation the map prints in it (Beaver Creek Upper, Birds of Prey and
# Rose Bowl: the summit's; Beaver Creek Lower: Spruce Saddle's, where its runs start; Strawberry Park and Elkhorn: Red
# Tail's, the top of the Strawberry Park lift; McCoy Park and the skiways: Bachelor Gulch Mountain's and the village's)
AREAS = [('beaver-creek-upper', 'Beaver Creek Upper', 11440), ('birds-of-prey', 'Birds of Prey', 11440),
         ('rose-bowl', 'Rose Bowl', 11440), ('grouse-mountain', 'Grouse Mountain', 10688),
         ('larkspur', 'Larkspur', 10370), ('beaver-creek-lower', 'Beaver Creek Lower', 10200),
         ('bachelor-gulch', 'Bachelor Gulch', 9560), ('mccoy-park', 'McCoy Park', 9560),
         ('arrowhead', 'Arrowhead', 9100), ('strawberry-park', 'Strawberry Park', 8850),
         ('elkhorn', 'Elkhorn', 8850), ('resort-skiways', 'Resort Skiways', 8100),
         ('beaver-creek-landing', 'Beaver Creek Landing', 7430)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}
AREA_OF = {}
for _n, _a, _r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])


def _of(name):
    """The area of a run the report splits into parts (Kestrel  Upper, Peregrine - Lower): its first part's."""
    return next(_AREA_ID[a] for n, a, _r in REPORT if n.startswith(name))


# the runs the map prints once (or several times along the run) that the report splits into parts, and the runs the
# report lists by another name: one trail each, named as the map prints them
AREA_OF.update({n: _of(n) for n in ('Kestrel', 'Peregrine', 'Larkspur', 'Raven Ridge', 'Stacker', 'Intertwine',
                                    'Primrose', 'Cinch', 'Dally', 'Latigo', "Gunder's", 'Little Brave',
                                    'Cabin Fever')})
AREA_OF.update({'Beaver Creek Mountain Expressway': 'larkspur', 'Upper Stirrup': 'arrowhead',
                'Lower Stirrup': 'arrowhead', 'Upper Stone Creek Chutes': 'rose-bowl',
                'Lower Stone Creek Chutes': 'rose-bowl', 'Big Bark': 'beaver-creek-lower',
                'Little Bark': 'beaver-creek-lower', 'Borders-Pines-Chateau Skiway': 'resort-skiways',
                "Slanderous Sam's": 'beaver-creek-upper', 'Tombstone Territory': 'beaver-creek-lower',
                'Buckaroo Bowl': 'beaver-creek-lower', 'Keller Glade': 'beaver-creek-lower',
                'Aspen Alley': 'arrowhead', 'West Fall Road': 'beaver-creek-lower'})


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


# names printed in parts (two or three lines), in reading order; a part printed more than once near another
# name's is (text, (x, y)): the label near that point (map px)
JOIN = [
    ('UPPER', 'GOLDEN EAGLE'),
    ('MIDDLE', 'GOLDEN EAGLE'),
    (('UPPER', (1678, 1076)), ('GOSHAWK', (1686, 1101))),
    (('GOSHAWK', (1755, 986)), 'CONNECTOR'),
    ('GOLDEN', 'EAGLE FLYWAY'),
    ('UPPER', 'STONE CREEK', 'CHUTES'),
    ('LOWER', 'STONE CREEK', 'CHUTES'),
    ('BEAVER CREEK', 'MOUNTAIN', 'EXPRESSWAY'),
    ("FORD'S", 'WAY'),
    ('SHOOTING', 'STAR'),
    ('McCOY', 'SKIWAY'),
    ('RIDGEPOINT', 'SKIWAY'),
    ('KELLER', 'GLADE'),
    ('BARREL', 'STAVE'),
    ('TOMBSTONE', 'TERRITORY'),
    ('DALLY', 'ALLEY'),
    ("FOOL'S", 'GOLD'),
    ('BUCKAROO', 'BOWL'),
    ('HIGHLANDS', 'SKIWAY'),
    ('CREEKSIDE', 'SKIWAY'),
    ('BORDERS-PINES -', 'CHATEAU SKIWAY'),
    ('THREE TREE', 'GULLY'),
    ('RUFFED', 'GROUSE'),
    ('ROYAL ELK', 'GLADE'),
    ('HOLDEN', 'SKIWAY'),
    ('ELKHORN', 'SKIWAY'),
    ('SECOND', 'CHANCE'),
    ('RHUBARB', 'SKIWAY'),
    ('COYOTE', 'GLADE'),
    ("SOURDOUGH'S", 'SLIDE'),
    (('CABIN', (3599, 1991)), 'FEVER'),
    ('LOWER', 'STIRRUP'),
    (('LITTLE', (3868, 2346)), 'BRAVE'),
    ("PIECE O'", 'CAKE'),
    ('GALLAGHER', 'GLADE'),
    ('WAMPUM', 'SKIWAY'),
    ('BORDERS', 'SKIWAY'),
    ('ASPEN', 'ALLEY'),
    ('MYSTIC', 'ISLAND'),
    ('LUMBER', 'YARD'),
    ('EASY COME', 'EASY GO'),
    (('CENTENNIAL', (1588, 1418)), "(WILLY'S FACE("),
    (('SHEEPHORN', (1254, 943)), 'ESCAPE'),
]
JOIN_GAP = 9  # pt between the parts' glyph centres
TWO_LINE = {' '.join(t if isinstance(t, str) else t[0] for t in p) for p in JOIN}
# names printed beside their symbol, not in a gap of their line (crops p45.png, solit.png, stretch_all.png): no
# stretch along them (Leav the Beav: its lower label only; its upper is printed on its line)
NO_STRETCH = {'Maverick', 'Solitaire', 'Charter Skiway', 'Tall Timber', 'Roughlock', ('Leav the Beav', (2940, 3122))}
LABEL_LINE = set()
# the peaks' names, a building's (the children's ski school center)
DROP = [('MOUNT of the HOLY CROSS', None), ('MOUNT JACKSON', None), ('GOLD DUST PEAK', None),
        ('NEWYORK MOUNTA N', None), ("CHILDREN'S", None), ('SKI SCHOOL CENTER', None)]
# as the report spells them where it lists the run (its runs split into parts, printed as the map prints them: Upper
# Golden Eagle is the report's Golden Eagle - Upper); the rest as the map prints them, in their own case
RENAME = {
    'UPPER GOLDEN EAGLE': 'Golden Eagle - Upper', 'LOWER GOLDEN EAGLE': 'Golden Eagle - Lower',
    'UPPER GOSHAWK': 'Goshawk Upper', 'LOWER GOSHAWK': 'Goshawk Lower', 'GOSHAWK CONNECTOR': 'Goshawk Connector',
    'UPPER HARRIER': 'Harrier - Upper', 'LOWER HARRIER': 'Harrier - Lower', 'UPPER SHEEPHORN': 'Sheephorn - Upper',
    'ANDERSON ALLEY': "Anderson's Alley", 'BORDERS SKIWAY': 'Borders', 'CREEKSIDE SKIWAY': 'Creekside',
    'RHUBARB SKIWAY': 'Rhubarb', 'RIDGEPOINT SKIWAY': 'Ridgepoint', 'WAMPUM SKIWAY': 'Wampum',
    'SADDLERIDGE WAY': 'Saddleridge Skiway',
    'KESTREL': 'Kestrel', 'PEREGRINE': 'Peregrine', 'LARKSPUR': 'Larkspur', 'RAVEN RIDGE': 'Raven Ridge',
    'INTERTWINE': 'Intertwine', 'PRIMROSE': 'Primrose', 'CINCH': 'Cinch', 'DALLY': 'Dally',
    'LATIGO': 'Latigo', "GUNDER'S": "Gunder's", 'LITTLE BRAVE': 'Little Brave', 'CABIN FEVER': 'Cabin Fever',
    "PRESIDENT FORD'S": "President Ford's - Upper", 'STACKER': 'Stacker - Upper',
    'BEAVER CREEK MOUNTAIN EXPRESSWAY': 'Beaver Creek Mountain Expressway', 'UPPER STIRRUP': 'Upper Stirrup',
    'LOWER STIRRUP': 'Lower Stirrup', 'UPPER STONE CREEK CHUTES': 'Upper Stone Creek Chutes',
    'LOWER STONE CREEK CHUTES': 'Lower Stone Creek Chutes', 'BIG BARK': 'Big Bark', 'LITTLE BARK': 'Little Bark',
    'BORDERS-PINES - CHATEAU SKIWAY': 'Borders-Pines-Chateau Skiway', "SLANDEROUS SAM'S": "Slanderous Sam's",
    'TOMBSTONE TERRITORY': 'Tombstone Territory', 'BUCKAROO BOWL': 'Buckaroo Bowl', 'KELLER GLADE': 'Keller Glade',
    'ASPEN ALLEY': 'Aspen Alley', 'WEST FALL ROAD': 'West Fall Road',
}
# names printed some other way (map px): the Toyota Race Center's logo (its course, the red line beside it, is traced in
# decisions.py; no symbol is printed: the report's blue), and Dakota Skiway, which the 2025-26 image adds at Arrowhead
# (its name and circle, and its dotted line, traced)
# President Ford's and Stacker turn blue partway down (a square on each line under the Strawberry Park lift, no name):
# the report's - Lower, from the square
EXTRA = [('Toyota Race Center', 1428, 1745, 'square'), ('Dakota Skiway', 4225, 3064, 'circle'),
         ("President Ford's - Lower", 2221, 2287, 'square'), ('Stacker - Lower', 2281, 2264, 'square')]
# CENTENNIAL is printed three times, with a circle at the summit (the report's Hohum), a diamond above Spruce Saddle
# (Spruce Face) and a diamond above the base (Finish Face), and once as CENTENNIAL (WILLY'S FACE): four runs, as the
# report names them (its Flats, between Willy's Face and Finish Face, prints no name or symbol: left to Willy's Face,
# down to the next symbol)
RENAME_AT = [((1703, 628), 'CENTENNIAL', 'Centennial - Hohum'), ((1480, 937), 'CENTENNIAL', 'Centennial - Spruce Face'),
             ((1659, 2034), 'CENTENNIAL', 'Centennial - Finish Face')]
# the EX symbols (two diamonds holding E and X: extreme terrain, the Stone Creek Chutes): double black
SYMBOL_FIX = [((1267, 496), 'double-diamond'), ((825, 797), 'double-diamond')]
SYMBOL_ON_LINE = True  # each run's symbol is printed on its line (often partway along it), the name beside it
LOOSE_SYMBOLS = ''
# Wapiti prints a diamond by its name and a square on its line above and below it (where it eases): the report's black
RATING = {'Wapiti': 'diamond'}
# symbols printed by their name but nearer another's (crops wap.png, p104.png): Piece O' Cake's circle on its road,
# Wapiti's diamond at the top of its name (the squares on its line above and below are where it eases: the report's
# black); 4 Get About It's double diamond under its name
SYMBOL_OF = [((3865, 2435), "Piece O' Cake"), ((3969, 2379), 'Wapiti'), ((1301, 1760), '4 Get About It')]
DISPLAY = {}
# glades the names don't say (Corkscrew: a square and the glade icon, no line); the parks (the report's terrain parks,
# printed with no symbol: blue, the parks' default)
GLADES = {'Corkscrew', 'Three Tree Gully', 'Upper Stone Creek Chutes', 'Lower Stone Creek Chutes'}
PARKS = {'Lumber Yard', 'Park 101', 'Zoom Room'}
# names printed with no symbol: the parks blue; the kids' adventure zones the report lists blue (Big Bark/Little Bark,
# Sourdough's Slide), and so the one it doesn't list (Tombstone Territory); Slanderous Sam's has a circle on its line
DEFAULT_SYMBOL = {**{n: 'square' for n in PARKS}, 'Big Bark': 'square', 'Little Bark': 'square',
                  'Sourdough’s Slide': 'square', 'Tombstone Territory': 'square', "Slanderous Sam's": 'circle'}
NO_LINE = {}
