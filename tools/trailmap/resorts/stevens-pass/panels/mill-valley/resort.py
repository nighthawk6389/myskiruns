"""Stevens Pass, the mill-valley panel: the Mill Valley painting (the page's right half, at a larger scale). Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('stevens_pass', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (1165, 13, 2003, 695)  # PDF points: the painting
SCALE = 3.0  # map px per PDF point (the painting itself is 100 dpi: 1.4 px per point)
SOURCE = ('Stevens Pass trail map PDF (stevenspass.com), mill-valley: 1.1 to 1.4 pt black, blue and green strokes, '
          'tools/trailmap/resorts/stevens-pass/prepare.py; percent of the map image')
SYMBOL_REACH = 20  # pt (the panel is drawn at a larger scale: its symbols sit farther from their names)
END_REACH = 8
ALONG = 5

AREA_OF = TOP.AREA_OF
is_name = TOP.is_name


def area(c):
    raise ValueError(f'a name at {c} with no lift: give it one in AREA_OF')


# names printed in parts (on two lines), in reading order; a part printed twice is (text, (x, y)): the label near that
# point (map px)
JOIN = [(('SOUTH', (225, 1251)), 'PARK'), (('SOUTH', (1401, 588)), 'DIVIDE'), (('AQUARIUS', (1227, 729)), 'FACE'),
        (('PEGASUS', (1296, 1071)), 'GULCH'), ('RION', 'CHUTES'), ('ANDROMEDA', 'FACE'), ('CORO', 'BOWL')]
TWO_LINE = {' '.join(t if isinstance(t, str) else t[0] for t in p) for p in JOIN}
JOIN_GAP = 45  # pt between the parts' glyph centres (BOBBY CHUTE and CORONA BOWL are printed one part after the
# other down their line, a gap apart; only the parts JOIN lists are joined)
NO_STRETCH = set()
LABEL_LINE = set()
# the sign to the base area; LOWER VOLTAGE, whose two lines' glyphs read jumbled (placed in EXTRA)
DROP = TOP.DROP + [(t, None) for t in ('EASIESTWAYBACK', 'TO', 'BASEAREA', 'BIG', 'CHIEF', 'LO', 'TA', 'LOMERE')]
RENAME = dict(TOP.RENAME)
RENAME_AT = []
EXTRA = [('LOWER VOLTAGE', 765, 1700, 'diamond')]
SYMBOL_FIX = []
SYMBOL_OF = []
RATING = {}
DISPLAY = dict(TOP.DISPLAY)
GLADES = set()
PARKS = TOP.PARKS
NO_LINE = {}
DEFAULT_SYMBOL = dict(TOP.DEFAULT_SYMBOL)
