"""Palisades Tahoe, the Palisades side (palisadesmaintrailmap.pdf). Trail lines are strokes in the difficulty
colours; names are black glyphs on a white halo, the symbol before the name, printed along the line, in a gap of it
or beside it. Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import re

CLIP = (60, 360, 2080, 1280)  # PDF points: the map, without the sky above it
SCALE = 2.5  # map px per PDF point
SOURCE = ('Palisades Tahoe 2025-26 trail map PDF (palisadestahoe.com, trail maps), Palisades side: 1.26 pt green, '
          'blue and black strokes, tools/trailmap/resorts/palisades-tahoe/prepare.py; percent of the map image')
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
JOIN = [('Akja Cache', 'Pockets'), ('Bailey’s', 'Cirque'), ('Bill’s', 'Boardwalk'), ('Bottleneck', 'Gully'),
        ('Chicken', 'Bowl'), ('Downhill', 'Cliffs'), ('East Face', 'Cliffs'), ('Easy', 'Street'),
        ('Enchanted', 'Forest'), ('Granite', 'Chief Peak'), ('Hidden', 'Bowl'), ('Jagged', 'Edge'), ('Light', 'Towers'),
        ('Lost Lake', 'Loop'), ('Mainline', 'Pocket'), ('Monkey', 'Flower'), ('Monument', 'Ridge'), ('Mountain', 'Run'),
        ('North', 'Bowl'), ('Oregon', 'Trail'), ('Paris', 'Glades'), ('Powder', 'Horn'), ('Red Dog', 'Ridge'),
        ('Schimmelpfennig', 'Bowl'), ('Siberia', 'Bowl'), ('Siberia', 'Ridge'), ('Spring', 'Bowl'), ('Start', 'Me Up'),
        ('Strawberry', 'Fields'), ('Tom’s', 'Tumble'), ('Tower 12', 'Cliffs'), ('Tram', 'Bowl'), ('Upper', 'Dog Leg'),
        ('Valley', 'View'), ('Women’s', 'Downhill'), ('Yellow', 'Trail'), ('Nose', 'Chutes'),
        ('Summer Road', 'Pockets'), ('Saddle', 'Face'), ('Main', 'Backside')]
JOIN_GAP = 26  # pt between the parts' glyph centres (MOUNTAIN RUN is printed across a lift)
# (MOUNTAIN RUN is one line, printed across the Headwall Express: a stretch along it)
TWO_LINE = {' '.join(p) for p in JOIN} - {'Mountain Run'}
# names not printed along their line: no stretch along them. Main, Extra, Chimney and National print theirs
# across the sky above the Palisades, a line hanging from the symbol down to the chute; Attic's runs down through
# its one-line name; Broken Arrow is a name and diamond with no line (a 2 pt stub at the diamond's corner)
NO_STRETCH = {'Main', 'Extra', 'Chimney', 'National', 'Attic', 'Broken Arrow'}
LABEL_LINE = set()
# the terrain parks' sizes (XS, S/M, M/L) and the SnoVentures shuttle and tubing hill's signs
DROP = [(t, None) for t in ('XS', 'S/M', 'M/L', 'SHUTTLE', 'Tubing', 'SnoVentures')]
# misreadings (capital I read as l: CII; dots read as l: G.S.; a word gap read as none), as the trail report spells
# them (GS, To Mountain Run)
RENAME = {'Cll Ridge': 'CII Ridge', 'GlSl Bowl': 'GS Bowl', 'G.S. Cliffs': 'GS Cliffs',
          'Lower ChampsElysees': 'Lower Champs Elysees', 'to Mountain Run': 'To Mountain Run'}
RENAME_AT = []
# the High Camp gates: a number in a box with its symbol, on the traverse above Tram Bowl and Bailey's (the trail
# report's Gate 1 to Gate 8): (name, x, y, symbol) in map px
EXTRA = [('Gate 1', 4211, 718, 'double-diamond'), ('Gate 2', 4062, 653, 'double-diamond'),
         ('Gate 3', 3985, 639, 'double-diamond'), ('Gate 4', 3928, 660, 'double-diamond'),
         ('Gate 5', 3855, 684, 'double-diamond'), ('Gate 6', 3692, 731, 'double-diamond'),
         ('Gate 7', 3468, 797, 'diamond'), ('Gate 8', 3218, 771, 'diamond')]
SYMBOL_FIX = []
# ((x, y), NAME): a symbol printed beside its name but out of SYMBOL_REACH: on the line below its name
SYMBOL_OF = [((2779, 855), 'Burkhart’s'), ((1002, 1583), 'Red Dog Glades')]
DISPLAY = {}
GLADES = set()
PARKS = set()
NO_LINE = {}


def area(c):
    return 'palisades'
