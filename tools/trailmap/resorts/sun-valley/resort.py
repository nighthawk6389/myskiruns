"""Sun Valley's 2026-27 trail maps (sunvalley.com's trail-maps page): Bald Mountain and Dollar Mountain, each an image
only, with the 2023-24 vector exports of both artworks (skimap.org) registered on them for the lines, names and
symbols. Read by tools/trailmap/pdf_resort.py, panel by panel (panels/<panel>/resort.py and decisions.py, which take
NAMES, AREA_OF and the rest from here); prepare.py extracts them."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('bald-mountain', 'Bald Mountain'), ('dollar-mountain', 'Dollar Mountain')]
# the trail list (report.json: the interactive maps' downhill trails with their ratings, report_ml.py), each mountain
# an area, with its summit as printed (Bald Mountain 9,150', Dollar Mountain 6,638')
REPORT = json.load(open(os.path.join(HERE, 'report.json')))['trails']
AREAS = [('bald-mountain', 'Bald Mountain', 9150), ('dollar-mountain', 'Dollar Mountain', 6638)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}
NAMES = sorted({n for n, *_r in REPORT})
AS_PRINTED = False
AREA_OF = {n: _AREA_ID[a] for n, a, _r in REPORT}
PARKS = {n for n, _a, r in REPORT if r == 'TerrainPark'}


class _Rename(dict):
    """The map abbreviates a run's part, U. M. L. (Upper, Mid, Lower), and Picabo's Street's St: spelled out (the
    trail list's names then spell the rest); the names set out below as they are."""
    def get(self, k, default=None):
        if k in self:
            return self[k]
        n = re.sub(r'^U\. ?', 'Upper ', re.sub(r'^M\. ?', 'Mid ', re.sub(r'^L\. ?', 'Lower ', k)))
        n = re.sub(r' ST$', ' STREET', n)
        return n if n != k else default


RENAME = _Rename({'SADDLE UP': 'Saddle Up Park', 'BROADWAYPARK': 'Broadway Park'})
DISPLAY = {}


def is_name(label):
    return True
