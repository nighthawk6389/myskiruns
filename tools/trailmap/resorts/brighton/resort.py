"""Brighton Resort's 2025-26 trail map (brightonresort.com's trail-maps page: one Illustrator page): James Niehues's
painting under 0.8 pt strokes in the runs' colours (green, blue, black; the parks orange), every name printed along
its run's line in Eurostile Condensed Heavy, outlined black glyphs (five set as text) on a white halo, the symbol on
the line by it; a few expert runs (bowls, chutes) a name and a diamond with no line. Read by
tools/trailmap/pdf_resort.py; prepare.py extracts it."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CLIP = (0, 0, 864, 648)  # PDF points: the whole page
SCALE = 4.0  # map px per PDF point (the painting is 312 dpi: 4.3 px per point)
SOURCE = ('Brighton 2025-26 trail map PDF (brightonresort.com): green, blue, black and orange 0.8 pt strokes, '
          'tools/trailmap/resorts/brighton/prepare.py; percent of the map image')
SYMBOL_REACH = 10  # pt from a name's first or last letter to its symbol
END_REACH = 8  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 5  # pt: a name printed beside its line
NO_STRETCH_BESIDE = True  # names printed beside their line (Face, Candyland) as well as in gaps of it: no stretch

# the trail report (report.json: the resort's reportpal), its lift areas, each with its lift's top (OpenStreetMap's
# lift lines on the USGS's 10 m elevation model, tools/trailmap/lift_tops.py); the parks their own area
AREAS = [('great-western', 'Great Western Express', 10446), ('snake-creek', 'Snake Creek Express', 10138),
         ('crest', 'Crest 6', 9969), ('milly', 'Milly Express', 9852), ('majestic', 'Majestic', 9481),
         ('explorer', 'Explorer', 8888), ('terrain-park', 'Terrain Park', 9481)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}
REPORT = json.load(open(os.path.join(HERE, 'report.json')))['trails']
NAMES = sorted({n for n, _a, _r in REPORT})
AS_PRINTED = False
AREA_OF = {}
for _n, _a, _r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])
# names the map prints that the report doesn't list, each in the lift area it is reached from
AREA_OF.update({'Elk Park Access': 'great-western', "Wally's World": 'great-western',
                'Boundary Chute': 'great-western', 'Great Western': 'great-western', "Rockin' R": 'great-western',
                'Hawkeye Access': 'majestic', 'Scree Slope': 'milly', 'Scree Chute': 'milly',
                'Diagonal Chute': 'milly', 'Elevator': 'milly', 'Boll Weevil': 'milly', 'Spaghetti': 'milly',
                'Captain Hook': 'milly', 'Sol Bright Access': 'milly', 'Slalom Hill': 'milly'})
PARKS = {'My-O-My', 'Candyland', 'Pee-Wee'}
GLADES = set()


def is_name(label):
    """The runs' names, in upper and lower case; the peaks', the areas' and the base's are capitals (and SS
    Traverse's SS, joined to its second line)."""
    return any(ch.islower() for ch in label['text']) or label['text'] == 'SS'


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


COLOR_SYMBOL = {}
# names printed on two lines, in reading order
JOIN = [('Snake', 'BowI'), ('Captain', 'Hook'), ('SoI Bright', 'Access'), ('BoII', 'WeeviI'), ('Chicken', 'Out'),
        ('SS', 'Traverse')]
JOIN_GAP = 10  # pt
TWO_LINE = {' '.join(p) for p in JOIN} - {'SS Traverse'}
# two names read as one run of glyphs (2nd Face printed on from Majestic Main's last letter)
SPLIT = {'Majestic Main 2nd Face': ('Majestic Main', '2nd Face')}
NO_STRETCH = {'Shoulder', 'Slalom Hill'}  # printed beside their lines (below Slalom Hill's, left of Shoulder's)
LABEL_LINE = set()
DROP = [('Designated Ski Area Boundary', None)]
# the font draws M and W as one shape turned over, and i, l and I (their dots apart) as one: what the glyphs misread,
# and the map's spellings that the report spells otherwise
RENAME = {'Snake BowI': 'Snake Bowl', 'SoI Bright Access': 'Sol Bright Access', 'BoII WeeviI': 'Boll Weevil',
          "Plck'Em U p": "Pick 'Em Up", 'Mary Maln': 'Mary Main', 'True Grlt': 'True Grit',
          'Majestlc Access': 'Majestic Access', 'Elk Par k Access': 'Elk Park Access', 'Mintergreen': 'Wintergreen',
          'Mrangler': 'Wrangler', 'Mestern Trail': 'Western Trail', 'Wary Back': 'Mary Back',
          'Materfall': 'Waterfall', 'Wary Maln': 'Mary Main', 'Race Course': 'Racecourse (Snake Creek Access)'}
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
# symbols printed by a name but nearer another's end (map px)
SYMBOL_OF = [((1289, 937), 'Pick Em Up'),  # its circle where its line leaves the light-bulb sign (Great Divide's
             # name starts there too, on its blue line)
             ((1469, 765), 'Hard Coin'), ((3003, 983), 'Lone Pine'), ((2824, 1176), "Randy's Chute"),
             ((1942, 1452), 'Cat Track'),  # its square at its line's top, by Mary Back's name's end
             ((1556, 1611), 'Powder Alley'),  # its square at the top of its line (SS Traverse's foot)
             ((3023, 1803), 'Spaghetti')]  # its diamond over the middle of its name
RATING = {}
# names printed with no symbol (the playbook's conventions): a line's colour (Great Divide's and Mary Back's), a
# bowl's or a glade's black, the report's rating where it lists the name (Snake Bowl, Milly Bowl), a chute between
# double-black chutes their double black (Diagonal Chute), Elevator as Milly Bowl, the bowl it is printed in
DEFAULT_SYMBOL = {'Great Divide': 'square', 'Mary Back': 'circle', 'Snake Bowl': 'double-diamond',
                  'Milly Bowl': 'diamond', "Wally's World": 'diamond', 'Elevator': 'diamond',
                  'Diagonal Chute': 'double-diamond'}
DISPLAY = {}
NO_LINE = {}
