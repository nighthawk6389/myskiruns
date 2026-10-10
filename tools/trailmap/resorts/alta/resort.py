"""Alta Ski Area's 2025-26 trail map (alta.com: Alta_Trailmap_2025_26.pdf, one Illustrator page): James Niehues's
painting under vector strokes in the three trail colours; names outlined black glyphs printed along their run's line,
the symbol at the name's start; many expert runs a name and a diamond with no line. Read by
tools/trailmap/pdf_resort.py; prepare.py extracts it."""
import json
import os

CLIP = (0, 0, 1695, 952)  # PDF points: the page above the key bar
SCALE = 2.5  # map px per PDF point
SOURCE = ('Alta 2025-26 trail map PDF (alta.com): black, blue and green strokes, '
          'tools/trailmap/resorts/alta/prepare.py; percent of the map image')
SYMBOL_REACH = 16  # pt from a name's first or last letter (or its middle) to its symbol
SYMBOL_CENTRE = True  # the faces' and bowls' names printed level, the diamond under or over their middle
END_REACH = 10
ALONG = 6  # pt: a name printed beside its line, about a letter's height off it
ALONG_NEAREST = True
ALONG_FIRST = True
NO_STRETCH_BESIDE = True

# the trail report's lifts (report.json: the lift and terrain status page), each with the top of its lift's terrain
# as printed (Sugarloaf Peak 11,051 ft for Sugarloaf and Supreme's Devil's Castle side, Mt. Baldy 11,068 ft for
# Collins and Wildcat, the Albion base 8,580 ft for Sunnyside's)
AREAS = [('sunnyside', 'Sunnyside', 8580), ('supreme', 'Supreme', 10920), ('sugarloaf', 'Sugarloaf', 11051),
         ('collins', 'Collins', 11068), ('wildcat', 'Wildcat', 11068)]
_AREA_ID = {'Sunnyside': 'sunnyside', 'Supreme': 'supreme', 'Sugarloaf': 'sugarloaf', 'Collins': 'collins',
            'Wildcat': 'wildcat'}
REPORT = [t for t in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
          if not t[0].startswith('Nordic')]
NAMES = sorted({n for n, _a, _r in REPORT})
AS_PRINTED = True
AREA_OF = {}
for _n, _a, _r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


def is_name(label):
    return True


COLOR_SYMBOL = {}  # every name is black: the rating is the symbol printed by it
# names printed in parts (on two or three lines, or two runs of glyphs along one), in reading order
JOIN = [('EAST', 'CASTLE'), ("DEVIL'S", 'CASTLE'), ('SUGAR', 'BOWL'), ('GRAVY', 'BOAT'), ('EAST', 'BALDY'),
        ('BALDY', 'CHUTES'), ('SHOULDER', 'TRAVERSE'), ('BALDY', 'SHOULDER'), ('HIGH', 'MAIN STREET'),
        ('HIGH RACE', 'COURSE'), ('GLORY', 'HOLE'), ('RUNNING', 'DOG', 'NOSE'), ('YELLOW', 'TRAIL'),
        ('HIGH', 'SUNSPOT'), ('EAST', 'GREELEY'), ('HIGH', 'GREELEY'), ('GREELEY', 'BOWL'), ('RACE COURSE', 'SADDLE'),
        ('WEST', 'RUSTLER'), ('GREELEY', 'HILL'), ('SUPREME', 'CHALLENGE'), ('SUPREME', 'ACCESS'), ('THREE', 'B EARS'),
        ('CECRET', 'SHUTES')]
TWO_LINE = {' '.join(p) for p in JOIN} - {'EAST CASTLE', "DEVIL'S CASTLE", 'GREELEY HILL'}
JOIN_GAP = 16  # pt: a name's two lines, about 12 pt apart
NO_STRETCH = set()
LABEL_LINE = set()
# the areas' and the backcountry's labels (map px), and the uphill route's note
DROP = [('P ATSEY', (898, 1620)), ('MARLEY', (998, 1622)), ('BACKCOUNTRY CONDITIONS EXIST', None),
        ('GRIZZLY', None), ('GULCH', None), ('CAT SKIING', None), ('(UPHILLACCESS)', None),
        ('SHUTES', None)]  # (SHUTES: a copy of CECRET CHUTES's last six letters, its C read as an S)
# as the trail report names them (NAMES spells the rest by their letters)
RENAME = {'18OBEND': '180 Bend', 'THREE B EARS': '3 Bears', 'SANTA CLAUSE': 'Santa Claus',
          'EBT to COLLINS': 'East Baldy Traverse (EBT)', 'SPINEY CHUTES AREA': 'Spiney Chutes'}
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = {}
GLADES = set()
PARKS = set()
NO_LINE = {}
# SUPREME ACCESS, printed with no symbol: black, as the report rates it
RATING = {'Supreme Access': 'diamond'}
