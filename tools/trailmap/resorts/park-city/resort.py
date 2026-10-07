"""Park City Mountain's 2025-26 trail map (parkcitymountain.com, its trail-map page): one vector PDF page over a
low-resolution painting, the Park City side on the left and Canyons on the right, with the High Meadow Park inset
at the top right. Trail lines are strokes in the difficulty colours (orange: the terrain parks); names are outlined
glyphs in the run's colour, the symbol before the name. prepare.py extracts it; read by
tools/trailmap/pdf_resort.py."""
import re

CLIP = (12, 12, 1758, 922)  # PDF points: the map, above the lift table
SCALE = 2.5  # map px per PDF point
SOURCE = ('Park City Mountain 2025-26 trail map PDF (parkcitymountain.com): 1.14 pt green, blue, black and orange '
          'strokes (1.54 and 1.57 pt in the High Meadow Park inset), tools/trailmap/resorts/park-city/prepare.py; '
          'percent of the map image')
SYMBOL_REACH = 12  # pt from a name's first or last character to its symbol (a double diamond's middle)
END_REACH = 6.5  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 4.5  # pt: a name printed beside its line, about a character's height off it
ALONG_NEAREST = True
NO_STRETCH_BESIDE = True

# text in the names' style that isn't a run: the peaks (letters spaced out: JUPITER P EAK) and their elevations
NOT_NAMES = ('ELEVATI', 'P EAK')


def is_name(label):
    if label.get('color') not in ('green', 'blue', 'black', 'orange'):
        return False
    return not any(w in label['text'] for w in NOT_NAMES)


# names printed in parts (two or three lines), in reading order
JOIN = [('THE', 'CHUTES'), ('SCOTT’S', 'BOWL'), ('DEAD', 'TREE'), ('MAIN', 'BOWL'), ('WAR', 'ZONE'),
        ('WEST SCOTT’S', 'BOWL'), ('1 ST', 'BOWL'), ('WEST', 'FACE'), ('McCONKEY’S', 'BOWL'), ('PUMA', 'BOWL'),
        ('UPPER', 'EAST FACE'), ('LOWER', 'EAST FACE'), ('BLACK', 'FOREST'), ('BLUESLIP', 'BOWL'),
        ('MID-MTN', 'CUTOFF'), ('THE', 'ABYSS'), ('SNOW', 'MEADOW'), ('UPPER', 'CROWNING', 'GLORY'),
        ('SHADOW', 'LANDS'), ('MURDOCK', 'BOWL'), ('MYSTIC', 'PINES'), ('HIDDEN', 'SPLENDOR'),
        ('MOTHERLODE', 'MEADOWS'), ('UPPER', 'HARMONY'), ('POWER', 'ALLEY'), ('MIDDLE', 'CROWNING GLORY'),
        ('BUGLE', 'RIDGE', 'BYPASS'), ('BERG’S', 'BOWL'), ('FOOLS', 'PARADISE'), ('BADGER’S', 'BYPASS'),
        ('PARADISE', 'BOWL'), ('CONDOR', 'WOODS'), ('PARADISE', 'CHUTES'), ('BONANZA', 'ACCESS'),
        ('ESCAPADE', 'WOODS'), ('SOUTH', 'FORK'), ('LOWER', 'SILVER SKIS'), ('RENDEZVOUS', 'BOWL'),
        ('PLATINUM', 'WOODS'), ('GOTCHA', 'CUT-OFF'), ('ROAD TO', 'THAYNES', 'CANYON'), ('ALLOY', 'ALLEY'),
        ('COBALT', 'WOODS'), ('UPPER', 'FIRST TIME'), ('SILVERADO', 'BOWL')]
# (and three read as one word: 10TH MTN in its oval, TURTLE TRAIL and LAZY DAY)
TWO_LINE = {' '.join(p) for p in JOIN} | {'1OTHMTN', 'TURTLETRAIL', 'LAZYDAY'}
NO_STRETCH = set()
LABEL_LINE = set()
DROP = [(t, None) for t in ('JUPITER', 'N IN ETY-N I N E 9 O')]
# the High Meadow Park inset prints WAPITI and FLYING SALMON at its top edge with no line under them (their lines
# are on the main map): no stretch along them
DROP += [('WAPITI', (3755, 113)), ('FLYING SALMON', (3717, 139))]
# misreadings (a 1 read as I, a letter drawn twice, Blaise's apostrophe read as a hyphen, Lazy Day's two lines read
# as one run) and the map's abbreviations, as the resort's trail report spells
# them; HARMONY is printed on the lower part of Upper Harmony's run (the report's Lower Harmony); PINECONE, by the
# Jupiter bowls, is the report's Pinecone Bowl (PINECONE RIDGE is printed apart)
RENAME = {'1OTHMTN': '10TH MOUNTAIN', '1 ST BOWL': '1ST BOWL', 'WHIIPPETS CHUTES': 'WHIPPETS CHUTES',
          'TURTLETRAIL': 'TURTLE TRAIL', 'MID-MTN': 'MID-MOUNTAIN', 'MID-MTN CUTOFF': 'MID-MOUNTAIN CUTOFF',
          'MID-MTN MEADOWS': 'MID-MOUNTAIN MEADOWS', 'MEN’S SL': 'MEN’S SLALOM', 'LADIES’ SL': 'LADIES’ SLALOM',
          'HARMONY': 'LOWER HARMONY', 'PINECONE': 'PINECONE BOWL', 'BLAISE-S WAY': 'BLAISE’S WAY',
          'LAZYDAY': 'LAZY DAY'}
EXTRA = []
SYMBOL_FIX = []
# ((x, y), NAME): a symbol printed beside its name but out of SYMBOL_REACH: the diamonds under the middle of the
# one-line names in grey ovals (tree areas and bowls)
SYMBOL_OF = [((3348, 1521), 'BLACK HOLE'), ((3405, 705), 'THE PINES'), ((3625, 1007), 'TREE TIME'),
             ((3287, 677), 'THE ASPENS')]
DISPLAY = {}
GLADES = set()
# the terrain parks: orange lines named in orange (the halfpipe is a name with no line)
PARKS = {'3 KINGS', 'LITTLE KINGS', 'PICK ’N SHOVEL', 'PICK AXE', 'HALFPIPE', 'TRANSITIONS'}
NO_LINE = {}
# the two sides, each with its summit elevation as printed (Jupiter Peak 10,026 ft; Ninety-Nine 90 9,990 ft)
AREAS = [('park-city', 'Park City Mountain Village', 10026), ('canyons', 'Canyons Village', 9990)]


def area(c):
    """The area (AREAS id) of a name printed at c (map px): the resort's trail report groups its lift pods into the
    Park City side (Payday to Jupiter) and the Canyons side (Iron Mountain to Condor); on the map they meet by Thaynes
    Canyon, between the Park City side's rightmost name (Pinecone Ridge) and the Canyons side's leftmost (The Highway)."""
    return 'park-city' if c[0] < 1543 else 'canyons'
