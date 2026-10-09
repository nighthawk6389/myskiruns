"""Mammoth Mountain's 2025-26 trail map (skimap.org 42347: the resort's PDF; page 2 is the map): the whole mountain,
and in its lower right corner an inset of the back side (Chairs 13 and 14). Its names are text and its symbols
fills, over a painting with no trail lines drawn: the lines are the resort's interactive maps'
(resorts-interactive.com maps 1812 and 1819). Read by tools/trailmap/pdf_resort.py, panel by panel
(panels/<panel>/resort.py and decisions.py, which take NAMES, AREA_OF and the rest from here); prepare.py extracts
them."""
import json
import os

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('main', 'Whole mountain'), ('back-side', 'Back Side')]
# the report's areas, its three base lodges, each with its elevation as the map prints it
AREAS = [('main-lodge', 'Main Lodge', 8909), ('canyon-lodge', 'Canyon Lodge', 8343),
         ('eagle-lodge', 'Eagle Lodge', 7953)]

# the resort's trail report (report.json: the mtnpowder feed, every run with its lodge and rating). Its uphill
# routes (skinning routes up the runs, white names on the map) are no runs
REPORT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
REPORT = [t for t in REPORT if t[2] != 'UphillArrow']
NAMES = sorted({n for n, _a, _r in REPORT})
AS_PRINTED = True  # names are shown as the report spells them
_AREA_ID = {'Main Lodge': 'main-lodge', 'Canyon Lodge': 'canyon-lodge', 'Canyon': 'canyon-lodge',
            'Eagle Lodge': 'eagle-lodge'}
AREA_OF = {n: _AREA_ID[a] for n, a, _r in REPORT}


# Lower Shaft, printed under Shaft with its own diamond (Shaft's is double), is a run the interactive map lists and the
# report does not: Canyon Lodge's, as Shaft is
AREA_OF['Lower Shaft'] = 'canyon-lodge'


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


def is_name(label):
    return True  # prepare.py keeps the names' font and colour only


# names drawn as outlined glyphs, not text (prepare.py): the first glyph's drawing order on the page -> the name, as
# read on a crop (work/mammoth glyph runs: every other run of outlined glyphs is the ski area boundary's or a
# notice's)
OUTLINED = {1443: 'LOWER ROAD RUNNER', 1545: 'ANTIN ALLEY / CHICKADEE'}
# the interactive maps' group names the report spells otherwise; LOWER SHAFT, in no group, as a name
RENAME = {'LOWER SHAFT': 'Lower Shaft', 'Arriba Lower': 'Arriba (Lower)', 'Arriba Upper': 'Arriba (Upper)', 'Starr Chute': 'Starr Chutes',
          'White Bark Ridge': 'Whitebark Ridge'}
# the terrain parks and halfpipes (the report's), and the Hemlocks' terrain features
PARKS = {n for n, _a, r in REPORT if r in ('TerrainPark', 'Halfpipe')}
# the adventure zones (the report's PurpleStar: tree runs with jumps for children, a purple star on the map): green,
# as the report has no rating for them
DEFAULT_SYMBOL = {n: 'circle' for n, _a, r in REPORT if r == 'PurpleStar'}
