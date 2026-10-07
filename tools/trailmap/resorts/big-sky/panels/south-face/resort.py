"""Big Sky Resort, the South Face inset (bigsky_south-face.pdf: Shedhorn, Dakota and the south side of Lone Peak,
drawn larger than on the main map). Trail lines are strokes in the difficulty colours (green, blue, black; the terrain parks orange; the
main green and blue routes drawn wide); names are dark text on a white halo, curved ones also drawn a letter at a
time, the symbol before or after the name, printed along the line, in a gap of it or beside it. Read by
tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location('big_sky', os.path.join(os.path.dirname(__file__), '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (12, 12, 2091, 1204)  # PDF points: the page inside its black frame
SCALE = 1.6  # map px per PDF point
SOURCE = ('Big Sky Resort 2025-26 trail map PDF (bigskyresort.com, trail maps), South Face inset: 2.1 pt blue and black '
          'strokes, tools/trailmap/resorts/big-sky/prepare.py; percent of the map image')
SYMBOL_REACH = 38  # pt from a name's first or last character to its symbol
END_REACH = 12  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 9  # pt: a name printed beside its line, about a character's height off it
ALONG_NEAREST = True
ALONG_FIRST = True  # names are printed along their own line, the symbol at one end: that line is the name's
SYMBOL_CENTRE = True  # symbols printed before or after the name, or under its middle
NO_STRETCH_BESIDE = True

is_name = TOP.is_name


# names printed in parts (on two lines), in reading order
JOIN = [('HANGING', 'VALLEY'), ('BACKCOUNTRY!', 'USE EXTREME CAUTION'), ('BAVARIAN', 'FOREST'), ('ERIKA’S', 'GLADE'),
        ('VUARNET', 'CLIFFS'), ('DICTATOR', 'CHUTES'), ('ROCKVILLE', 'BOWL'), ('ASPEN', 'MEADOWS'),
        ('GULLIES', 'TRAVERSE'), ('SHEDHORN', 'GRILL')]
JOIN_GAP = 20  # pt between the parts' glyph centres (12.6 pt capitals)
TWO_LINE = {' '.join(p) for p in JOIN}
NO_STRETCH = set()
LABEL_LINE = set()
# backcountry beyond the boundary (Wyoming and Dakota Bowls, Hanging Valley), Kircher's Cliffs (a landmark: no symbol,
# not on the trail report), the Shedhorn Grill, a pointer to the Mountain Village, the Yellowstone Club gate (YC)
DROP = [(t, None) for t in ('WYOMING BOWL', 'BACKCOUNTRY! USE EXTREME CAUTION', 'DAKOTA BOWL', 'HANGING VALLEY',
                            'KIRCHER’S CLIFFS', 'SHEDHORN GRILL', 'TO MOUNTAIN VILLAGE', 'YC')]
# as the resort's trail report names them (NAMES spells the rest)
RENAME = {'ERIKA’S GLADE': 'Erika’s', 'BITTEROOT': 'Bitterroot',
          'CALAMITY JANE': 'Calamity Jane (Upper)'}  # its upper part, from the Swift Current lift's top
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = {}
# Ace's line leaves the traverse past the double diamond that it and King's share
DEFAULT_SYMBOL = {'Ace': 'double-diamond'}
GLADES = set()
PARKS = TOP.PARKS
NO_LINE = {}
NAMES = TOP.NAMES
AREA_OF = TOP.AREA_OF


def area(c):
    return 'lone-mountain'
