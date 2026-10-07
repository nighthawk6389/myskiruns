"""Palisades Tahoe, Alpine's front side (alpine-front-side-trail.pdf). Trail lines are strokes in the difficulty
colours; names are black glyphs on a white halo, the symbol before the name, printed along the line, in a gap of it
or beside it. Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import re

CLIP = (150, 220, 1620, 1141)  # PDF points: the map, without the sky above it
SCALE = 2.5  # map px per PDF point
SOURCE = ('Palisades Tahoe 2025-26 trail map PDF (palisadestahoe.com, trail maps), Alpine front side: 1.11 pt green '
          'and blue and 1 pt black strokes, tools/trailmap/resorts/palisades-tahoe/prepare.py; percent of the map '
          'image')
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
JOIN = [('Top', 'Alpine', 'Bowl'), ('Alpine', 'Bowl'), ('Art’s', 'Knob'), ('Banana', 'Chute'),
        ('Lower', 'Beaver', 'Entrance'), ('South', 'Beaver'), ('Beaver', 'Bowl'), ('Bernie’s', 'Bowl'),
        ('Chute That', 'Seldom Slides'),
        ('Counterweight', 'Gully'), ('Estelle', 'Bowl'), ('Expert', 'Shortcut'), ('Gentian', 'Gully'),
        ('Gunner’s', 'Knob'), ('Hidden', 'Knoll’s'), ('High', 'Yellow', 'Face'), ('High', 'Yellow', 'Gully'),
        ('Lower 40', 'Gully'), ('Lower', 'Saddle'), ('Meadow', 'Beginner', 'Area'), ('Nick’s', 'Run'),
        ('North', 'Peril'), ('Pete ’s', 'Peril'), ('Poma', 'Rocks'), ('Pond', 'Slope'), ('Reily’s', 'Run'),
        ('Return', 'Road'), ('Sandy’s', 'Corner'), ('Sherwood', 'Cliffs'), ('Subway', 'Beginner', 'Area'),
        ('Sympathy', 'Face'), ('The', 'Buttress'), ('Three', 'Sisters'), ('Upper', 'Saddle'), ('Werner’s', 'Schuss'),
        ('ldiot’s', 'Delight'), ('Wolverine', 'Saddle'), ('Wolverine', 'Bowl'), ('Estelle', 'Lake'),
        ('Face', 'Cliffs'), ('High Traverse to', 'Sherwood'), ('Access to', 'Sherwood'), ('Chalet', 'Restaurant')]
JOIN_GAP = 12  # pt between the parts' glyph centres
TWO_LINE = {' '.join(p) for p in JOIN}
NO_STRETCH = set()
LABEL_LINE = set()
# pointers (High Traverse to Sherwood; Access to Sherwood via Ray's Rut), a lake, the lodge
DROP = [(t, None) for t in ('High Traverse to Sherwood', 'Access to Sherwood', 'viaRay’s Rut', 'Estelle Lake',
                            'Chalet Restaurant')]
# (TO LAKEVIEW CHAIR, along an arrowed route with its own symbol, is the trail report's To Lakeview; the map's HIDDEN
# KNOLL'S is the report's Hidden Knolls)
RENAME = {'to Lakeview Chair': 'To Lakeview', 'Hidden Knoll’s': 'Hidden Knolls', 'Pete ’s Peril': 'Pete’s Peril',
          'ldiot’s Delight': 'Idiot’s Delight', 'our Father': 'Our Father',
          'outer Limits': 'Outer Limits', 'Upper Weasel one': 'Upper Weasel One', 'Keyholes Slopes': 'Keyhole Slopes',
          # as the trail report spells them
          'D-5': 'D5', 'D-6': 'D6', 'D-7': 'D7', 'D-8': 'D8', 'Ladies Slalom': 'Ladies’ Slalom',
          'Face Cliffs': 'The Face Cliffs',  # printed beside The Face
          # names the Palisades side also has, for other runs (the trail report lists both): Alpine's own trails
          'Rock Garden': 'Rock Garden (Alpine)', 'Yellow Trail': 'Yellow Trail (Alpine)'}
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
# ((x, y), NAME): a symbol printed beside its name but out of SYMBOL_REACH
SYMBOL_OF = [((417, 396), 'Outer Limits'), ((248, 483), 'Leisure Lane'), ((2050, 968), 'Banana Chute')]
# names printed with no symbol (and no line to colour them), as the resort's trail report rates them
DEFAULT_SYMBOL = {'Gunner’s Knob': 'diamond', 'Sandy’s Corner': 'square'}
DISPLAY = {'Rock Garden (Alpine)': 'Rock Garden', 'Yellow Trail (Alpine)': 'Yellow Trail'}
GLADES = set()
PARKS = set()
NO_LINE = {}


def area(c):
    return 'alpine'
