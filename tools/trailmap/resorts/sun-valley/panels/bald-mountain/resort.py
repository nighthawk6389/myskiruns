"""Sun Valley, the bald-mountain panel: this season's Bald Mountain image, the 2023-24 export's strokes, names and
symbols registered on it. Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('sun_valley', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

IMAGE = 'baldy_2627.png'  # this season's map (the PDF's picture, 4000x2257 px)
EXPORT = 'baldy_2023.pdf'  # the 2023-24 export (skimap.org 24666), 2926x1838 pt
# the export's page (pt) on the image (px), registered with tools/trailmap/register_pages.py (SIFT on the page's render,
# RANSAC: 1453 inliers, median residual 0.15 px): x = a pt_x + b pt_y + c, y = d pt_x + e pt_y + f
AFFINE = (1.3605964, -0.0001165, 19.5418, 0.0000055, 1.3602595, -303.3982)
CLIP = (0, 0, 4000, 2257)  # map px: everything is put on the image (SCALE 1)
SCALE = 1
SOURCE = ("Sun Valley Bald Mountain 2026-27 trail map image with the 2023-24 export's 1 pt green, blue and black "
          'strokes and 4 pt dotted way down (skimap.org 24666) registered on it, '
          'tools/trailmap/resorts/sun-valley/prepare.py; percent of the map image')
DARK, DARK2 = (0.14, 0.12, 0.13), (0.14, 0.12, 0.13)
LINE_WIDTH = (0.9, 1.1)
WAY_DOWN_WIDTH = (3.9, 4.1)  # pt: the least difficult way down's dots (green, and blue on its two blue stretches)
LABEL_ARGS = []
# map px: the Warm Springs Plaza inset (top right), the River Run Plaza inset (bottom left), the legend (bottom right),
# the land agencies' logos and note (bottom left)
EXCLUDE = [(3200, 200, 3935, 665), (40, 1770, 770, 2210), (3230, 1540, 3970, 2230), (320, 1580, 870, 1705)]
SYMBOL_REACH = 22  # px (16 pt: the symbol sits on the line a gap past the name) from a name's first or last letter to its symbol
END_REACH = 11  # px
ALONG = 7  # px: a name printed beside its line
JOIN_GAP = 30  # px
NO_STRETCH_BESIDE = True

NAMES, AREA_OF, AS_PRINTED, PARKS = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED, set(TOP.PARKS) | {'Broadway Park'}
is_name = TOP.is_name


def area(c):
    return 'bald-mountain'


JOIN = [('SHOWTIME', 'P ARK'), ('MAIDEN', 'LANE'), ('42nd', 'STREET'), ('SUNSET', 'STRIP'), ('SUNRISE', 'BOWL'),
        ('ROUNDHOUSE', 'SLOPE')]
TWO_LINE = {' '.join(p) for p in JOIN}
NO_STRETCH = set()
# runs the 2023 export (and this season's print) draws no line for, the name printed down the run: the stretch along
# the name is the run's overlay (Arapahoe Basin's way); the bowls, faces and glades printed level are markers (the cat
# tracks on the least difficult way down, and Upper Flying Squirrel on its blue stretch, have its dots for their line)
LABEL_LINE = {'Fire Trail', 'Hour Glass', 'Little Scorpion', 'Mid Inhibition', 'Numbers', 'Rock Garden',
              'Sleeping Bear', 'Three Bears', 'Upper Janss Pass', 'Wolverton'}
DROP = [('--', None), ('S/M', None), ('ACCELERATOR', None), ('CONVEYOR LIFT', None), ('FIRST AID-SKI PATROL', None)]
RENAME = TOP.RENAME
RENAME_AT = []
# names this season's print adds that the 2023 export doesn't have (z26.png, z27.png, z28.png: each with its symbol, no
# line), at their names (map px); the trail list's other names this print doesn't show (the kids' adventure trails, the
# College Hike Park, the Broadway family cross course, The Flume) are left out
EXTRA = [('29 Turns', 575, 477, 'diamond'), ('Cold Springs Chutes', 640, 670, 'double-diamond'),
         ('Bear Den', 1612, 905, 'diamond'), ('Pioneer Bowl', 1790, 880, 'diamond'), ("Tim's", 1815, 790, 'diamond'),
         ('Sheep Camp', 1585, 1032, 'square')]
SYMBOL_FIX = []
SYMBOL_OF = []
# z29.png: the symbol printed by these names (the trail list's too) where the match took a neighbour's: Cut Off's
# diamond, Inhibition's and Three Bears' two, Sunrise Bowl's one; 42nd Street prints none, on the green way down
RATING = {'Cut Off': 'diamond', 'Inhibition': 'double-diamond', 'Three Bears': 'double-diamond',
          'Sunrise Bowl': 'diamond', '42nd Street': 'circle'}
DISPLAY = dict(TOP.DISPLAY)
GLADES = set()
NO_LINE = {}
DEFAULT_SYMBOL = {}
