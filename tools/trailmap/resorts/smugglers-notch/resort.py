"""Smugglers' Notch's trail map (smuggs.com, the 2024-25 artwork, still the map the resort links): one vector PDF
page over a low-resolution painting. Trail lines are strokes in the difficulty colours; names are white outlined
glyphs on label boxes in the run's colour, on the line or off it with a leader line to the line or to a glade's
hollow circle. prepare.py extracts it; read by tools/trailmap/pdf_resort.py."""

CLIP = (0, 0, 1695, 1146)  # PDF points: the map, left of the key panel
SCALE = 2.5  # map px per PDF point
SOURCE = ("Smugglers' Notch trail map PDF (smuggs.com, trailmap_2425.pdf): 3.44 pt green, blue and black strokes, "
          'tools/trailmap/resorts/smugglers-notch/prepare.py; percent of the map image')
SYMBOL_REACH = 0  # the only symbols are the experts' diamond chains, on the line away from the name
END_REACH = 4
ALONG = 3  # pt: a label box sits on its line
ALONG_NEAREST = True
MATCH_ENDS = False
ON_CIRCLE = 3.5  # pt: a leader stops at the edge of its line: its far end names the line under it
JOIN_GAP = 10  # pt: the parks' names are three lines in a box
COLOR_SYMBOL = {'green': 'circle', 'blue': 'square', 'black': 'diamond'}  # a name's rating is its label box's colour


def is_name(label):
    return True


# names printed in parts (a text and a glyph label; the parks' names on three lines), in reading order
JOIN = [('Howie’s', 'Wanderer'), ('Log Jam', 'Terrain', 'Park'), ('Birch Run', 'Terrain', 'Park'),
        ('The Zone', 'Terrain Park'), ('Knight’s', 'Revenge', 'Gladed Park'), ('Burton', 'Treehouse', 'Riglet Park')]
TWO_LINE = set()
NO_STRETCH = set()
LABEL_LINE = set()
# Birch Run's own label (a leader to the park's line) names the park's line: its park box is the same run. A second
# Sherwood Forest label is drawn under the painting at the map's right edge (hidden)
DROP = [('Birch Run Terrain Park', None), ('Sherwood Forest', (4144, 1574))]
RENAME = {'Express': 'Thomke’s Express'}  # printed on its line beside Thomke's (the resort's list: Thomke's Express)
EXTRA = []
SYMBOL_FIX = []
DISPLAY = {}
AS_PRINTED = True  # names are printed in their own case: display them as printed
GLADES = set()
PARKS = {'Birch Run', 'Log Jam Terrain Park', 'The Zone Terrain Park', 'Knight’s Revenge Gladed Park',
         'Burton Treehouse Riglet Park'}  # the orange lines and the Riglet park's box
NO_LINE = {'Burton Treehouse Riglet Park': "A kids' learning park at the village base, its name in an orange box with "
                                           'no line: marker at its name'}
# the three mountains, each with its summit elevation as printed; trails grouped as the resort's trail report does
AREAS = [('morse', 'Morse Mountain', 2250), ('madonna', 'Madonna Mountain', 3640),
         ('sterling', 'Sterling Mountain', 3040)]
# names whose label positions don't tell: Midway and Curley's Cutback run from Morse to the upper mountains' base;
# Shuttle is printed on the Sterling side of the col but leaves Madonna (the resort's trail report lists them so)
AREA_OF = {'Midway': 'morse', 'Curley’s Cutback': 'morse', 'Shuttle': 'madonna'}
# Midway is printed on a green box at Morse and a blue one on its lower part: the resort's trail report rates it Easy
RATING = {'Midway': 'circle'}
# the parks print no rating: blue, the default (seed_roster.py), also for Knight's Revenge Gladed Park, which as a
# glade would default to black; the Burton Treehouse Riglet Park (no line) is a kids' learn-to-ride park: green
DEFAULT_SYMBOL = {'Burton Treehouse Riglet Park': 'circle', 'Knight’s Revenge Gladed Park': 'square'}
# the double diamond on the unnamed expert line at the Madonna summit (decisions.py UNNAMED)
LOOSE_SYMBOLS = 'the double diamond on the unnamed expert line at the Madonna summit'


def area(c):
    """The area (AREAS id) of a name printed at c (map px): Morse left of Madonna's slopes and along the village
    base, Sterling right of the col below Highlander Glades, Madonna between."""
    x, y = c
    if x < 1250 or (y > 1950 and x < 2100):
        return 'morse'
    return 'sterling' if x > 2620 else 'madonna'
