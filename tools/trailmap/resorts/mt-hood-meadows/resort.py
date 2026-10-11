"""Mt. Hood Meadows' 2025-26 trail map (skihood.com's Trail_Map_20x17_2025_26 PDF, its second page: the map; the
first is its back): the painting and everything on it are vectors (no image), the runs 0.69 pt strokes in their
colours (green, blue, black), every name printed along its run's line, in a gap of it, in outlined near-black
glyphs (one name, Dallas Bowl, set as text; Memorial Bowl's glyphs a shade darker), its symbol on the line by it;
the bowls and canyons above the trees a name and a diamond with no line. Read by tools/trailmap/pdf_resort.py;
prepare.py extracts it."""
import re

CLIP = (290, 0, 1440, 1224)  # PDF points: the map, right of the text column
SCALE = 3.0  # map px per PDF point
SOURCE = ('Mt. Hood Meadows 2025-26 trail map PDF (skihood.com): green, blue and black 0.69 pt strokes, '
          'tools/trailmap/resorts/mt-hood-meadows/prepare.py; percent of the map image')
SYMBOL_REACH = 12  # pt from a name's first or last letter (or its middle) to its symbol
SYMBOL_CENTRE = True  # the bowls', canyons' and cliffs' names print their symbol under (or over) their middle
END_REACH = 8  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 5  # pt: a name printed beside its line

# the lifts (the app's areas), each with its top: as printed on the map (Cascade Express, Vista Express, Shooting
# Star Express, Mt. Hood Express), else OpenStreetMap's lift line on the USGS's 10 m elevation model
# (tools/trailmap/lift_tops.py; the map prints 5,949', 5,958' and 5,928' at the three tops beside Stadium Express's)
AREAS = [('cascade', 'Cascade Express', 7305), ('vista', 'Vista Express', 6568),
         ('shooting-star', 'Shooting Star Express', 6562), ('mt-hood-express', 'Mt. Hood Express', 6548),
         ('daisy', 'Daisy', 6026), ('heather', 'Heather', 5955), ('stadium', 'Stadium Express', 5931),
         ('hood-river', 'Hood River Express', 5931), ('easy-rider', 'Easy Rider', 5863)]
