"""Heavenly, the Top of Gondola inset (the 2024-25 image's inset under the main painting, the area round Tamarack
Lodge drawn larger; lines, names and symbols from the 2022-23 PDF of the same artwork, ../../prepare.py). Trail lines
are blue and green outlines, 2.7 pt wide; names are dark outlined glyphs, the symbol just before the name, printed
along their line or beside it; the lifts' and buildings' names are printed alike. Read by
tools/trailmap/pdf_resort.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location('heavenly', os.path.join(os.path.dirname(__file__), '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

# the 2022-23 page (pt) on the panel's image: resort.AFFINE, its shear taken at the inset's middle (under 0.2 px)
_A = TOP.AFFINE['top-of-gondola']
SCALE = (_A[0] + _A[4]) / 2  # map px per PDF point
_x0 = -(_A[2] + _A[1] * 1145) / _A[0]
_y0 = (TOP.BOX['top-of-gondola'][1] - _A[5] - _A[3] * 380) / _A[4]
CLIP = (_x0, _y0, _x0 + 2368 / SCALE, _y0 + 1102 / SCALE)
SOURCE = ("Heavenly 2024-25 trail map image (Vail Resorts' scene7 CDN), Top of Gondola inset; lines from the 2022-23 "
          'PDF of the same artwork (skimap.org 23043): outlined blue and green lines, tools/trailmap/resorts/heavenly/'
          'prepare.py; percent of the map image')
SYMBOL_REACH = 12  # pt from a name's first or last character to its symbol
END_REACH = 9  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 7  # pt: a name printed beside its line, about a character's height off it
ALONG_NEAREST = True
ALONG_FIRST = True
NO_STRETCH_BESIDE = True


def is_name(label):
    """The inset's names are drawn first on the page, lifts and buildings among them (DROP)."""
    return label['seq'] < 700


# names printed in parts (on two lines), in reading order; Black Bear Carpet's three lines (a lift)
JOIN = [('VON', 'SCHMIDT'), ('EASY', 'STREET'), ('BIG', 'EASY'), ('TO', 'NEVADA'), ('TUBING', 'HILL'),
        ('TAMARAC', 'EXPRESS'), ('BLAC', 'BEAR', 'CARPET')]
JOIN_GAP = 20  # pt between the parts' glyph centres (the inset's letters are twice the main map's)
TWO_LINE = set()
NO_STRETCH = set()
LABEL_LINE = set()
# the panel's title (its letters read as ONDO), lifts (names in red boxes: the Big Easy lift, the Red Fir tow, the
# Black Bear carpet, the Tamarack Express, the Tubing lift, the Gondola), the tubing hill, the mountain coaster, the
# buildings, and the pointers to the two sides
DROP = [(t, None) for t in ('ONDO', 'TO NEVADA', 'TO CALIFORNIA', 'TAMARAC EXPRESS', 'TUBING LIFT', 'GONDOLA',
                            'RIDGE RIDER MTN COASTER', 'BEAR CAVE', 'WINTER ACTIVITIES', 'BLAC BEAR CARPET',
                            'RED FIR', 'TUBING HILL')] + [('BIG EASY', (905, 575))]
RENAME = {'VON SCHMIDT': 'Von Schmidt'}
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
DEFAULT_SYMBOL = {}
DISPLAY = {}
GLADES = set()
PARKS = set()
NO_LINE = {}
NAMES = TOP.NAMES
AREA_OF = TOP.AREA_OF


def area(c):
    """A name the trail report doesn't list: the inset is the Top of Gondola area."""
    return 'top-of-gondola'
