"""Arapahoe Basin, the frontside panel: the Frontside & The Beavers painting (the page below the Zuma Bowl frame), with
Pallavicini, the Steep Gullies and the East Wall. Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('arapahoe_basin', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (0, 523, 1296, 1294.58)  # PDF points: the painting below the Zuma Bowl frame (the title band's foot above it)
SCALE = 3.5  # map px per PDF point
SOURCE = ('Arapahoe Basin 2025-26 trail map PDF (arapahoebasin.com), the Frontside & The Beavers: 0.5 pt black, blue '
          'and green strokes, tools/trailmap/resorts/arapahoe-basin/prepare.py; percent of the map image')
SYMBOL_REACH = 12  # pt from a name's first or last letter (or its middle) to its symbol
SYMBOL_CENTRE = True  # some names printed level with their symbol under or over their middle (LAND OF THE GIANTS)
END_REACH = 8
ALONG = 5
ALONG_NEAREST = True
ALONG_FIRST = True
NO_STRETCH_BESIDE = True

NAMES, AREA_OF, AS_PRINTED = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED
is_name = TOP.is_name


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


# names printed in parts (on two lines), in reading order
JOIN = [('MOUNTAIN GOAT', 'ALLEY'), ('HALF MOON', 'GLADES'), ('PIKA', 'PLACE'), ('NORTHPOLE', 'HIKING GATE')]
TWO_LINE = {' '.join(p) for p in JOIN}
JOIN_GAP = 10
NO_STRETCH = set()
# runs the map draws no line for, the name printed down the run from its symbol: the stretch along the name is the
# run's overlay (as Heavenly's); the faces, chutes, gullies, glades, woods and trees with no line, the names printed
# level (LAND OF THE GIANTS, LOWER EAST WALL, PALLAVICINI, BALD SPOT, THE CELLAR) and those on two lines are markers
LABEL_LINE = {
    "1st Alley - David's Run", '2nd Alley', '3rd Alley', '4th Alley (West Alley)', 'Alex', 'Bailey Bros.',
    'Bear Trap', 'Bighorn', 'Castor', 'Challenger', 'Digger', 'Dreamcatcher', 'Drummond', 'East Avenue',
    'Exhibition', 'Faculty Club', 'Falcon', 'Gauthier', 'Gentry', 'Hauk', 'Humbug', 'Jaeger', 'Janitors Only',
    'Jetta', 'King Cornice', 'Knolls', 'Lenawee Parks', 'Lynx Lane', 'Molly Hogan', 'No Name', 'North Fork',
    'North Pole', 'Norway Mountain Run', 'Nose', 'Peaceful Valley', 'Pioneer Willy', 'Porcupine', 'Powder Keg',
    'Powerline', 'Radical', 'Rock Garden', 'Roller Coaster', 'Scudder', 'Slalom Slope', 'Snorkel Nose', 'The Gulch',
    'The Spine', 'Thick & Thin', 'Tinker Toy', "Todd's Ridge", 'Turbo', 'West Turbo', 'Wildcat', "Willy's Wide"}
# labels that name no run (map px): the summer activities, the base area's lots, buildings and decks, the peaks and
# elevations, the hiking gate, the hike-back trail (an uphill walk), and the letters of the area titles' boxes
DROP = [(t, None) for t in (
    'VIA FERRATA', 'SUMMER', 'GUIDED EXPERIENCE', 'AERIAL', 'ADVENTURE', 'PARK', 'SUMMER EXPERIENCE', 'DROP OFF',
    'EARLY RISER', 'LAST CHANCE', 'PEDESTRIAN', 'TUNNEL', 'UPPER', 'PARKING EXIT', 'UPPER PARKING LOT', 'ENTRANCE',
    'BEAVERBOWL DECK', 'DOGWOODS DECK', 'ARAPAHOE BASIN', 'LENAWEE MOUNTAIN', 'BASE AREA', 'ELEVATION', 'MOUNTAIN',
    'GOAT PLAZA', "' - 3'978 m", "' - 4'2O5 m", "13'O5O - 3'978 m", "13'2O4 - 4'2O5 m", "1O'78O - 3'286 m",
    "1O'52O - 3'2O7 m", 'NORTHPOLE HIKING GATE', 'STEEP GULLIES HIKE BACK', 'HET', 'ES', 'GU', 'EE', 'LL', 'TS', 'AW',
    'TE', 'NO', 'EA', 'EH')] + [('HIGH NOON', (1218, 2286))]  # (the High Noon parking lot)
RENAME = dict(TOP.RENAME)
# CHISHOLM, printed three times: by the lodge Upper Chisholm Trail, the two below Lower Chisholm Trail (the report's)
RENAME_AT = [((1533, 1260), 'CHISHOLM', 'Upper Chisholm Trail'), ((1060, 1673), 'CHISHOLM', 'Lower Chisholm Trail'),
             ((1043, 1932), 'CHISHOLM', 'Lower Chisholm Trail')]
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
RATING = {}
DISPLAY = dict(TOP.DISPLAY)
GLADES = set()
PARKS = set()
NO_LINE = {}
# names printed with no symbol: the Steep Gullies' the area's EX (printed under THE STEEP GULLIES and in its note:
# "EX ONLY"); East Wall Traverse and Grand Portage their line's black
DEFAULT_SYMBOL = {**{f'SG {k}': 'double-diamond' for k in range(1, 6)}, 'East Wall Traverse': 'diamond',
                  'Grand Portage': 'diamond'}
