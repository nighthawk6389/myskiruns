"""Mount Snow's 2025-26 trail map (VistaMap's painting, Gary Milliken): the resort's PDF of it is flattened (the whole
map one 72 dpi image) and Vail Resorts' CDN serves the same page as a 3175 px image (scene7
20251103_SO_winter-trail_map_001), the map image (BOX). Its vectors come from two older exports of the same artwork
on skimap.org, registered on it (recipe D, as Beaver Creek): the 2023-24 trail map PDF (map 24777: every run's line a
1.15 pt stroke, the Sunbrook inset's 0.61 pt; its names outlined glyphs) for the lines (AFFINE, INSET_AFFINE), and the
2024-25 winter uphill-access map (map 36693: the names as live text, under a white fade; some runs' lines clipped
away) for the names (UPHILL_AFFINE). The Sunbrook area behind the summit is drawn only in the inset (top left); its
names are placed by hand (EXTRA). prepare.py extracts it; read by tools/trailmap/pdf_resort.py."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
# the 2025-26 image's map (px: x0, y0, x1, y1): the painting, above the partners' band
BOX = (49, 50, 3125, 1967)
# each export's page (pt) on the 2025-26 image (px), registered with tools/trailmap/register_pages.py (SIFT matches on
# the page's render, RANSAC): x = a pt_x + b pt_y + c, y = d pt_x + e pt_y + f. The 2023-24 map right of its inset
# (1256 inliers, median residual 1.06 px: the painting re-rendered a little since), its inset on this season's inset
# (1054 inliers, 0.49 px), the uphill map (419 inliers, 0.41 px)
AFFINE = (2.0000837, -0.0004997, 135.7052, 0.0001794, 1.9984569, 133.2066)
INSET_AFFINE = (2.0639210, 0.0006106, 125.6116, 0.0000258, 2.0615402, 121.6499)
UPHILL_AFFINE = (1.1461917, -0.0000959, 122.6823, -0.0000866, 1.1461754, 50.2714)
INSET = (9, -8, 354, 258)  # the 2023-24 inset's frame (pt)
INSET_COVER = (1, -25, 367, 264)  # the part of the 2023-24 map this season's inset covers (pt)
SCALE = (AFFINE[0] + AFFINE[4]) / 2  # map px per PDF point (the shear, under 0.5 px across the page, left out)
_x0, _y0 = (BOX[0] - AFFINE[2]) / AFFINE[0], (BOX[1] - AFFINE[5]) / AFFINE[4]
CLIP = (_x0, _y0, _x0 + (BOX[2] - BOX[0]) / SCALE, _y0 + (BOX[3] - BOX[1]) / SCALE)  # PDF points (2023-24)
SOURCE = ("Mount Snow 2025-26 trail map: the 2023-24 PDF's 1.15 pt run strokes (skimap.org 24777) registered on the "
          "2025-26 image (Vail Resorts' CDN), tools/trailmap/resorts/mount-snow/prepare.py; percent of the map image")
SYMBOL_REACH = 0  # the map prints no symbol by a name: each run is rated by its name's colour (COLOR_SYMBOL)
END_REACH = 14  # pt from a name's end to the end of the line that runs into it
ALONG = 4  # pt: a name printed beside its line
ALONG_NEAREST = True  # names printed beside their line, between parallel ones: the nearest only

# the trail report (report.json: the terrain feed of mountsnow.com's lift-and-terrain-status page as Common Crawl
# captured it on 2025-12-14), every run with its area
REPORT = json.load(open(os.path.join(HERE, 'report.json')))['trails']
# its areas, each with the highest elevation printed or measured in it: the summit as printed (3,600 ft) for the Main
# Face, the North Face and Sunbrook (its lift's top is the summit); Carinthia the top of the Nitro Express
# (tools/trailmap/lift_tops.py: OpenStreetMap's lift line on the USGS's 10 m elevation model)
AREAS = [('main-face', 'Main Face', 3600), ('north-face', 'North Face', 3600), ('sunbrook', 'Sunbrook', 3600),
         ('carinthia', 'Carinthia', 2962)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}


def key(name):
    """A name with case, spaces and punctuation left out (pdf_resort.py's spelling_key)."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


NAMES = sorted({n for n, *_r in REPORT})
AS_PRINTED = False
AREA_OF = {}
for _n, _a, *_r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])
PARKS = {n for n, _a, r in REPORT if r == 'TerrainPark'}
# rated by the colour each name is printed in (the legend's green, blue and black; the parks' names orange)
COLOR_SYMBOL = {'green': 'circle', 'blue': 'square', 'black': 'diamond'}


def is_name(label):
    """The runs' names: the condensed Futura in the runs' colours (prepare.py keeps only these)."""
    return True


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


# names printed in two parts (on two lines), in reading order (the others on two lines are one text object)
JOIN = [('SNOWDANCE', 'PITCH')]
JOIN_GAP = 18  # pt: SNOWDANCE over PITCH, 16 apart
TWO_LINE = {'SWITCH BACK', 'SNOWDANCE PITCH', 'SECOND THOUGHTS', 'LITTLE STEEP'}
SPLIT = {}
NO_STRETCH = set()
LABEL_LINE = set()
DROP = [('TUBING PARK', None)]  # the tubing park: no ski run
RENAME = {'THE JUNKYARD': 'Junkyard', 'BEARPAW': 'Bear Paw', 'SWITCH BACK': 'Switchback'}
RENAME_AT = []
# the Sunbrook inset's names (outlined glyphs in the 2023-24 PDF, which this map takes no names from), each at its
# label in map px with the symbol printed by it, read on a 3.5x render of that inset (Little Dipper is printed twice)
EXTRA = [('Big Dipper', 258, 195, 'square'), ('Moonwalk', 341, 154, 'square'), ('Little Dipper', 282, 242, 'square'),
         ('Little Dipper', 249, 401, 'square'), ('Thanks Walt', 329, 251, 'square'), ('Cloud Nine', 356, 322, 'square'),
         ('Sunspot', 423, 175, 'square'), ('Shooting Star', 485, 208, 'square'),
         ('One Small Step', 258, 282, 'square'), ('Moonbeam', 255, 460, 'square'), ('Milky Way', 650, 449, 'square'),
         ('Skyline', 430, 138, 'square'), ('Bear Paw', 653, 343, 'circle'), ('Long John', 665, 319, 'circle'),
         ('Bear Trap', 482, 413, 'diamond')]
SYMBOL_FIX = []
SYMBOL_OF = []
RATING = {'Ripcord': 'double-diamond'}  # its two diamonds (the name is black, as every expert run's)
DEFAULT_SYMBOL = {}
DISPLAY = {}
GLADES = set()
NO_LINE = {}
