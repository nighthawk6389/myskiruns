"""Snowmass's 2025-26 trail map (aspensnowmass.com, its trail-map page: one Illustrator page, "layered"): the whole
mountain, and at the top an inset of Hanging Valley drawn larger. Trail lines are vectors over a 100 dpi painting:
blue, black and green strokes, and the expert runs a black line in a yellow casing; names are white text on a pill
in the run's colour, set on the run's line. Read by tools/trailmap/pdf_resort.py, panel by panel
(panels/<panel>/resort.py and decisions.py, which take NAMES, AREA_OF and the rest from here); prepare.py extracts
them."""
import json
import os
import re

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('main', 'Whole mountain'), ('hanging-valley', 'Hanging Valley')]
# the printed summits, each with its elevation as printed: the trail report's lift areas go with the summit their
# runs come down from (below)
AREAS = [('cirque', 'Cirque', 12510), ('high-alpine', 'High Alpine', 11880), ('big-burn', 'Big Burn', 11835),
         ('elk-camp', 'Elk Camp', 11325), ('sams-knob', "Sam's Knob", 10630)]
_AREA_ID = {'Cirque': 'cirque', 'Hanging Valley': 'high-alpine', 'High Alpine': 'high-alpine',
            'Alpine Springs': 'high-alpine', 'Big Burn': 'big-burn', 'Coney Express': 'big-burn',
            'Elk Camp': 'elk-camp', 'Two Creeks': 'elk-camp', "Sam's Knob": 'sams-knob', 'Campground': 'sams-knob'}

# the resort's trail report (report.json: its grooming feed, every trail with its lift area and rating); its uphill
# routes are no runs
REPORT = [t for t in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
          if t[1] != 'Uphill Routes']
# runs the report splits into (Upper) and (Lower) are printed as one name, once or several times along the run: one
# trail each; but Green Cabin and Banzai, printed apart (UPPER GREEN CABIN and GREEN CABIN; LOWER BANZAI)
KEEP_PARTS = ('Green Cabin', 'Banzai')


def _base(name):
    if name.startswith(KEEP_PARTS):
        return name
    return re.sub(r'\s*\((?:Upper|Lower)\)$', '', name)


NAMES = sorted({_base(n) for n, _a, _r in REPORT})
AS_PRINTED = True  # names are shown as the report spells them
# each name's area: its lift area's summit (a run whose parts are in two areas goes with its upper part's)
AREA_OF = {}
for _n, _a, _r in sorted(REPORT, key=lambda t: '(Lower)' in t[0]):
    if _a in _AREA_ID:
        AREA_OF.setdefault(_base(_n), _AREA_ID[_a])
# the names the inset prints and the report doesn't list (Hanging Valley's runs, from High Alpine)
AREA_OF.update({n: 'high-alpine' for n in (
    'Upper Ladder', 'Valley Valley', 'Wall One', 'Wall Two', 'Strawberry Patch', "Cassidy's", 'Union', "Willy's",
    'Glade One', 'Glade Two', 'Glade Three', 'Waters', 'Weird Woods', 'Frog Pond Glades', 'Hanging Valley Glades',
    'Hanging Valley Headwall')})
# the runs printed in the Burnt Mountain glades, off Elk Camp (the report's Burnt Mountain Glades)
AREA_OF.update({n: 'elk-camp' for n in ('Rio', 'A-Line', 'Split Tree')})
AREA_OF['Bridges'] = 'elk-camp'  # by Assay Hill, at the base


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


def is_name(label):
    return True  # prepare.py keeps the names (white text on a green, blue or black pill) only


# the rating is the pill's colour (prepare.py: an expert run's black name on a yellow-cased line, or by a double
# diamond or an EX mark, is "expert")
COLOR_SYMBOL = {'green': 'circle', 'blue': 'square', 'black': 'diamond', 'expert': 'double-diamond'}
# names printed in parts (two or three lines), in reading order
JOIN = [('JACK OF', 'HEARTS'), ('COYOTE', 'HOLLOW'), ('BUCKSKIN', 'CLIFFS'), ('GARRETT', 'GULCH'),
        ('WEST', 'GARRETT'), ('FREE FALL', 'GLADES'), ('SNEAKY’S', 'GLADES'), ('POWERLINE', 'GLADES'),
        ('HANGING', 'VALLEY', 'GLADES'), ('FROG POND', 'GLADES'), ('CIRQUE', 'HEADWALL'),
        ('CIRQUE', 'CORNICE GATE'), ('CIRQUE', 'CORNICE'), ('HANG ON', 'HALVIN’S'), ('ROCK BAND', 'CHUTE'),
        ('WEIRD', 'WOODS'), ('HANGING', 'VALLEY')]
JOIN_GAP = 9
TWO_LINE = {' '.join(p) for p in JOIN} - {'CIRQUE CORNICE'}  # (Cirque Cornice: two words on one line)
# two names drawn as one text object, each on its own pill (prepare.py splits them before it reads the pills)
SPLIT = {'BEAR BOTTOM GUNNER’S VIEW': ['BEAR BOTTOM', 'GUNNER’S VIEW'],
         'UTE CHUTE FAST DRAW': ['UTE CHUTE', 'FAST DRAW'], 'AMF GOWDY’S': ['AMF', 'GOWDY’S']}
# the area names in a black pill (Hanging Valley's, The Cirque's) and Spider Sabich's picnic and race area: no runs
# and the Cirque Cornice gate's sign
DROP = [('HANGING VALLEY', None), ('THE CIRQUE', None), ('SPIDER SABICH', None), ('PICNIC/RACE AREA', None),
        ('CIRQUE CORNICE GATE', None)]
# as the report names them (NAMES spells the rest by their letters), or the map's own name where the report
# abbreviates it
RENAME = {'CAMP 3': 'Camp Three', 'WEST I & II': 'West 1 & 2', 'SUNKISS': 'Sunkiss Glades',
          'ROCKY MTN HIGH': 'Rocky Mountain High', 'POWERLINE GLADES': 'Powerline',
          'UPPER GREEN CABIN': 'Green Cabin (Upper)', 'GREEN CABIN': 'Green Cabin (Lower)',
          'LOWER BANZAI': 'Banzai (Lower)', 'HANGING VALLEY GLADES': 'Hanging Valley Glades',
          'WEIRD WOODS': 'Weird Woods'}
# the names the report doesn't list, as printed in title case (Hanging Valley's in the inset; the Burnt Mountain
# glades' runs)
RENAME.update({t: t.title().replace('’S', "'s").replace("'S", "'s") for t in (
    'UPPER LADDER', 'VALLEY VALLEY', 'WALL ONE', 'WALL TWO', 'STRAWBERRY PATCH', 'CASSIDY’S', "CASSIDY'S", 'UNION',
    'WILLY’S', "WILLY'S", 'GLADE ONE', 'GLADE TWO', 'GLADE THREE', 'WATERS', 'FROG POND GLADES', 'RIO', 'A-LINE',
    'SPLIT TREE', 'BRIDGES')})
DISPLAY = {}
# glades the report names without the word (POWERLINE GLADES is its Powerline)
GLADES = {'Powerline'}
# the terrain parks and pipes (the report's)
PARKS = {n for n, _a, r in REPORT if r == 'TerrainPark'}
