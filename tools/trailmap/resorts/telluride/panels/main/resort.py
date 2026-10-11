"""Telluride, the main panel: the 2024-25 trail map PDF's one page (James Niehues's painting under strokes and
outlined names in the runs' colours). Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('telluride', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (0, 0, 1243, 875)  # PDF points: the whole page (the key, top left, left out of the lines and names)
SCALE = 3  # map px per PDF point
SOURCE = ('Telluride 2024-25 trail map PDF (tellurideskiresort.com): 1 pt black, blue and green strokes, '
          'tools/trailmap/resorts/telluride/prepare.py; percent of the map image')
SYMBOL_REACH = 10  # pt from a name's first or last character to its symbol (a double diamond's middle up to 9 pt; the second of two circles or squares, about 11 pt, is left over)
END_REACH = 5  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 3  # pt: a piece this close to most of a name's characters runs along it

NAMES, AREA_OF, AS_PRINTED = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED
is_name = TOP.is_name


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


# names printed in parts (on two lines), in reading order
JOIN = [('ZULU', 'QUEEN'), ('GOLD', 'RUSH'), ('LAST', 'CHANCE'), ('JOINT', 'POINT'), ('RUNAWAY', 'TRAIN'),
        ('PROSPECT', 'WOODS'), ('LOWER', 'VILLAGE BYPASS'), ('LOWER', 'BOOMERANG'), ('BEGINNER', 'P ARK')]
TWO_LINE = {'ZULU QUEEN', 'GOLD RUSH', 'LAST CHANCE', 'JOINT POINT', 'RUNAWAY TRAIN', 'PROSPECT WOODS',
            'BEGINNER P ARK', 'LOWER VILLAGE BYPASS'}
JOIN_GAP = 9
NO_STRETCH = set()
# runs the map draws no line for, the name printed down the run from its symbol: the stretch along the name is the
# overlay (the Gold Hill chutes; Captain Jack's, a glade)
LABEL_LINE = {'Gold Hill 1', 'Gold Hill 2', 'Captain Jack’s'}
# labels that name no run: the town, bases, buildings, peaks and their elevations, the boundary, closures, gates and
# access points, the warming huts, the hikes, the area titles; Gold Hill Chutes 6-10, printed as one label here, are
# drawn one by one on the Palmyra panel
DROP = [(t, None) for t in (
    'TELLURID E', "8' 750' / 2667m", "6'545' / 2606m", 'BALD', 'MOUNTAIN', "1 1'880' / 3621m", "1 1'666' / 3647m",
    "11'815' /3601m", 'TEMPTER', 'HOUSE', 'PROSPECT', 'BOWL', 'BOUNDARY', 'GOLD HILL CHUTES', '6I1O', 'GOLD HILL',
    'STAIRS', 'REVELATIO N', "12'515' / 3815m", 'See Reverse fOr DetaiI', 'WARMING', 'HUTS',
    'BACKCOUNTRY ACCESS POINT', 'THE PEAKS', 'RESORT', 'SPA', 'CLOSED', 'VILLAGE', "6'540' / 2608m",
    "8' 725' / 2656m", 'HIKE TO TERRAIN', 'BACKCOUNTRY', 'ACCESS POINT', 'CARHENGE', 'P ARKIN G LOT', 'SAN',
    'SOPHIA', 'STATION', "1 0'540' / 321 3m", 'P ALMYRA', 'P EAK', "1 3' 1 50' / 4060m", 'TOPATEN', 'NORDICAND',
    'SNOWSHOE', 'AREA', 'AVALANCHE', 'CONTROL GATE', 'LIT', 'TELL I E',
    # the walking path out of the Gold Hill chutes (no symbol, no line, not in the report)
    'GOAT PATH')] + [('MEADOWS', (2091, 2364))]
# ENCHANTED and FOREST, printed apart along one line (a square by each)
RENAME = {**TOP.RENAME, 'ENCHANTED': 'Enchanted Forest', 'FOREST': 'Enchanted Forest'}
RENAME_AT = [((423, 1893), 'BAIL OUT', 'Lower Bail Out'),  # the blue BAIL OUT (the black one is Bail Out)
             # the two MEADOWS from Mountain Village to the Meadows base, either side of the chondola: the one below
             # it (nearer the viewer, who looks south) the report's North, the one above it South
             ((1689, 2217), 'MEADOWS', 'Meadows – North'), ((1833, 2241), 'MEADOWS', 'Meadows – South')]
# HOOT BROWN TERRAIN PARK, white on its orange stroke (no glyphs in a name colour): its name at the stroke's middle
EXTRA = [('Hoot Brown Terrain Park', 1212, 1893)]
SYMBOL_FIX = []
# symbols printed beside their name, out of reach: SPIRAL STAIRS's double diamond above its label's top (spiral.png),
# RUNAWAY TRAIN's beside its two-line label
SYMBOL_OF = [((720, 1238), 'Spiral Stairs'), ((2934, 1500), 'Runaway Train')]
# SUNDANCE, printed twice: blue (a square) from the warming huts down to Teddy's Way, green (two circles) below; the
# report has one Sundance, intermediate: one trail, blue
RATING = {'Sundance': 'square'}
DISPLAY = dict(TOP.DISPLAY)
GLADES = set()
PARKS = set(TOP.PARKS)
DEFAULT_SYMBOL = {'Hoot Brown Terrain Park': 'square'}  # (a park, printed with no symbol: blue, as the report rates it)
NO_LINE = {}
