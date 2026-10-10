"""Snowbird's 2025-26 trail map (snowbird.com's winter trail map page: one 1920x2318 JPEG, James Niehues's painting,
the front side and Mineral Basin; no vector PDF, no interactive map). names.py is the map read on zoomed crops: each
name with its label and its run's line as points, which prepare.py routes along the painted line. Read by
tools/trailmap/pdf_resort.py."""
import json
import os
import re

CLIP = (0, 0, 1920, 2318)  # the whole image, in px: the map's units are its pixels
SCALE = 1
SOURCE = ('Snowbird trail map 2025-26 (snowbird.com, JPEG): the lines read on crops and routed along the painted ones, '
          'tools/trailmap/resorts/snowbird/prepare.py; percent of the map image')
GROUPED = True  # every line piece carries its trail's name (names.py)
MATCH_ENDS = False
SYMBOL_REACH = 0
END_REACH = 0  # the pieces are named by names.py, not by where they end
ALONG = 0

# the trail report's sectors, each with its top's elevation as printed (Hidden Peak's for the two it serves, the Gad 2
# touring gate's for Gad Valley)
AREAS = [('gad-valley', 'Gad Valley', 9840), ('peruvian-gulch', 'Peruvian Gulch', 11000),
         ('mineral-basin', 'Mineral Basin', 11000)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}

# the trail report (report.json: the DOR trail list snowbird.com's lift and trail report loads): names, sectors, ratings
REPORT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
NAMES = sorted({n for n, _a, _r in REPORT})
AS_PRINTED = True  # names.py names each run as the report spells it (the others as printed)
AREA_OF = {n: _AREA_ID[a] for n, a, _r in REPORT}


def key(name):
    """A name with case, spaces and punctuation left out (pdf_resort.py's spelling_key)."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


def area(c):
    """For a name the report doesn't list: Mineral Basin below the front side's view (y 1504), Peruvian Gulch west of
    the Peruvian lift's line, else Gad Valley."""
    x, y = c
    if y > 1504:
        return 'mineral-basin'
    return 'peruvian-gulch' if x < 700 else 'gad-valley'


def is_name(label):
    return True


# the rating is the name's colour and the symbol printed on its line: names.py's 'expert' where it is a double diamond
COLOR_SYMBOL = {'green': 'circle', 'blue': 'square', 'black': 'diamond', 'expert': 'double-diamond'}
RATING = {}
JOIN = []
TWO_LINE = set()
LABEL_LINE = {"Chip's Access"}  # (its label printed along the cased way from the tram, no line of its own read)
NO_STRETCH = set()
DROP = []
RENAME = {}
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = {}
GLADES = set()
PARKS = set()
DEFAULT_SYMBOL = {}
NO_LINE = {}
