"""Big Sky Resort, the Bowl inset (bigsky_bowl.pdf: Lone Peak above the Powder Seeker and the tram, drawn larger
than on the main map). Trail lines are strokes in the difficulty colours (green, blue, black; the terrain parks orange; the
main green and blue routes drawn wide); names are dark text on a white halo, curved ones also drawn a letter at a
time, the symbol before or after the name, printed along the line, in a gap of it or beside it. Read by
tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location('big_sky', os.path.join(os.path.dirname(__file__), '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (12, 12, 1184, 1178)  # PDF points: the page inside its black frame
SCALE = 2.5  # map px per PDF point
SOURCE = ('Big Sky Resort 2025-26 trail map PDF (bigskyresort.com, trail maps), Bowl inset: 1.4 pt green, blue and black '
          'strokes, tools/trailmap/resorts/big-sky/prepare.py; percent of the map image')
SYMBOL_REACH = 28  # pt from a name's first or last character to its symbol
END_REACH = 8  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 6  # pt: a name printed beside its line, about a character's height off it
ALONG_NEAREST = True
ALONG_FIRST = True  # names are printed along their own line, the symbol at one end: that line is the name's
SYMBOL_CENTRE = True  # symbols printed before or after the name, or under its middle
NO_STRETCH_BESIDE = True

is_name = TOP.is_name


# names printed in parts (on two lines), in reading order
JOIN = [('BONECRUSHER', 'HIKING AREA'), ('ST. ALPHONSE', 'TREES')]
JOIN_GAP = 14  # pt between the parts' glyph centres (8.3 pt capitals)
TWO_LINE = {' '.join(p) for p in JOIN}
NO_STRETCH = {'The Gullies'}  # printed across its six chutes, not in a gap of a line
LABEL_LINE = set()
# the Gullies' and A-Z Chutes' numbers, the TO of TO CRON'S, a name cut by the inset's frame (FORBIDDEN FOREST, its
# letters drawn twice), Stutzman's Rock (a landmark: no symbol, not on the trail report)
DROP = [(t, None) for t in ('1 2 3', '4 5 6', 'TO', 'FORBIDDEN FORE', 'STUTZMAN’S ROCK')]
# as the resort's trail report names them (NAMES spells the rest)
RENAME = {'THE BIG COULOIR': 'Big Couloir', 'KASTLE ROCK (A-Z)': 'Kastle Rock (A-Z Chutes)',
          'PARACHUTE (A-Z)': 'Parachute (A-Z Chutes)', 'STEEP & DEEP': 'Steep and Deep',
          '0-3 CACHE TREES': 'Cache Trees', '1-3 LITTLE GULLIES': 'Little Gullies',
          'BONECRUSHER HIKING AREA': 'Bone Crusher', 'PLAIN JANE': 'Plain Jane Park', 'FORBIDDEN FOR': 'Forbidden Forest',
          'CALAMITY JANE': 'Calamity Jane (Upper)'}  # its upper part, beside the Swift Current lift's top
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = {}
GLADES = set()
PARKS = TOP.PARKS
NO_LINE = {}
NAMES = TOP.NAMES
AREA_OF = TOP.AREA_OF


def area(c):
    return 'lone-mountain'
