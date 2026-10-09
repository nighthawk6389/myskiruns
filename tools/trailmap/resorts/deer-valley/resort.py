"""Deer Valley's 2025-26 trail map (Rad Smith's painting, with the East Village expansion): the resort publishes it
as its interactive map (resorts-interactive.com map 1815) and links no PDF; skimap.org keeps two exports of the
same artwork: the vector PDF of 2025-10-16 (map 35124: trail lines as strokes, names as outlined glyphs, over a
45 dpi painting) and the flattened image of 2025-11-04 (map 40099: 5301x3997 px, the page with a sharp painting, a
taller top and the logo and legend moved). The map image is the November image (its trail area, BOX); the lines,
names and symbols are the October PDF's, registered on it (AFFINE). prepare.py extracts it; read by
tools/trailmap/pdf_resort.py."""
import json
import os
import re

# the November image's trail area (px: x0, y0, x1, y1): the map image
BOX = (58, 600, 5242, 3920)
# the October PDF's page (pt) on the November image (px), registered with tools/trailmap/register_pages.py (SIFT
# matches on the page's render, RANSAC: 2982 inliers, median residual 0.085 px): x = a pt_x + b pt_y + c,
# y = d pt_x + e pt_y + f
AFFINE = (1.3888948, 0.0000021, -27.5124, 0.0000022, 1.3888649, 573.8250)
SCALE = (AFFINE[0] + AFFINE[4]) / 2  # map px per PDF point (the shear, under 0.01 px here, left out)
_x0, _y0 = (BOX[0] - AFFINE[2]) / AFFINE[0], (BOX[1] - AFFINE[5]) / AFFINE[4]
CLIP = (_x0, _y0, _x0 + (BOX[2] - BOX[0]) / SCALE, _y0 + (BOX[3] - BOX[1]) / SCALE)  # PDF points
# the interactive map's SVG (its units) on the map image (px): registered on its painting (register_pages.py --ref),
# then refined on the line pieces (tools/trailmap/vicomap.py fit: its trail lines are this map's strokes drawn again;
# 17834 of 17954 points paired, median 0.27 px)
VICOMAP_AFFINE = (0.8585342, 0.0000115, 58.6005, -0.0000090, 0.8585314, 72.2233)
SOURCE = ('Deer Valley 2025-26 trail map: the 2025-10-16 PDF (skimap.org 35124), its 2.1 pt green, blue and black '
          'strokes registered on the 2025-11-04 image (skimap.org 40099), tools/trailmap/resorts/deer-valley/'
          'prepare.py; percent of the map image')
SYMBOL_REACH = 20  # pt from a name's first or last character (or its middle) to its symbol
SYMBOL_CENTRE = True  # bowls', glades' and chutes' symbols are printed under the middle of their name
END_REACH = 12  # pt from a name's end (or its symbol: printed a little apart, in the gap) to the end of the line
ALONG = 4.5  # pt: a name printed beside its line, about a character's height off it


def is_name(label):
    """The trail names: the names' layer, drawn after the lines and before the lift names (Sultan Express, from 10480
    on: McHenry and Exchange, drawn last of the names, come just before), the lodges', peaks' and elevations'; the
    COMING WINTER 26/27 notice on Hail Peak (2-8) is no name."""
    return 1000 < label['seq'] < 10480


# the resort's trail report (report.json: the 2025-26 list, every trail with its mountain and rating). Its runs split
# into (Upper), (Mid) and (Lower) are printed as one name, once or several times along the run, with one rating
# (Big Stick's lower part is advanced intermediate, its upper intermediate: both blue): one trail each.
REPORT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']


def _base(name):
    return re.sub(r'\s*\((?:Upper|Mid|Lower)\)$', '', name)


