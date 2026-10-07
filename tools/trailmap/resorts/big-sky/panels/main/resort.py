"""Big Sky Resort, the main map (bigsky_main.pdf: the whole resort; the South Face and the Bowl in more detail on
their insets). Trail lines are strokes in the difficulty colours (green, blue, black; the terrain parks orange; the
main green and blue routes drawn wide); names are dark text on a white halo, curved ones also drawn a letter at a
time, the symbol before or after the name, printed along the line, in a gap of it or beside it. Read by
tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location('big_sky', os.path.join(os.path.dirname(__file__), '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (13, 13, 2404, 1194)  # PDF points: the page inside its black frame
SCALE = 2.0  # map px per PDF point
SOURCE = ('Big Sky Resort 2025-26 trail map PDF (bigskyresort.com, trail maps), main map: 1.4 pt green, blue and '
          'black strokes (the main routes wider), tools/trailmap/resorts/big-sky/prepare.py; percent of the map image')
SYMBOL_REACH = 14  # pt from a name's first or last character to its symbol
END_REACH = 6  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 4.5  # pt: a name printed beside its line, about a character's height off it
ALONG_NEAREST = True
ALONG_FIRST = True  # names are printed along their own line, the symbol at one end: that line is the name's
NO_STRETCH_BESIDE = True

is_name = TOP.is_name


# names printed in parts (on two lines), in reading order
JOIN = [('Rock', 'Pocket'), ('Marlboro', 'Country'), ('BONE', 'CRUSHER'), ('ST. ALPHONSE', 'TREES'),
        ('BIG ROCK', 'TONGUE'), ('PATROL', 'TREES'), ('DEEPWATER', 'BOWL'), ('AMBUSH', 'MEADOWS'),
        ('HORSESHOE', 'BOWL'), ('COWPOKE', 'PARK')]
TWO_LINE = {' '.join(p) for p in JOIN}
NO_STRETCH = {"Don't Tell Mama"}  # DTM: three letters along its line, the line drawn already
LABEL_LINE = set()
# the beacon training area, the snowshoe trails; a curved name's leftover letters (its W is drawn with STUMPY'S);
# SPMC under SIX SHOOTER (where it goes: the Spanish Peaks Mountain Club); the numbers of The Gullies' six chutes
# and of Three Forks' three (each chute is the run's)
DROP = [(t, None) for t in ('Beacon Training', 'Area', 'MOOSE TRACKS SNOWSHOE TRAIL', 'SNOWSHOE TRAIL', 'OLF', 'SPMC',
                            '1 2 3 4 5 6')] + [('1', (3411, 776)), ('2', (3429, 801)), ('3', (3442, 824))]
# as the resort's trail report names them (NAMES spells the rest)
RENAME = {'STUMPY’S W': 'STUMPY’S', 'Rock Pocket': 'Rock Pocket Area', 'Marlboro Country': 'Marlboro Country Area',
          'ELK PARK MEADOWS': 'Elk Park Meadows Area', 'WOLF’S DEN': 'Wolf Den',
          'BEAR BACK': 'Bear Back Line',  # the run beside the Bear Back lift
          'PLAIN JANE': 'Plain Jane Park', 'WOLF PUP': 'Wolf Pup Park',
          'DTM': "Don't Tell Mama",
          # the report's Whitewater (Class 4, 5, 6): three chutes, each printed with its own name
          'CLASS 4': 'Whitewater (Class 4)', 'CLASS 5': 'Whitewater (Class 5)', 'CLASS 6': 'Whitewater (Class 6)',
          # printed on its black lower part; the blue upper part, with its double square, is EXTRA below
          'PB&J WAY': 'PB & J Way (Lower)'}
# names printed twice that are two runs on the trail report: the upper label and the lower
RENAME_AT = [((2310, 1017), 'CALAMITY JANE', 'Calamity Jane (Upper)'),
             ((2129, 1175), 'CALAMITY JANE', 'Calamity Jane (Lower)'),
             ((729, 977), 'TAKE A BOUGH', 'Take a Bough (Upper)'),  # the black run under Moose Drop, its diamond
             ((460, 1097), 'TAKE A BOUGH', 'Take a Bough (Lower)'),  # the green one past the clubhouse
             # from Fast Lane down to Lazy Jack, its double square at the top; the lower label, a square, is the
             # report's Powder River
             ((3008, 1232), 'POWDER RIVER', 'Powder River (Upper)')]
# PB & J Way's upper part: its blue line from Horseshoe down to the black lower part, the symbol on it
EXTRA = [('PB & J Way (Upper)', 4490, 1457, 'square')]
SYMBOL_FIX = []
# symbols out of reach of their names, or nearer another name: Don't Tell Mama's, Summit Direct's and Tears' triple
# diamonds at the tops of their lines (the last two on the North Summit Snowfield traverse that links the tops);
# Sticks & Stones' double square under its name (the circle beside it is Lazy Jack's); Sacajawea's circle past its
# name's end and the double square beside it, Pomp's; Elk Park Meadows' double square by its name;
SYMBOL_OF = [((3470, 823), "Don't Tell Mama"), ((3706, 688), 'Summit Direct'), ((3741, 677), 'Tears'),
             ((3031, 1194), 'Sticks & Stones'), ((1114, 967), 'Sacajawea'), ((1103, 985), 'Pomp'),
             ((1134, 1450), 'Elk Park Meadows Area'),
             # Rudy's square at the top of its line, above its name and beside K1 Return's (whose circle is at the
             # label's other end)
             ((755, 1056), 'Rudy'), ((831, 1102), 'K1 Return')]
# Hells Half Acre's line leaves Hellroaring's below the triple diamond at its top, which the two share
DEFAULT_SYMBOL = {'Hells Half Acre': 'double-diamond'}
DISPLAY = {f'Whitewater (Class {k})': f'Whitewater (Class {k})' for k in (4, 5, 6)}
GLADES = set()
PARKS = TOP.PARKS
NO_LINE = {}
NAMES = TOP.NAMES
AREA_OF = TOP.AREA_OF


def area(c):
    """A name the trail report doesn't list: its mountain by where it is printed (the Spanish Peaks at the top left,
    Andesite Mountain west of the Swift Current lift, Lone Mountain east of it)."""
    if c[0] < 900 and c[1] < 1400:
        return 'spanish-peaks'
    return 'andesite' if c[0] < 2050 else 'lone-mountain'
