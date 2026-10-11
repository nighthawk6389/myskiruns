"""Stevens Pass, the front-side panel: the Front Side painting (the page's left half). Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('stevens_pass', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (13, 13, 1152, 695)  # PDF points: the painting
SCALE = 3.0  # map px per PDF point (the painting itself is 100 dpi: 1.4 px per point)
SOURCE = ('Stevens Pass trail map PDF (stevenspass.com), front-side: 1.1 to 1.4 pt black, blue and green strokes, '
          'tools/trailmap/resorts/stevens-pass/prepare.py; percent of the map image')
SYMBOL_REACH = 13  # pt from a name's first or last letter to its symbol (on the line, a gap past the name)
END_REACH = 8
ALONG = 5

AREA_OF = TOP.AREA_OF
is_name = TOP.is_name


def area(c):
    raise ValueError(f'a name at {c} with no lift: give it one in AREA_OF')


# names printed in parts (on two lines), in reading order
JOIN = [('BIG', 'CHIEF', 'BOWL'), ('SCHIM’S', 'MEADOW'), ('TRAINING', 'GROUNDS'), ('COURT’S', 'MEADOW'),
        ('BOBBY', 'CHUTE'), ('WINNIE', 'CHUTES'), ('UPPER', 'MAVERICKS'), ('LOWER', 'MAVERICKS'), ('WALL', 'ST.')]
TWO_LINE = {' '.join(p) for p in JOIN}
JOIN_GAP = 45  # pt between the parts' glyph centres (BOBBY CHUTE and CORONA BOWL are printed one part after the
# other down their line, a gap apart; only the parts JOIN lists are joined)
NO_STRETCH = set()
LABEL_LINE = set()
# the lots, lodges and the ski school, the double-diamond lift's name (the run's is printed beside it, smaller), the
# arrow to Mill Valley's lifts, the parks' feature sizes
DROP = TOP.DROP + [(t, None) for t in (
    'LOT 1', 'LOT 2', 'LOT 3', 'LOT 4', 'LOT A', 'LOT C', 'LOT E', 'LOT G', 'RV LOT/LOT F', 'LODGE', 'TYE CREEK LODGE',
    'PACIFIC CREST', 'GRANITE PEAKS', 'MTN EDUCATION', 'CENTER', 'SKI &', 'SNOWBOARDSCCOOL', 'LEARNING', 'TERRAIN',
    'MILL VALLEYIJUPITER EXPRESS &', 'SOUTHERN CROSS CHAIR LIFTS', 'S-X', '-LW', '-WS')] + [
    ('DOUBLE DIAMOND', (573, 831))]
RENAME = dict(TOP.RENAME)
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
RATING = {}
DISPLAY = dict(TOP.DISPLAY)
GLADES = set()
PARKS = TOP.PARKS
NO_LINE = {}
DEFAULT_SYMBOL = dict(TOP.DEFAULT_SYMBOL)
