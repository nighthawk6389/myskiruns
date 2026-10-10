"""Snowbasin's 2025-26 trail map (snowbasin.com, its trail-maps page: "Winter Trail Map 2025-26 (22.5in x 12in) for
Ikon, reduced", one InDesign page; skimap.org's map 34864 is the same file): James Niehues's painting under vector
lines, 2.25 pt strokes in the three trail colours; names are text in the run's colour printed along its line, the
symbols set on the line. Read by tools/trailmap/pdf_resort.py; prepare.py extracts it."""
import json
import os

CLIP = (0, 0, 1478, 864)  # PDF points: the page left of the legend
SCALE = 3  # map px per PDF point
SOURCE = ('Snowbasin 2025-26 trail map PDF (snowbasin.com): 2.25 pt black, blue and green strokes, '
          'tools/trailmap/resorts/snowbasin/prepare.py; percent of the map image')
SYMBOL_REACH = 14  # pt from a name's first or last character to its symbol (on the line, past the name)
END_REACH = 6  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 6  # pt: a name printed beside its line, about a character's height off it
ALONG_NEAREST = True
ALONG_FIRST = True  # names are printed along their own line: that line is the name's
NO_STRETCH_BESIDE = True

# the trail report's lift areas (report.json), each with the highest elevation printed where its lifts top out:
# Strawberry's DeMoisy Peak, the Needles (the Needles Gondola; the Porcupine lift, which the report lists apart,
# tops out below them and prints none), and Allen Peak (the tram, John Paul's)
AREAS = [('strawberry', 'Strawberry', 9370), ('needles', 'Needles', 9010), ('john-paul', 'John Paul', 9465)]
_AREA_ID = {'Strawberry': 'strawberry', 'Needles': 'needles', 'Porcupine': 'needles', 'John Paul': 'john-paul',
            'Terrain Parks': 'needles'}

# the resort's trail report (report.json: the mountain report's tables, every run with its lift area and rating)
REPORT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
NAMES = sorted({n for n, _a, _r in REPORT})
AS_PRINTED = True  # names are shown as the report spells them, the others as printed
AREA_OF = {n: _AREA_ID[a] for n, a, _r in REPORT}
# names the report doesn't list
AREA_OF.update({'Trapper’s Bypass': 'strawberry', 'Eas-A-Long': 'needles', 'Catastrophe Rocks!': 'needles',
                'Porky Cirque': 'needles', 'Blue Grouse': 'needles', 'Dry Bowl': 'john-paul',
                'Staircase': 'john-paul', 'Pig Pen': 'john-paul'})


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


def is_name(label):
    return label['color'] in ('green', 'blue', 'black')  # prepare.py keeps the trail-name text only


# the rating is the symbol on the line by the name, else the name's colour (black: a diamond or two)
COLOR_SYMBOL = {'green': 'circle', 'blue': 'square', 'black': 'diamond'}
# names printed in parts (on two lines: the bowls), in reading order
JOIN = [('Sister’s', 'Bowl'), ('Middle Bowl', 'Cirque'), ('Needles', 'Cirque'), ('Porky', 'Cirque'),
        ('Mt. Ogden', 'Bowl'), ('Lower', 'Pyramids')]
TWO_LINE = {' '.join(p) for p in JOIN}
JOIN_GAP = 17  # pt: the bowls' two lines, about 15 pt apart
# two names printed as one text object, each along its own line
SPLIT = {'RockyJ Pineview': ('RockyJ', 'Pineview'), 'Dogleg Sunshine': ('Dogleg', 'Sunshine')}
NO_STRETCH = {'Trapper’s Bypass'}  # printed beside its line, a label's height off it
LABEL_LINE = set()
# the summits and their elevations; a copy of Twist & Shout with its T drawn apart (in red)
DROP = [(t, None) for t in ('STRAWBERRY PEAK', '9265’', 'DEMOISY PEAK', '9370’', 'NEEDLES', '9010’', 'MT. OGDEN',
                            '9570’', 'ALLEN PEAK', '9465’', 'NO NAME', '9070’', 'wist & Shout')]
# as the trail report names them (NAMES spells the rest by their letters): LMM is Lower Moose Mound
RENAME = {'LMM': 'Lower Moose Mound', 'Rainer’s': "Rainer's Run", 'Needles Run': 'Needles',
          'Lower Pyramids': 'Lower Pyramid'}
# the LITTLECAT on the orange pill by the Littlecat lift's foot is the report's terrain park; the other, along the
# green line, the run
RENAME_AT = [((3171, 2238), 'Littlecat', 'Littlecat Terrain Park')]
EXTRA = []
SYMBOL_FIX = []
# symbols printed beside their names but out of reach: the bowls' double diamonds under their names, The Flank's at
# its line's top above its name; and Bullwinkle's square at its name's foot, where Rocky J's diamond, on Rocky J's
# line beside it, is nearer Bullwinkle's last letter
SYMBOL_OF = [((766, 605), "Sister's Bowl"), ((1784, 412), 'Middle Bowl Cirque'), ((3393, 631), 'Mt. Ogden Bowl'),
             ((3951, 1803), 'Lower Pyramid'), ((2884, 581), 'The Flank'), ((2011, 1199), 'Bullwinkle'),
             ((1988, 1167), 'Rocky J')]
# what the two double diamonds with no name, on no line, are: the restricted expert terrain above Strawberry Fields
# and The Walrus, and between Lone Tree's top and Middle Bowl Cirque
LOOSE_SYMBOLS = 'double diamonds marking restricted expert terrain (hatched) with no name'
# NEEDLES CIRQUE is printed with no symbol, in black (one diamond or two on this map): the report's Most Difficult
RATING = {'Needles Cirque': 'double-diamond'}
DISPLAY = {}
GLADES = set()
# the orange pills: the report's two parks, and Blue Grouse (printed, not on the report)
PARKS = {'Littlecat Terrain Park', "Orson's", 'Blue Grouse'}
NO_LINE = {}
