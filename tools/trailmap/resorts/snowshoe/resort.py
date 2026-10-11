"""Snowshoe Mountain's 2025-26 trail map (the resort's image, 3000x1500 px: James Niehues's painting of Snowshoe
Basin and Silver Creek, the Western Territory an inset on the right, the safety text below) with its interactive
map's SVG as the vector layer (resorts-interactive.com map 1814: every trail's line, letters and symbol grouped under
the trail's name). prepare.py extracts it; read by tools/trailmap/pdf_resort.py."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CLIP = (0, 0, 3000, 954)  # px: the map, above the safety text
SCALE = 1
# the SVG's units on the image (px), registered on its painting (register_pages.py --ref background.png --ref-scale
# 2.79785, the painting's offset in the SVG added): the main map (1466 inliers, median 0.17 px) and, left of
# WT_SPLIT units (the interactive map draws it west of the main mountain), the Western Territory inset (4075
# inliers, median 0.21 px)
VICOMAP_AFFINE = (0.4459118, -0.0000017, -774.3122, 0.0000013, 0.4460073, -106.8255)
WT_AFFINE = (0.3915958, -0.0000030, 2401.7891, 0.0000247, 0.3907970, 14.7445)
WT_SPLIT = 1460
SOURCE = ("Snowshoe 2025-26 trail map image (snowshoemtn.com) with its interactive map's SVG lines "
          '(resorts-interactive.com map 1814), tools/trailmap/resorts/snowshoe/prepare.py; percent of the map image')
GROUPED = True  # every line piece carries its group's name (pdf_resort.py names it by that)
SYMBOL_REACH = 12  # px from a name's first or last letter to its symbol
END_REACH = 8  # px from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 3  # px: a name printed beside its line
NO_STRETCH_BESIDE = True  # names printed on their line, which runs on under them

# the trail report (report.json: the conditions widget's mtnpowder feed): every run with its area
REPORT = json.load(open(os.path.join(HERE, 'report.json')))['trails']
# its areas, each with its highest lift top (OpenStreetMap's lift lines on the USGS's 10 m elevation model,
# tools/trailmap/lift_tops.py): the Soaring Eagle Express's for Snowshoe (the Western Territory with it), the
# Flying Eagle's for Silver Creek
AREAS = [('snowshoe', 'Snowshoe', 4768), ('silver-creek', 'Silver Creek', 4820)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}
NAMES = sorted({n for n, *_r in REPORT})
AS_PRINTED = False
AREA_OF = {}
for _n, _a, *_r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])
PARKS = {n for n, _a, r in REPORT if r == 'TerrainPark'}  # (placed by EXTRA)
# the map's spelling (the report's Knot bumper Glades)
AREA_OF['Knot Bumper Glades'] = 'snowshoe'
GLADES = {n for n, _a, r in REPORT if r == 'Glades' or 'Glades' in n} | {'Knot Bumper Glades'}


def is_name(label):
    return True


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


JOIN = []
TWO_LINE = set()
NO_STRETCH = set()
# names printed in a gap of their own line where the interactive map draws only a stub of it (fix crops): the stretch
# along the name, from its symbol (Cut-off from its circle across the lift toward Lower Whistlepunk's branch;
# Moonshine from its square up to Singletree; Tail Tree from its square to its stub by Heisler Way;
# Lower Ballhooter from its square down to the Boathouse); Stemwinder's, in no line of the interactive map, from its
# square up to Heisler Way's
LABEL_LINE = {'Cut Off', 'Moonshine', 'Tail Tree', 'Lower Ballhooter', 'Stemwinder'}
# the interactive map's second printing of Lower Shay's Revenge, lower down its line: not on this print (wt crop)
DROP = [("Lower Shay's Revenge", (2889, 738))]
RENAME = {}
# printed with no group in the interactive map (names and symbols read on crops, map px): the terrain parks on their
# hatched slopes (their S-M and M-L pills no rating: blue, the playbook's convention), the glades on their hatching
# with the diamond printed by each (the Western Territory prints its diamonds as squares), Shamrock along the path to
# its circle
EXTRA = [('Progression Park', 1100, 542, 'square'), ('Evolution Park', 1208, 579, 'square'),
         ('Mountaineer Park', 1939, 592, 'square'), ('Timberjack Park', 1932, 830, 'square'),
         ('Sawmill Glades', 120, 307, 'diamond'), ('Knot Bumper Glades', 611, 406, 'diamond'),
         ('Sunset Glades', 2652, 315, 'diamond'), ('Flying Eagle Glades', 2215, 590, 'diamond'),
         ('Shamrock', 1225, 255, 'circle')]
SYMBOL_FIX = []
SYMBOL_OF = [((978, 339), 'Stemwinder')]  # its square, out of reach of its name's start
# Lower Shay's Revenge's two squares (the inset's double diamond), beside its name, are in no symbol of its group
RATING = {"Lower Shay's Revenge": 'double-diamond'}
DEFAULT_SYMBOL = {}
DISPLAY = {}
NO_LINE = {}