# each name's lift, read on the map: the lift whose top it is skied from (the gated bowls right of Heather Canyon's
# orange boundary, and Clark Canyon's and the Private Reserve's, with Heather, whose lift brings them back)
_AREAS = {
    'cascade': ['SUPERBOWL', 'DALLAS BOWL', 'TEXAS TRAILS', 'CATACOMBS', 'GULCH', 'ARENA', 'MARMOT RIDGE',
                'SUNBURST', 'ELEVATOR', 'LOWER ELEVATOR', 'OUTER LIMITS', 'BOULEVARD'],
    'vista': ['THE ZOO', 'MITCHELL CREEK', 'VISTA RIDGE', 'I HEAR CARS', 'SUNRISE PARKING RUNOUT', 'MY TY', 'JIGSAW',
              'LUCKY LADY', "NATE'S WAY", "NATE'S OTHER WAY", 'SOUTH CANYON', 'DENTAL FLOSS', 'GINGIVITIS'],
    'easy-rider': ['FIREWEED', 'NASTAR PARK', 'NASTAR HILL', 'SUPERPIPE', 'WALL FLOWER', 'BANKED SLALOM'],
    'daisy': ['DAISY BOWL', 'SPEEDWELL', 'WATERFALL', 'BEAVER TAIL'],
    'mt-hood-express': ['WHOOPEE', '1 BOWL', '1½ BOWL', '2 BOWL', '3 BOWL', '4 BOWL', '5 BOWL', 'RESERVOIR HILL',
                        'CASCADE SKIWAY', 'CHUNKY SWIRLY', 'SHOW OFF', 'RIDGE RUN', 'LOWER FACE', 'BLUE FACE',
                        'WEE BEE GEE BEE', "JACOB'S LADDER", 'POWDER KEG', 'MIDDLEFORK', 'BREEZEWAY',
                        'NORTH CANYON', 'ROACH BOWL', "ERIC'S CORNER"],
    'stadium': ['STADIUM', "RAM'S HEAD", 'TRILLIUM'],
    'hood-river': ['FRIGHT TREES', 'FOREST PARK', 'LADY SLIPPER', 'LADY SLIPPER BOWL', 'LADY FINGER', 'TAMARACK',
                   'KNOT HOLE', 'KINNIKINICK', 'WILLOW', 'WY EAST', 'SKILLIT', 'SKIWAY', 'BREAKAWAY',
                   'LOWER OUTRIGGER', 'OUTRIGGER', 'PIPELINE', 'PICNIC ROCK'],
    'shooting-star': ['INNER LIMITS', 'DISCOVERY RIDGE', 'DISCOVERY', "NETTIE'S RUN", 'MERCURY', '3D', 'O-RING',
                      'ROCK GARDEN', 'TILLICUM', 'VOYAGER', 'GEMINI', 'SHOOTING STAR RIDGE', 'APOLLO', 'COLUMBIA',
                      'TITAN'],
    'heather': ['HEATHER CANYON', 'CLARK CANYON', 'A-ZONE', 'SILVER BOWL', 'GOLD BOWL', 'DIAMOND BOWL',
                'MEMORIAL BOWL', 'TWILIGHT BOWL', 'PLUTO', 'MOON BOWL', '½ MOON BOWL', 'HIGHLANDS', 'LOWLANDS',
                'HEATHER WOODS', 'SUNRISE BOWL', 'HAMMER BOWL', 'CONAN BOWL', 'HINTERLANDS', 'ACCORDION BOWL',
                'ABSOLUTE MAGNITUDE', "JACK'S WOODS", 'HEATHER CANYON RUNOUT', 'PRIVATE RESERVE', 'ELK CLIFFS',
                'ELK BOWL', 'YODA BOWL', "GOD'S WALL", 'MINI GODS', 'RESCUE HILL', 'S&R CLIFFS', "JD'S",
                'THE CURTAINS', 'FBW', 'ENDOR'],
}
AREA_OF = {n: a for a, ns in _AREAS.items() for n in ns}


def area(c):
    raise ValueError(f'a name at {c} with no lift: give it one in _AREAS')


def is_name(label):
    """The runs' names: all of the near-black glyphs and text in the map (lifts, elevations, buildings and notices
    are in other colours or fonts)."""
    return label.get('font') == 'glyph' or label['text'] == 'DALLAS BOWL'


# names printed in parts, in reading order
JOIN = [("NATE'S", 'OTHER', 'WAY'), ('S&R', 'CLIFFS'), ('THE', 'CURTAINS'), ('BANKED', 'SLALOM'),
        ('NASTAR', 'PARK')]
JOIN_GAP = 10  # pt
TWO_LINE = {' '.join(p) for p in JOIN}
NO_STRETCH = set()
LABEL_LINE = set()
DROP = []
# the glyphs' shapes are read turned any way, so I and the hyphen are one shape, and so are the hyphen and the
# apostrophe: the names they misread
RENAME = {'PR-VATE RESERVE': 'PRIVATE RESERVE', "A'ZONE": 'A-ZONE', "O'RING": 'O-RING',
          "NETTIES'S RUN": "NETTIE'S RUN",
          # two words set close (the reading saw no gap)
          'SHOWOFF': 'SHOW OFF', 'KNOTHOLE': 'KNOT HOLE'}
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
RATING = {}
DEFAULT_SYMBOL = {}
# the parks (orange on the map: The Zoo, Nastar Park and Forest Park's S/M/L features, the Superpipe, the Banked
# Slalom course)
PARKS = {'THE ZOO', 'NASTAR PARK', 'FOREST PARK', 'SUPERPIPE', 'BANKED SLALOM'}
GLADES = set()
# as the resort spells them (title case would lower these)
DISPLAY = {'NASTAR HILL': 'NASTAR Hill', 'NASTAR PARK': 'NASTAR Park', 'S&R CLIFFS': 'S&R Cliffs', "JD'S": "JD's",
           'FBW': 'FBW', '3D': '3D'}
NO_LINE = {}
