"""Loon Mountain's winter trail map (loonmtn.com's mountain-maps page: one image, 2500x1406 px, in a Photoshop PDF;
Rob Smith's painting, the Black Ridge expansion shaded in, not yet open) with its interactive map's SVG as the vector
layer (resorts-interactive.com map 14: every trail's line, letters and symbol grouped under the trail's name). The
print draws no lines: each run is a cut through the trees, its name and symbol printed in it. prepare.py extracts it;
read by tools/trailmap/pdf_resort.py."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CLIP = (0, 0, 2500, 1406)  # the whole image, in px: the map's units here are its pixels
SCALE = 1
# the SVG's units on the image (px): registered on its painting (register_pages.py --ref background.png
# --ref-scale 2.77778: 1314 inliers, median 0.11 px; the print stretches the painting 1% more tall than wide)
VICOMAP_AFFINE = (0.3671699, -0.0000006, 436.0732, 0.0000003, 0.3708860, 244.2682)
SOURCE = ("Loon winter trail map image (loonmtn.com's PDF) with its interactive map's SVG lines "
          '(resorts-interactive.com map 14), tools/trailmap/resorts/loon/prepare.py; percent of the map image')
GROUPED = True  # every line piece carries its group's name (pdf_resort.py names it by that)
SYMBOL_REACH = 12  # px from a name's first or last letter to its symbol
END_REACH = 8  # px from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 3  # px: a name printed beside its line
NO_STRETCH_BESIDE = True  # names printed in the cut beside the line (the line is the interactive map's)

# the trail report (report.json: the resort's reportpal feed): every run with its area; the Nordic trails and the
# uphill routes are no runs of the alpine map
REPORT = [r for r in json.load(open(os.path.join(HERE, 'report.json')))['trails']
          if r[1] not in ('Nordic', 'Uphill Routes')]
# its areas, each with the elevation printed at its top (North Peak 3,050', Loon Peak 2,733', South Peak 2,461'; West
# Basin's runs start at Loon Peak's summit)
AREAS = [('north-peak', 'North Peak', 3050), ('loon-peak', 'Loon Peak', 2733), ('west-basin', 'West Basin', 2733),
         ('south-peak', 'South Peak', 2461)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}
NAMES = sorted({n for n, *_r in REPORT})
AS_PRINTED = False
AREA_OF = {}
for _n, _a, *_r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])
# the Air Site, printed with the freestyle-terrain symbol under the North Peak lift, a feature the report doesn't list
AREA_OF['Air Site'] = 'north-peak'
PARKS = {n for n, _a, r in REPORT if r == 'TerrainPark'} | {'Air Site'}
GLADES = set()


def is_name(label):
    return True


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


COLOR_SYMBOL = {}
JOIN = []
TWO_LINE = set()
# printed on two lines beside its line (its letters read as several runs): no stretch along it
NO_STRETCH = {"Hannah's Bypass"}
LABEL_LINE = set()
DROP = []
RENAME = {}
# the parks the print shows with no line (blue, the parks' convention): Lil' Stash's logo, printed three times in the
# woods left of Lower Bear Claw (the middle one), and the Air Site's name and freestyle pill (the report's other parks,
# Little Sister Park, Springboard Park, Superpipe, Progression Park, Top Secret Parks and Mini Pipe, print only an
# orange pill or a halfpipe icon on a run, no name: left out)
EXTRA = [("Lil' Stash", 722, 1050, 'square'), ('Air Site', 888, 615, 'square')]
SYMBOL_FIX = []
SYMBOL_OF = []
# the interactive map's symbols for these differ from the print's (and the print is the report's): Undercut prints two
# diamonds, Lower Walking Boss Woods one
RATING = {'Undercut': 'double-diamond', 'Lower Walking Boss Woods': 'diamond'}
DEFAULT_SYMBOL = {}
DISPLAY = {}
NO_LINE = {}
