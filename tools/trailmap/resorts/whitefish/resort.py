"""Whitefish Mountain Resort's trail maps (skiwhitefish.com, its trail-maps page: web JPEGs only, James Niehues's
paintings): the 2025-26 front side, and the 2024-25 North Side and Hellroaring Basin insets it still links. No PDF and
no interactive map: names.py is the map read on zoomed crops (each name, its label, its symbol, its run's line as
rough points), prepare.py snaps the lines onto the painted ones. Read by tools/trailmap/pdf_resort.py, panel by
panel (panels/<panel>/resort.py and decisions.py, which take NAMES, AREA_OF and the rest from here)."""
import json
import os
import re

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('front-side', 'Front Side'), ('north-side', 'North Side'), ('hellroaring', 'Hellroaring Basin')]
# the map's sides, each with the summit's elevation as printed (6,817 ft: the three share the summit)
AREAS = [('front-side', 'Front Side', 6817), ('north-side', 'North Side', 6817),
         ('hellroaring', 'Hellroaring Basin', 6817)]
# the trail report (report.json: the snow report page's runs, by lift): each lift's side
_SIDE = {'Chair 7 - Big Creek Express': 'north-side', 'Chair 11 - Flower Point': 'north-side',
         'Bigfoot T-Bar 2': 'north-side', 'Chair 8 - Hellroaring': 'hellroaring'}
REPORT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
NAMES = sorted({n for n, _l, _r in REPORT})
AS_PRINTED = True  # names are shown as the report spells them, the others as printed
AREA_OF = {n: _SIDE.get(lift, 'front-side') for n, lift, _r in REPORT}


def key(name):
    """A name with case, spaces and punctuation left out (pdf_resort.py's spelling_key)."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


def area_of_panel(panel):
    def area(c):
        return panel
    return area


def is_name(label):
    return True


# the rating is the symbol printed by the name (names.py)
COLOR_SYMBOL = {}
JOIN = []
TWO_LINE = set()
SPLIT = {}
# as the report names them (NAMES spells the rest by their letters): the carpets' and parks' areas, BENCH RUN
RENAME = {'2 Easy Carpet': '2 Easy Carpet Area', 'Big Easy Carpet': 'Big Easy Carpet Area',
          '2nd Street': '2nd Street Park', 'The Depot': 'Depot Terrain Park', 'Bench Run': 'Bench Runs'}
# Minnow Park, printed with no symbol (by its XS pill): green, as the report rates it
RATING = {'Minnow Park': 'circle'}
DISPLAY = {}
GLADES = set()
PARKS = set()
