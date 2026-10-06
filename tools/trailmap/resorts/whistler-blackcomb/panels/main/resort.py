"""Whistler Blackcomb, the main map (the PDF's second page): Blackcomb on the left, Whistler on the right. Trail
lines are strokes in the difficulty colours; each name is printed in its run's colour with its symbol before it,
along its line or in a gap of it. Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import re


CLIP = (0, 0, 1728, 841)  # PDF points: the map above the info bands
SCALE = 2.5  # map px per PDF point
SOURCE = ('Whistler Blackcomb 2025-26 trail map PDF (whistlerblackcomb.com, the Mountain Atlas), main map: 1.07 and '
          '1.6 pt green, blue, black and purple strokes, tools/trailmap/resorts/whistler-blackcomb/prepare.py; '
          'percent of the map image')
SYMBOL_REACH = 8  # pt from a name's first or last character to its symbol
END_REACH = 5  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 4.5  # pt: a name printed beside its line, about a character's height off it
ALONG_NEAREST = True
GLADE_LINES = True  # glades are black lines under white dashes (prepare.py marks them)
NO_STRETCH_BESIDE = True  # names printed beside their line get no stretch along their characters

# text in the names' style that isn't a run: notes, places, peaks and lodges, lifts and their stations, elevations
NOT_NAMES = ('ELEVATION', 'PERMANENTLY', 'CLOSED AREA', 'PROVINCIAL', 'GARIBALDI', 'LIFT', 'EXPRESS', 'GONDOLA',
             'CHAIR', 'T-BARS', 'MID STATION', 'SNOW SCHOOL', 'LEARNING AREA', 'LEARNING CENTRE', 'TRAINING',
             'CENTRE')
DROP_EXACT = {  # (after the names printed in parts are joined)
    'CLIFF', 'AREA', 'CLIFF AREA', 'BLACKCOMB PEAK', 'SYMPHONY', 'LITTLE WHISTLER PEAK', 'FISSILE',
    'OVERLORD GLACIER', 'SPEARHEAD', 'HORSTMAN HUT', 'CRYSTAL HUT', 'SNOWMAKING', 'RESERVOIR', 'THE CHIC PEA',
    'FITZSIMMONS CREEK', 'OLYMPIC', 'BASE 2', 'BLACKCOMB BASE', 'PARK', 'P ARK', 'BLACKCOMB', 'GLACIER', 'ACCESS TO',
    'S+M', 'XL', 'ML-', 'M', 'L', 'S', 'LOWER', 'GARNET, DIAMOND,', 'RUBY & SAPPHIRE', 'BOWLS', 'DAVE MURRAY',
    'NATIONAL TRAINING', 'GEMINI', 'FREESTYLE', 'RETURN ROUTE', 'FROM SYMPHONY', 'TO HARMONY', 'FROM 7TH HEAVEN',
    'TO PEAK 2 PEAK', 'WHISTLER ADAPTIVE CENTRE', 'TO SUN BOWL', 'FLUTE BOWL', 'HORSTMAN', 'MID STATIOZ', '-',
    'ROADS', 'ENTRANCE TO GARNET, DIAMOND, RUBY & SAPPHIRE BOWLS'}


def is_name(label):
    t = ' '.join(label['text'].split())
    if label.get('color') not in ('green', 'blue', 'black', 'purple', 'park') or label['text'].count('*'):
        return False
    return not any(re.search(rf'\b{w}\b', t) for w in NOT_NAMES)  # (EXPRESSWAY is a run)


# names printed in parts (on two or three lines), in reading order
JOIN = [('ENTRANCE TO', 'GARNET, DIAMOND,', 'RUBY & SAPPHIRE', 'BOWLS'), ('ENTRANCE TO', 'BLACKCOMB GLACIER'),
        ('ENTRANCE TO', 'GREY ZONE'), ('SPANKY’S', 'LADDER'), ('SOUTHSIDE', 'GREEN'), ('CATSKINNER', 'TRAVERSE'), ('DOWNLOAD', 'ROAD'), ('COUGAR', 'CHUTE'),
        ('CRYSTAL', 'GLIDE'), ('NORTHERN', 'LIGHTS'), ('BOBCAT AND', 'CHIPMUNK PARK'), ('ENCHANTED', 'FOREST'),
        ('BERNIE’S', 'BUMPS'), ('CLOSED', 'CAPTIONS'), ('GLACIER', 'BOWL'), ('WHISTLER', 'BOWL'), ('CAMEL', 'HUMPS'),
        ('HARMONY', 'HORSESHOES'), ('LOW', 'ROLL'), ('STEFAN’S', 'CHUTE'), ('DOOM &', 'GLOOM'), ('SECRET', 'BOWL'),
        ('SECRET', 'CHUTE'), ('BROWNLIE', 'BASIN'), ('JERSEY CREAM', 'BOWL'), ('JERSEY CREAM', 'WALL'),
        ('BARK', 'SANDWICH'), ('DAVIES', 'DERVISH'), ('LOG', 'JAM'), ('RIDER’S', 'REVENGE'), ('GNARLY', 'KNOTS'),
        ('TREE', 'FORT'), ('UPPER', 'WHISKEY', 'JACK'), ('LOWER', 'RATFINK'), ('CROSS', 'ROADS'),
        ('LITTLE', 'WHISTLER'), ('HORSTMAN', 'FACE'), ('ROCK', 'ALLEY'), ('T-BAR', 'BOWL'),
        ('SHOWCASE', 'BOWL'), ('PALE', 'FACE'), ('KID', 'TRAIL'), ('DAVE MURRAY DOWNHILL', '-', 'LOWER')]
# two names drawn as one run of glyphs: Glacier Drive (reading down) ends where The Bite (reading up) starts
SPLIT = {'GLACIER DRIVE THE BITE': ('GLACIER DRIVE', 'THE BITE')}
TWO_LINE = set()
NO_STRETCH = {'SEPPO’S - LOWER'}  # printed across its line
# names printed over their whole line but for a stub, its end hidden under the label (no line end at the name): the
# stretch along the name is the run (Rabbit Tracks: from below Pika's Traverse to its symbol, then the stub to G.S.,
# as the resort's ArcGIS run line goes)
LABEL_LINE = {'RABBIT TRACKS'}
DROP = [(t, None) for t in sorted(DROP_EXACT)]
# (Greenline is printed GREENLINE above Catskinner and GREEN LINE further down its dashed line, and Kadenwood Trail
# KADENWOOD TRAIL and KADENWOOD by the Kadenwood houses: one run each on the resort's trail report)
RENAME = {'CROSS': 'CROSS ROADS', 'H/GHESTLEVEL': 'HIGHEST LEVEL', 'GREY L/NE': 'GREY LINE', 'CHOKERPARK': 'CHOKER PARK',
          'GREEN LINE': 'GREENLINE', 'KADENWOOD': 'KADENWOOD TRAIL'}
# names printed twice with two symbols, two runs on the resort's trail report: Seppo's (black) above Seppo's - Lower
# (blue); Mainline - Upper (blue) above Mainline - Lower (green). And Expressway, a run on each mountain (the report
# lists both): Whistler's is a trail of its own, shown as Expressway (DISPLAY)
RENAME_AT = [((2505, 1211), 'SEPPO’S', 'SEPPO’S - LOWER'), ((1457, 1507), 'MAINLINE', 'MAINLINE - UPPER'),
             ((1636, 1614), 'MAINLINE', 'MAINLINE - LOWER'), ((2852, 1472), 'EXPRESSWAY', 'EXPRESSWAY (WHISTLER)')]
EXTRA = []
SYMBOL_FIX = []
# ((x, y), NAME): a symbol printed beside its name but out of SYMBOL_REACH: Bernie's Bumps' diamond above it, Cougar
# Chute's double diamond a little before it; and Green Acres' square, as close to the end of the Bobcat and Chipmunk
# Park pill before it (a park's pill carries no symbol)
SYMBOL_OF = [((4071, 479), 'BERNIE’S BUMPS'), ((865, 708), 'COUGAR CHUTE'), ((2586, 760), 'GREEN ACRES')]
LOOSE_SYMBOLS = ('the symbols of the pointer labels To Sun Bowl and Access to Flute Bowl, of Flute Bowl (named on '
                 'the Symphony panel) and a small double diamond by the top of the Peak chair, with no name')
# names printed with no symbol and no line to colour them (seed_roster.py would make them blue), as the resort's own
# trail report rates them: Showcase Bowl and Brownlie Basin black; the family areas Magic Castle and Tree Fort green;
# the kids' trail at the Blackcomb base green; the adventure trails Enchanted Forest and School Yard blue
DEFAULT_SYMBOL = {'SHOWCASE BOWL': 'diamond', 'BROWNLIE BASIN': 'diamond', 'MAGIC CASTLE': 'circle', 'TREE FORT': 'circle', 'KID TRAIL': 'circle',
                  'ENCHANTED FOREST': 'square', 'SCHOOL YARD': 'square'}
DISPLAY = {'EXPRESSWAY (WHISTLER)': 'Expressway'}
GLADES = set()
NOT_GLADES = {'THE GLADES'}  # a groomed blue run, drawn as one (the map's glades have white dashes)
PARKS = {'HIGHEST LEVEL', 'GREY LINE', 'CHOKER PARK', 'SNOW CROSS', 'BOBCAT AND CHIPMUNK PARK'}
NO_LINE = {}


def area(c):
    """The area (AREAS id) of a name printed at c (map px): Blackcomb left of the Fitzsimmons valley (Village Run is
    its rightmost name), Whistler right of it (Lower Olympic its leftmost), as the resort's trail report groups them."""
    return 'blackcomb' if c[0] < 2050 else 'whistler'
