"""Crested Butte, the main panel: the 2025-26 trail map PDF's second page (James Niehues's painting under filled
outlines and outlined names in the runs' colours). Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts
it."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('crested_butte', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (0, 0, 1436, 946)  # PDF points: the page left of the legend, above the partners' band
SCALE = 3  # map px per PDF point
SOURCE = ('Crested Butte 2025-26 trail map PDF (skicb.com), page 2: the centre lines of the blue, green and black '
          'outlines, tools/trailmap/resorts/crested-butte/prepare.py; percent of the map image')
SYMBOL_REACH = 16  # pt from a name's first or last character (or its middle) to its symbol
SYMBOL_CENTRE = True  # the extreme terrain's EX printed above the middle of its name
END_REACH = 11  # pt from a name's end (or its symbol) to the end of the line that runs into it (wide halos, EZ signs in the gaps)
ALONG = 9  # pt: a piece this close to most of a name's characters runs along it
ALONG_NEAREST = True  # names printed beside their line, between parallel ones: the nearest only

NAMES, AREA_OF, AS_PRINTED = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED
is_name = TOP.is_name


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


# names printed in parts (on two or three lines, or either side of a line crossing them), in reading order; a part
# (text, (x, y)) is the label printing it nearest that point (map px)
JOIN = [('Teocalli 2', 'Bowl'), ('Teocalli', ('Bowl', (1584, 422))), ('Halfpipe', ('Gully', (1887, 369))),
        ('Powder 8', ('Gully', (1801, 464))), ('Big', 'Chute'), ('Paradise', 'Cliffs'),
        (('Banana', (2267, 422)), 'High', 'Entrance'), (('Upper', (2530, 544)), 'Peel'),
        (('Upper', (2619, 630)), ('Forest', (2618, 660))), ('Sunset', 'Ridge'), ('Hot', 'Rocks'), ('Hockey', 'Rink'),
        ('Schofield', 'Road'), (('Ruby', (2029, 701)), ('Road', (2112, 718))), ('Silver Queen', 'Road'),
        (('Upper', (2038, 940)), ('Ruby', (2024, 850)), ('Chief', (1979, 777))),
        (('Paradise', (1768, 744)), ('Bowl', (1770, 777))), (('Upper', (1833, 998)), 'Canaan'),
        (('Houston', (1887, 1095)), ('Access', (1929, 1189))), (('Lower', (1684, 1359)), 'Forest Queen'),
        ('Lower Ruby', ('Chief', (1847, 1256))), (('Paradise', (1621, 1623)), ('Access', (1730, 1553))),
        (('Upper', (1556, 1733)), ('Conundrum', (1549, 1766))), (('Middle', (1289, 1862)), 'Gallowich'),
        ('Rosebush', ('Glades', (1753, 1813))), ('Gus’', 'Way'), ('Black', 'Eagle'),
        (('Gully', (745, 1606)), ('Glades', (818, 1546))), ('Double Top', ('Glades', (882, 1558))),
        ('Git Some', ('Glades', (844, 1672))), ('Bakery', 'Trees'), ('Easy', 'Out'), ('Last', 'Steep'),
        ('Sock It To', 'Me', ('Ridge', (899, 1299))), (('Phoenix', (642, 1181)), ('Bowl', (642, 1214))),
        (('Phoenix', (782, 1209)), 'Steps'), (('Lower', (308, 1211)), ('Third', (263, 1238)), ('Bowl', (351, 1241))),
        (('Third', (372, 1060)), ('Bowl', (376, 1103))),
        (('Upper', (525, 866)), ('Third', (479, 902)), ('Bowl', (567, 904))), (('High', (650, 787)), 'Nowhere'),
        (('Spellbound', (819, 855)), ('Bowl', (826, 889))), (('Spellbound', (904, 950)), ('Glades', (906, 984))),
        ('Hawks', 'Nest'), (('The', (1101, 882)), ('North', (1182, 883)), ('Face', (1149, 919))), ('Old', 'Pro'),
        ('Hard', 'Slab'), (('The', (1496, 1045)), ('Glades', (1497, 1078))), ('Tower 11', 'Chutes'),
        ('Yellow', 'Brick', ('Road', (2416, 936))), ('Bubba’s', 'shortcut'), ('Roller', 'Coaster'),
        (('Horseshoe', (2202, 1081)), 'Springs'), (('Middle', (2617, 1116)), ('Twister', (2604, 1139))),
        (('Lower', (2800, 1313)), ('Twister', (2869, 1431))), (('Aspen', (2819, 1116)), ('Park', (2901, 1114)),
                                                                ('Road', (2974, 1116))),
        (('Upper', (3105, 1148)), ('Championship', (3123, 1183))),
        (('Middle', (3245, 1227)), ('Championship', (3267, 1256))), (('Banana', (3461, 1124)), 'Exit'),
        ('Upper Smith', ('Hill', (2597, 1392))), ('Lower Smith', ('Hill', (2939, 1607))), ('Big', 'Al’s'),
        ('Poverty', 'Gulch'), ('Gunsight', ('Pass', (2336, 1877))), ('Little', 'Queen'), ('Twin', 'Bridges'),
        ('Elko', ('Park', (2841, 2165))), ('Panion’s', 'Run'), (('North', (3155, 1952)), ('Pass', (3209, 2019))),
        ('Alley', 'Loop'), ('Mary', 'Jo'), ('Grand', 'Traverse'), ('Elk', 'Ave.'), ('Columbine', ('Hill', (3578, 1791))),
        ('Warming', 'House', ('Hill', (3936, 1743)))]
TWO_LINE = {'Teocalli 2 Bowl', 'Teocalli Bowl', 'Halfpipe Gully', 'Paradise Cliffs', 'Upper Peel', 'Upper Forest',
            'Hockey Rink', 'Paradise Bowl', 'Upper Canaan', 'Upper Conundrum', 'Middle Gallowich', 'Rosebush Glades',
            'Bakery Trees', 'Easy Out', 'Last Steep', 'Phoenix Bowl', 'Phoenix Steps', 'Lower Third Bowl',
            'Third Bowl', 'Upper Third Bowl', 'High Nowhere', 'Spellbound Bowl', 'Spellbound Glades', 'Hawks Nest',
            'The North Face', 'Hard Slab', 'The Glades', 'Tower 11 Chutes', 'Bubba’s shortcut', 'Horseshoe Springs',
            'Middle Twister', 'Upper Championship', 'Middle Championship', 'Mary Jo', 'Grand Traverse', 'Elk Ave.',
            'Sock It To Me Ridge', 'Old Pro', 'Sunset Ridge', 'Hot Rocks', 'Big Al’s', 'Lower Twister'}
JOIN_GAP = 30  # pt between two parts' nearest letters (big capitals 10 apart; LOWER over TWISTER 17; ROLLER and COASTER either side of a dash of their line 27)
NO_STRETCH = set()
LABEL_LINE = set()
# labels that name no run: the easiest-way-down signs (EZ), the restaurants (The Umbrella Bar at Ten Peaks, Butte
# 66), logos
DROP = [(t, None) for t in ('EZ', 'The', 'Umbrella Bar', 'AT TEN PEAKS', '66', 'BUTTE', '**', '***')]
# printed otherwise than the report spells them
RENAME = {**TOP.RENAME, 'Teocalli 2 Bowl': 'Teo 2', 'Halfpipe Gully': 'Halfpipe', 'Houston Access': 'Houston’s Access',
          'Rubysteep': 'Ruby Steep', 'RubyAccess': 'Ruby Access', 'HighTide': 'High Tide', 'Roosters': 'Roosters Run',
          'Fredo’s': 'Fredo’s North Face Cliffs', 'Spellbound Glades': 'Spellbound Glade', 'Alley Loop': 'Ally Loop',
          'Keystone': 'Upper Keystone', 'North star': 'Lower North Star', 'Bubba’s shortcut': "Bubba's Shortcut"}
RENAME_AT = []
# the terrain parks: their names white on orange pills (in the lifts' black, no glyphs of a name colour), at the pill
EXTRA = [('Painter Boy Park', 2655, 1726), ('Lower Twister Terrain Park', 3104, 1508)]
SYMBOL_FIX = []
# symbols printed on their run's line away from its name: each run's square at its start (its name further down the line)
SYMBOL_OF = [((1924, 1404), "Gus' Way"), ((1571, 1283), 'Upper Gallowich'), ((1620, 1295), 'Lower Canaan'),
             ((1675, 1480), 'Lower Ruby Chief'), ((1361, 1633), 'Middle Gallowich'), ((1942, 705), 'Upper Ruby Chief'),
             ((1979, 896), 'Yellow Brick Road'), ((3596, 1687), 'Warming House Hill'),
             ((897, 1231), 'Sock-It-To-Me Ridge'),
             ((2264, 641), 'Triangle'), ((1573, 666), 'Schofield Road'), ((3993, 1716), 'High Tide')]  # (its diamond above its name's legs; a dash below it reads as a diamond)
RATING = {}
DISPLAY = dict(TOP.DISPLAY)
GLADES = set()
PARKS = set(TOP.PARKS)
# names printed with no symbol (crops): rated as the report rates them
DEFAULT_SYMBOL = {'Avery': 'diamond', "Eflin's Way": 'diamond', 'Lower North Star': 'diamond', 'Mach 1': 'diamond',
                  "Robel's": 'diamond', 'Easy Out': 'double-diamond', 'Banana High Entrance': 'double-diamond',
                  'Silver Queen Road': 'square',
                  # not in the report; between Upper and Lower Championship (diamonds) on their black line
                  'Middle Championship': 'diamond'}
NO_LINE = {}
