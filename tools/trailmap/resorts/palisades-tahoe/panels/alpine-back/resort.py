"""Palisades Tahoe, Alpine's back side, Sherwood and the back of Scott Peak (alpine-back-side-trail.pdf). Trail
lines are strokes in the difficulty colours; names are black glyphs on a white halo, the symbol before the name,
printed along the line, in a gap of it or beside it. Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts
it."""
import re

CLIP = (60, 300, 1690, 850)  # PDF points: the map, without the sky above it
SCALE = 2.5  # map px per PDF point
SOURCE = ('Palisades Tahoe 2025-26 trail map PDF (palisadestahoe.com, trail maps), Alpine back side: 1 pt blue and '
          'black strokes, tools/trailmap/resorts/palisades-tahoe/prepare.py; percent of the map image')
SYMBOL_REACH = 14  # pt from a name's first or last character (or its middle) to its symbol
SYMBOL_CENTRE = True  # symbols printed before the name, or above or below its middle
END_REACH = 7  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 4.5  # pt: a name printed beside its line, about a character's height off it
ALONG_NEAREST = True
NO_STRETCH_BESIDE = True

AS_PRINTED = True  # names are printed in their own case: display them as printed

# text in the names' style that isn't a run
NOT_NAMES = ()


def is_name(label):
    t = ' '.join(label['text'].split())
    if label.get('color') != 'black' or label['text'].count('*'):
        return False
    return not any(re.search(rf'\b{w}\b', t) for w in NOT_NAMES)


# names printed in parts (on two or three lines, or one line with a wide word gap), in reading order
JOIN = [('Bobby’s', 'Run'), ('Reily’s', 'Run'), ('Sherwood', 'Run'), ('Standard', 'Run'), ('East', 'Gully'),
        ('West', 'Gully'), ('Grouse', 'Rock'), ('Lower', 'Saddle'), ('Upper', 'Saddle'), ('Maid', 'Marian'),
        ('Nottingham’s', 'Notch'), ('Robin', 'Hood'), ('Scott', 'Meadow'), ('Sherwood', 'Face'),
        ('Shooting', 'Star'), ('Summer', 'Road'), ('Twilight', 'Zone'), ('Winter', 'Road'), ('High TraVerse', 'Entry'),
        ('South Face', 'Access')]
JOIN_GAP = 12  # pt between the parts' glyph centres
TWO_LINE = {' '.join(p) for p in JOIN}
NO_STRETCH = set()
LABEL_LINE = set()
DROP = [('F Tree', None)]  # a landmark
RENAME = {'High TraVerse': 'High Traverse', 'outer Limits': 'Outer Limits', 'SlPl Bowl': 'S.P. Bowl',
          'LakeView to Weasel': 'Lakeview to Weasel',
          'High TraVerse Entry': 'High Traverse',  # a pointer to where the High Traverse starts
          # the front side's Return Road (it runs on over the ridge to Weasel Run, and the front map names it so)
          'Return Road to Weasel': 'Return Road',
          # names the Palisades side also has, for other runs (the trail report lists both): Alpine's own trails
          'Sun Bowl': 'Sun Bowl (Alpine)', 'Summer Road': 'Summer Road (Alpine)'}
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
# ((x, y), NAME): a symbol printed beside its name but out of SYMBOL_REACH
SYMBOL_OF = [((913, 303), 'S.P. Bowl')]
# names printed with no symbol (and no line to colour them), as the resort's trail report rates them
DEFAULT_SYMBOL = {'High Traverse': 'diamond', 'South Face Access': 'diamond'}
DISPLAY = {'Sun Bowl (Alpine)': 'Sun Bowl', 'Summer Road (Alpine)': 'Summer Road'}
GLADES = set()
PARKS = set()
NO_LINE = {}


def area(c):
    return 'alpine'