# names as the report spells them (pdf_resort.py matches a printed name to one by its letters alone: the October PDF
# prints Non-Descript, To The Max, Lakeshore, straddle Bug), but for two the map spells better: Ruins of Pompeii (the
# report's Ruins Of Pompeii) and Miner's Delight (its Miners Delight; the report keeps every other apostrophe)
NAMES = sorted({_base(n) for n, _a, _r in REPORT} - {'Ruins Of Pompeii', 'Miners Delight'})
AS_PRINTED = True  # names are shown as printed or, where the report lists them, as it spells them
# the report's mountains, each with its elevation as the map prints it
AREAS = [('bald-mountain', 'Bald Mountain', 9400), ('bald-eagle', 'Bald Eagle Mountain', 8400),
         ('flagstaff', 'Flagstaff Mountain', 9100), ('empire', 'Empire', 9570), ('lady-morgan', 'Lady Morgan', 9000),
         ('park-peak', 'Park Peak', 9350), ('big-dutch', 'Big Dutch Peak', 8170), ('keetley', 'Keetley Point', 7770),
         ('pioche', 'Pioche Point', 7244), ('little-baldy', 'Little Baldy Peak', 7950)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}
AREA_OF = {_base(n): _AREA_ID[a] for n, a, _r in REPORT}
AREA_OF.update({'Ruins of Pompeii': AREA_OF['Ruins Of Pompeii'], 'Miner’s Delight': AREA_OF['Miners Delight'],
                'Lower Lily': AREA_OF['Lily'], 'Lower Magnet': AREA_OF['Magnet']})


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


# names printed in parts (two lines, one under the other), in reading order
JOIN = [('Dream', 'Meadow'), ('Anchor', 'Trees'), ('Daly', 'Bowl'), ('Quincy', 'Knoll'), ('Daly', 'Chutes'),
        ('Perseverance', 'Bowl'), ('Mayflower', 'Bowl'), ('Lady Morgan', 'Bowl'), ('Mayflower', 'Chutes'),
        ('Ontario', 'Bowl'), ('Sunset', 'Glade'), ('DT’s', 'Trees'), ('Black', 'Forest'), ('Gumby', 'Glade'),
        ('Gilt', 'Edge'), ('Son of', 'Rattler'), ('Mayflower', 'Link'), ('Sil ver', 'Link'), ('Rising', 'Star'),
        ('Yes', 'YouDo'), ('White', 'Owl'), ('Lucky', 'Bud'), ('Littl e', 'Kate'), ('Lower', 'Lily')]
JOIN_GAP = 20  # pt between the parts' glyph centres (Little Kate's two lines are 19 apart)
TWO_LINE = {' '.join(p) for p in JOIN}
NO_STRETCH = set()
LABEL_LINE = set()
# Magnet is drawn twice at one spot, the first time misspelt (Magent) and hidden under the second
DROP = [('Magent', None)]
# the November image's corrections (checks/editions.py labels): it prints Humbug for the October PDF's Ham Bug,
# Persistance for Persistence, Niagara for Niagra, Ruins of Pompeii for Pompei (and Nondescript, To the Max, which
# NAMES spells so); Mtn. Daisy is the report's Mountain Daisy
RENAME = {'Ham Bug': 'Humbug', 'Persistence': 'Persistance', 'Niagra': 'Niagara', 'Ruins of Pompei': 'Ruins of Pompeii',
          'Mtn. Daisy': 'Mountain Daisy'}
EXTRA = []
SYMBOL_FIX = []
# the unnamed "symbols" left: the black pick-and-shovel icons' and the peaks' small shapes, and squares repeated
# along a run's line (Jordanelle's, Free Will's, Redemption's): no run of their own
LOOSE_SYMBOLS = 'icon shapes and squares repeated along their own run'
# names printed twice with two symbols (the interactive map draws two parts of each, in the two ratings): the report's
# rating. Bluebell and Solid Muldoon: a circle and a square, blue; Solace: a square and a diamond, blue; Stein's Way:
# a square and a diamond, black
RATING = {'Bluebell': 'square', 'Solid Muldoon': 'square', 'Solace': 'square', "Stein's Way": 'diamond'}
SYMBOL_OF = []
DISPLAY = {}
GLADES = set()
PARKS = set()
NO_LINE = {}
