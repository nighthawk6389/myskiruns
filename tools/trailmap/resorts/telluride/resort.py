"""Telluride Ski Resort's trail map: the 2024-25 PDF (still the current one) of James Niehues's painting under strokes
and outlined names, and the resort's two inset images of the hike-to terrain the main map leaves out (Revelation Bowl,
Palmyra Peak and Black Iron Bowl). Read by tools/trailmap/pdf_resort.py, panel by panel (panels/<panel>/resort.py and
decisions.py, which take NAMES, AREA_OF and the rest from here); prepare.py extracts them."""
import json
import os
import re

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('main', 'Telluride'), ('revelation', 'Revelation Bowl'), ('black-iron-bowl', 'Palmyra & Black Iron')]

# the trail report (report.json: the resort's snow report plugin's scrape page in Common Crawl's capture of
# 2026-02-12), every run under the lift the page lists it by; the carpets are no runs
REPORT = [t for t in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
          if 'Carpet' not in t[0]]
# the report's lifts (its hike-to terrain listed apart), each with its lift's top (the 2017 Master Development Plan,
# Table IV-1; Lift 7 is the Coonskin lift) or, for the hike-to terrain, the highest point printed for it (Palmyra
# Peak 13,150 ft on the main map; Gold Hill's and Revelation's hike-to terrain from their lifts' tops)
AREAS = [('chondola', 'Chondola', 9555), ('village-express', 'Village Express', 10770),
         ('polar-queen-express', 'Polar Queen Express', 11195), ('apex-lift', 'Apex Lift', 11969),
         ('lift-7', 'Lift 7', 10570), ('oak-street-lift', 'Oak Street Lift', 9805),
         ('plunge-lift', 'Plunge Lift', 11910), ('sunshine-express', 'Sunshine Express', 10905),
         ('ute-park', 'Ute Park', 11152), ('prospect-express', 'Prospect Express', 11815),
         ('prospect-hike-to', 'Prospect Express (Hike-To Terrain)', 13150),
         ('gold-hill-express', 'Gold Hill Express', 12255),
         ('gold-hill-hike-to', 'Gold Hill Express (Hike-To Terrain)', 12255),
         ('revelation-lift', 'Revelation Lift', 12515),
         ('revelation-hike-to', 'Revelation Lift (Hike-To Terrain)', 12515)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}
_AREA_ID['UTE Park'] = 'ute-park'


def key(name):
    """A name with case, spaces and punctuation left out (pdf_resort.py's spelling_key)."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


# the report's parts of one run the map prints as one (one line, the name printed once or twice with the same
# symbols): one trail, named as the run
ONE_RUN = {
    'Galloping Goose – Upper': 'Galloping Goose', 'Galloping Goose – Lower': 'Galloping Goose',
    'Lower Galloping Goose (Upper)': 'Lower Galloping Goose', 'Lower Galloping Goose (Middle)': 'Lower Galloping Goose',
    'Lower Galloping Goose (Lower)': 'Lower Galloping Goose',
    'Double Cabin (Upper)': 'Double Cabin', 'Double Cabin (Lower)': 'Double Cabin',
    'Misty Maiden – Upper': 'Misty Maiden', 'Misty Maiden – Middle': 'Misty Maiden', 'Misty Maiden – Lower': 'Misty Maiden',
    'Boomerang – Upper': 'Boomerang', 'Boomerang – Middle': 'Boomerang',
    'Cake Walk – Upper': 'Cake Walk', 'Cake Walk – Lower': 'Cake Walk',
    'Cimarron – Upper': 'Cimarron', 'Cimarron – Middle': 'Cimarron',
    'Telluride Trail – Upper (above Easy Out)': 'Telluride Trail', 'Telluride Trail – Lower (below Easy Out)': 'Telluride Trail',
    'Bushwacker – Upper': 'Bushwacker', 'Bushwacker – Lower': 'Bushwacker',
    'Mine Shaft (below Bail Out)': 'Mine Shaft',
    'See Forever (Lift 14 to Lift 6)': 'See Forever', 'See Forever (Lift 6 to Lift 7)': 'See Forever',
    'See Forever – Upper': 'See Forever',
    'Hoot Brown Terrain Park – Upper': 'Hoot Brown Terrain Park', 'Hoot Brown Terrain Park – Lower': 'Hoot Brown Terrain Park',
}
# runs the insets print that the report doesn't list, with their areas
NOT_IN_REPORT = {'Capitol': 'prospect-hike-to', 'Golden Cross': 'revelation-lift'}
NAMES = sorted({ONE_RUN.get(n, n) for n, *_r in REPORT} | set(NOT_IN_REPORT))
AS_PRINTED = False
AREA_OF = dict(NOT_IN_REPORT)
for _n, _a, *_r in REPORT:
    AREA_OF.setdefault(ONE_RUN.get(_n, _n), _AREA_ID[_a])
# printed as the map names them, spelled as the report does (NAMES spells the rest by their letters)
RENAME = {"O'REILLY'S": 'O’Riley’s', 'LOWER PLUNGE': 'Plunge – Lower', 'LOWER LOOKOUT': 'Lookout – Lower',
          'LOOKOUT': 'Lookout – Upper', "LOWER WOOZLEY'S WAY": 'Woozley’s Way – Lower',
          'LOWER VILLAGE BYPASS': 'Village Bypass – Lower', 'LOWER BOOMERANG': 'Boomerang – Lower',
          'ZIPPER ROCK': 'Zipper'}
# the report's spellings, with straight apostrophes
DISPLAY = {n: n.replace('’', "'").replace('‘', "'") for n in NAMES if '’' in n or '‘' in n}
PARKS = {'Hoot Brown Terrain Park', 'UTE Park', 'Beginner Park'}


def is_name(label):
    return True


def spelled(n):
    """A printed name as the report spells it (RENAME, else NAMES by its letters)."""
    n = RENAME.get(n, n)
    return {key(m): m for m in NAMES}.get(key(n), n)
