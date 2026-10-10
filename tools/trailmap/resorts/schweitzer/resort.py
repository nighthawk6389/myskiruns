"""Schweitzer's 2025-26 trail maps (schweitzer.com's maps page: images only, James Niehues's paintings): Schweitzer
Bowl, the front side, and Outback Bowl, the back side, as two panels. The runs are painted slopes with their names
printed along them and the symbol by the name; only the cat tracks are drawn as lines (navy). The resort's
interactive maps (resorts-interactive.com maps 1826 and 1827) draw the same paintings with every name's letters and
most symbols in a group named after the run, and the front's cat tracks: prepare.py puts them on the prints, and
names.py holds what they lack, read on crops. Read by tools/trailmap/pdf_resort.py, panel by panel
(panels/<panel>/resort.py and decisions.py, which take NAMES, AREA_OF and the rest from here)."""
import json
import os
import re

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('schweitzer-bowl', 'Schweitzer Bowl'), ('outback-bowl', 'Outback Bowl')]
# the report's two areas (the bowls), each with the summit's elevation as printed (6,389 ft, the top of the Lakeview
# Triple, which both bowls share)
AREAS = [('schweitzer-bowl', 'Schweitzer Bowl', 6389), ('outback-bowl', 'Outback Bowl', 6389)]

# the resort's trail report (report.json: the mtnpowder feed, every run with its bowl and rating); the cross-country
# trails are no runs of these maps
REPORT = [t for t in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
          if t[1] != 'Cross Country Trails']
NAMES = sorted({n for n, _a, _r in REPORT})
AS_PRINTED = True  # names are shown as the report spells them (the interactive maps' groups spell them so too)
_AREA_ID = {'Schweitzer Bowl': 'schweitzer-bowl', 'Outback Bowl': 'outback-bowl'}
AREA_OF = {}
for _n, _a, _r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])


def key(name):
    """A name with case, spaces and punctuation left out (pdf_resort.py's spelling_key)."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


def area_of_panel(panel):
    def area(c):
        return panel
    return area


def is_name(label):
    return True


# the rating is the symbol printed by the name, else the interactive map's (its group's rating)
COLOR_SYMBOL = {'green': 'circle', 'blue': 'square', 'black': 'diamond', 'double-black': 'double-diamond'}
DISPLAY = {}
# the terrain parks (the report's, and SOUTHSIDE PARK, printed on an orange pill and not on the report): blue, the
# parks' default (no symbol is printed by them)
PARKS = {n for n, _a, r in REPORT if r == 'TerrainPark'} | {'Southside Park'}
DEFAULT_SYMBOL = {n: 'square' for n in PARKS}
