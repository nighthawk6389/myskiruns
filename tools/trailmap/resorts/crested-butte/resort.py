"""Crested Butte Mountain Resort's 2025-26 trail map: one page of the PDF (James Niehues's painting under a vector
layer of outlined lines and names), with the Teocalli Bowls inset on its own panel. Read by
tools/trailmap/pdf_resort.py, panel by panel (panels/<panel>/resort.py and decisions.py, which take NAMES, AREA_OF
and the rest from here); prepare.py extracts them."""
import json
import os
import re

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('main', 'Crested Butte'), ('teocalli-bowls', 'Teocalli Bowls')]

# the trail report (report.json: the terrain feed of skicb.com's lift-and-terrain-status page, as Common Crawl
# captured it on 2026-02-12); the three beginner areas at the conveyors are no runs
REPORT = [t for t in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
          if not t[0].startswith('Beginner Area')]
# the report's areas, each with the top of its highest lift (lift_tops.py: OpenStreetMap's lift lines and the USGS's
# 10 m elevation model; the resort publishes none): Front Side the Silver Queen Express, Back Side the Paradise
# Express, North Face the North Face lift, Ten Peaks the Prospect lift, the Learning Area the Peachtree lift; High
# Lift's terrain runs from the summit, printed on the map (12,162 ft)
AREAS = [('front-side', 'Front Side', 11460), ('back-side', 'Back Side', 11148), ('north-face', 'North Face', 11416),
         ('high-lift', 'High Lift', 12162), ('ten-peaks', 'Ten Peaks', 10173),
         ('learning-area', 'Learning Area', 9485)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}


def key(name):
    """A name with case, spaces and punctuation left out (pdf_resort.py's spelling_key)."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


# runs the map prints that the report doesn't list, with their areas
NOT_IN_REPORT = {'Lower Crystal': 'front-side', 'Middle Championship': 'front-side'}
NAMES = sorted({n for n, *_r in REPORT} | set(NOT_IN_REPORT))
AS_PRINTED = False
AREA_OF = dict(NOT_IN_REPORT)
for _n, _a, *_r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])
# printed as the map names them, spelled as the report does (NAMES spells the rest by their letters)
RENAME = {}
DISPLAY = {}
PARKS = {'Lower Twister Terrain Park', 'Painter Boy Park'}


def is_name(label):
    """The runs' names: in their colours (blue, green, black); not the lifts', the title's or the conveyors' (a
    second black)."""
    return label['color'] != 'dark'


def spelled(n):
    """A printed name as the report spells it (RENAME, else NAMES by its letters)."""
    n = RENAME.get(n, n)
    return {key(m): m for m in NAMES}.get(key(n), n)
