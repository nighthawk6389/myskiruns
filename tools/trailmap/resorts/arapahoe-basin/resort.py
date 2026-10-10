"""Arapahoe Basin's 2025-26 winter trail map (arapahoebasin.com's trail-maps page: "a basin map 2025.pdf", one page,
VistaMap's artwork): two paintings under one vector layer, the Frontside & The Beavers and, framed at the top right,
Zuma Bowl. Runs' lines thin strokes in the three trail colours where the map draws one (the groomed and gladed runs,
the traverses); the open faces, bowls and chutes a name and a symbol with no line. Names outlined near-black glyphs
along their run, the symbol by the name. Read by tools/trailmap/pdf_resort.py, panel by panel (panels/<panel>/
resort.py and decisions.py, which take NAMES, AREA_OF and the rest from here); prepare.py extracts them."""
import json
import os

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('frontside', 'Frontside & The Beavers'), ('zuma-bowl', 'Zuma Bowl')]
# the trail report's terrain areas, each with the top of its lift (the 2025 Master Development Plan's Table 1: Lenawee
# Express 12,465 ft, Pallavicini 12,115, Beavers 12,458, Zuma 12,475, Molly Hogan 10,870; the Steep Gullies are
# reached from Pallavicini's top) or, for the East Wall, the summit printed on the map (Arapahoe Basin, 13,050 ft)
AREAS = [('front-side', 'Front Side', 12465), ('pallavicini', 'Pallavicini', 12115),
         ('the-beavers', 'The Beavers', 12458), ('montezuma-bowl', 'Montezuma Bowl', 12475),
         ('steep-gullies', 'Steep Gullies', 12115), ('east-wall', 'East Wall', 13050),
         ('molly-hogan', 'Molly Hogan', 10870)]
_AREA_ID = {'Front Side Terrain': 'front-side', 'Pallavicini': 'pallavicini', 'The Beavers': 'the-beavers',
            'Montezuma Bowl': 'montezuma-bowl', 'Steep Gullies': 'steep-gullies', 'East Wall': 'east-wall',
            'Molly Hogan': 'molly-hogan'}
# the trail report (report.json: the snow report page's Terrain & Lift Status, every run under its terrain area); its
# carpet and uphill-access rows are no runs
REPORT = [t for t in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
          if not t[0].startswith(('Uphill Access', "Molly's Magic Carpet"))]
# the runs the map prints that the report doesn't list, in its spelling (the map prints capitals), with their areas
NOT_IN_REPORT = {'The Landing Strip': 'front-side', 'Cabin Glades': 'front-side', 'Pallavicini': 'pallavicini',
                 'Pali Cornice': 'pallavicini', 'Lower East Wall': 'east-wall', 'East Wall Traverse': 'east-wall',
                 "Elephant's Trunk": 'montezuma-bowl'}
NAMES = sorted({n for n, *_r in REPORT} | set(NOT_IN_REPORT))
AS_PRINTED = False
AREA_OF = dict(NOT_IN_REPORT)
for _n, _a, *_r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])
# as the trail report names them (NAMES spells the rest by their letters)
RENAME = {"DAVID'S RUN": "1st Alley - David's Run", '4th ALLEY': '4th Alley (West Alley)', 'TBGLADE': 'TB Glades',
          'DAVOS GLADE': "Davo's Glade"}
DISPLAY = {}


def is_name(label):
    return True
