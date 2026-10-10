"""Big Bear Mountain Resort's 2025-26 trail maps (bigbearmountainresort.com's trail-maps page: images only, James
Niehues's paintings): Snow Summit, Bear Mountain and Snow Valley, one panel each. Snow Summit's print draws each run's
line (blue, black, green); Bear Mountain's and Snow Valley's paint the runs as slopes, with a name and a symbol and no
line. The resort's interactive maps (resorts-interactive.com maps 1818, 1808 and 1825) draw the same paintings with
each run's symbols and a line in a group named after the run: the symbols are the prints' own, the lines an older
drawing (Snow Summit's lie up to 25 px off its print's). prepare.py puts them on the prints; names.py holds what they
lack, read on crops. Read by tools/trailmap/pdf_resort.py, panel by panel (panels/<panel>/resort.py and decisions.py,
which take NAMES, AREA_OF and the rest from here)."""
import json
import os
import re

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('snow-summit', 'Snow Summit'), ('bear-mountain', 'Bear Mountain'), ('snow-valley', 'Snow Valley')]
# the report's areas (the three mountains), each with its summit's elevation as printed
AREAS = [('snow-summit', 'Snow Summit', 8200), ('bear-mountain', 'Bear Mountain', 8805),
         ('snow-valley', 'Snow Valley', 7841)]

# the resort's trail report (report.json: the mtnpowder feed, every run with its mountain and rating)
REPORT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
NAMES = sorted({n for n, _a, _r in REPORT})
AS_PRINTED = True  # names are shown as the report spells them (the interactive maps' groups spell them so too)
_AREA_ID = {name: aid for aid, name, _e in AREAS}
AREA_OF = {}
for _n, _a, _r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])
# Bear Mountain and Snow Valley each have a Pipeline (blue and black): two trails, renamed apart on their panels and
# shown alike
AREA_OF.update({'Pipeline (Bear Mountain)': 'bear-mountain', 'Pipeline (Snow Valley)': 'snow-valley'})


def key(name):
    """A name with case, spaces and punctuation left out (pdf_resort.py's spelling_key)."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


def area_of_panel(panel):
    def area(c):
        return panel  # (each panel is one of the report's areas)
    return area


def is_name(label):
    return True


DISPLAY = {'Pipeline (Bear Mountain)': 'Pipeline', 'Pipeline (Snow Valley)': 'Pipeline'}
# the terrain parks and pipes (the report's Halfpipe rows, and the parks printed on orange pills): blue, the parks'
# default where no symbol is printed by them
PARKS = {n for n, _a, r in REPORT if r == 'Halfpipe'}
DEFAULT_SYMBOL = {n: 'square' for n in PARKS}
