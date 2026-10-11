"""Solitude Mountain Resort's 2025-26 trail map (the resort's PDF: one flattened image, 3000x2320 px; James Niehues's
painting with the Highway to Heaven inset top left) with its interactive map's SVG as the vector layer
(resorts-interactive.com map 1811: every trail's line, letters and symbol grouped under the trail's name). prepare.py
extracts it; read by tools/trailmap/pdf_resort.py."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CLIP = (0, 0, 3000, 2320)  # the whole image, in px: the map's units here are its pixels
SCALE = 1
# the SVG's units on the image (px): registered on its painting (register_pages.py --ref background.png
# --ref-scale 2.76778: 622 inliers, median 0.26 px; the painting's offset in the SVG added), then fitted on the
# image's blue line ink (vicomap.py fit-ink: median 0.44 px to the nearest ink pixel)
VICOMAP_AFFINE = (0.6150167, -0.0000117, 434.0412, 0.0000238, 0.6150899, -14.3717)
SOURCE = ("Solitude 2025-26 trail map image (solitudemountain.com's PDF) with its interactive map's SVG lines "
          '(resorts-interactive.com map 1811), tools/trailmap/resorts/solitude/prepare.py; percent of the map image')
GROUPED = True  # every line piece carries its group's name (pdf_resort.py names it by that)
SYMBOL_REACH = 12  # px from a name's first or last letter to its symbol
END_REACH = 8  # px from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 3  # px: a name printed beside its line
# names printed on their line, which runs on under them (most), or in a gap of it (Honeycomb Return): a stretch only
# where no line of its own runs along the name
NO_STRETCH_BESIDE = True

# the trail report (report.json: the conditions widget's mtnpowder feed): every run with its area; the Nordic area's
# cross-country and snowshoe trails are no runs of the alpine map
REPORT = [r for r in json.load(open(os.path.join(HERE, 'report.json')))['trails'] if r[1] != 'Nordic']
NORDIC = {r[0] for r in json.load(open(os.path.join(HERE, 'report.json')))['trails'] if r[1] == 'Nordic'}
# its areas, each with the highest elevation in it as printed (Honeycomb Peak, the Summit Express's top, Black Bess
# Peak for Fantasy Ridge and the Highway to Heaven, Evergreen Peak, the Eagle Express's top), the Moonbeam Express's
# top for the Moonbeam Area (OpenStreetMap's lift line on the USGS's 10 m model, tools/trailmap/lift_tops.py)
AREAS = [('honeycomb-canyon', 'Honeycomb Canyon', 10488), ('fantasy-ridge', 'Fantasy Ridge', 10479),
         ('highway-to-heaven', 'Highway to Heaven', 10479), ('solitude-canyon', 'Solitude Canyon', 10035),
         ('evergreen-peak', 'Evergreen Peak', 9850), ('eagle-ridge', 'Eagle Ridge', 9345),
         ('moonbeam', 'Moonbeam Area', 8756)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}
NAMES = sorted({n for n, *_r in REPORT})
AS_PRINTED = False
AREA_OF = {}
for _n, _a, *_r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])
# printed once, SUNDANCER, on the one line the interactive map calls Sundancer Lower (the report lists an Upper and a
# Lower): one run, as printed
AREA_OF['Sundancer'] = 'eagle-ridge'
PARKS = {n for n, _a, r in REPORT if r == 'TerrainPark' or 'Terrain Park' in n}
GLADES = set()


def is_name(label):
    return True


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


# the runs' lines print no symbol: a run is rated by the colour of its line and name (the expert areas, a name with no
# line, by the diamond or two printed by it)
COLOR_SYMBOL = {'green': 'circle', 'blue': 'square', 'black': 'diamond'}
JOIN = []
TWO_LINE = set()
NO_STRETCH = set()
LABEL_LINE = set()
DROP = []
RENAME = {'Sundancer Lower': 'Sundancer'}
# the Highway to Heaven, printed only in the inset (top left, outside the interactive map): the double-black terrain
# under the traverse from the Fantasy Ridge gate toward Twin Lakes Pass, a name and two diamonds with no line
EXTRA = [('Highway to Heaven', 280, 275, 'double-diamond')]
SYMBOL_FIX = []
SYMBOL_OF = []
RATING = {'Tude Dudes': 'circle'}  # its name printed green (the interactive map's letters are blue), as the report
DEFAULT_SYMBOL = {}
DISPLAY = {}
NO_LINE = {}
