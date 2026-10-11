"""Sun Valley, the dollar-mountain panel: this season's Dollar Mountain image, the 2023-24 export's strokes, names and
symbols registered on it. Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('sun_valley', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

IMAGE = 'dollar_2627.png'  # this season's map (the PDF's picture, 4723x1999 px)
EXPORT = 'dollar_2023.pdf'  # the 2023-24 export (skimap.org 24667), 1051x406 pt
# the export's page (pt) on the image (px), registered with tools/trailmap/register_pages.py (761 inliers, median
# residual 0.37 px): x = a pt_x + b pt_y + c, y = d pt_x + e pt_y + f
AFFINE = (4.8850854, -0.0043712, 4.2785, 0.0003525, 4.8809658, -81.6923)
CLIP = (0, 0, 4723, 1999)  # map px: everything is put on the image (SCALE 1)
SCALE = 1
SOURCE = ("Sun Valley Dollar Mountain 2026-27 trail map image with the 2023-24 export's 0.75 pt green, blue and "
          'black strokes (skimap.org 24667) registered on it, tools/trailmap/resorts/sun-valley/prepare.py; percent '
          'of the map image')
DARK, DARK2 = (0.14, 0.12, 0.12), (0.14, 0.12, 0.13)
LINE_WIDTH = (0.7, 0.8)
LABEL_ARGS = []
# map px: the legend (bottom left), the Carol's Dollar Mountain Lodge inset (bottom middle)
EXCLUDE = [(70, 1290, 1060, 1930), (1260, 1440, 2205, 1930)]
SYMBOL_REACH = 55  # px (11 pt) from a name's first or last letter to its symbol
END_REACH = 39  # px
ALONG = 24  # px
JOIN_GAP = 49  # px
NO_STRETCH_BESIDE = True

NAMES, AREA_OF, AS_PRINTED, PARKS = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED, set(TOP.PARKS)
is_name = TOP.is_name


def area(c):
    return 'dollar-mountain'


# names printed on two lines, in reading order
JOIN = [('ELKHORN', 'BOWL'), ('ELKHORN', 'FACE'), ('ARROWHEAD', 'WAY'), ('JOINT', 'VENTURE'), ('FORBIDDEN', 'FRUIT'),
        ('BITTERROOT', 'BOWL'), ('TRAIN', 'YARD'), ('NAME', 'DROPPER'), ('PROSPECTOR', 'PARK'), ('UPPER', 'TRESTLES')]
TWO_LINE = {' '.join(p) for p in JOIN}
NO_STRETCH = {'Sluice Box'}  # a park: its name beside Poverty Flats' line
LABEL_LINE = set()
# the 2023 export's names that this season's print no longer has (Graduation's run is gone, the Name Dropper park
# printed along where it ran; Upper Trestles is now Old Bowl's lower half), the parks' feature sizes
DROP = [('GRADUATION', None), ('NAME DROPPER', None), ('UPPER TRESTLES', None), ('S/M', None), ('M/L', None),
        ('XS/S', None)]
RENAME = TOP.RENAME
RENAME.update({'PROSPECTOR PARK': "Sunny's Adventure Park", 'SEPP’S': "Sepp's Bowl"})  # the park, renamed since 2023 (printed in the same place)
RENAME_AT = []
EXTRA = [('Name Dropper', 4150, 1190, 'square')]  # this season's print: its name down the old Graduation's line
SYMBOL_FIX = []
SYMBOL_OF = []
RATING = {}
DISPLAY = dict(TOP.DISPLAY)
GLADES = set()
NO_LINE = {}
DEFAULT_SYMBOL = {}
