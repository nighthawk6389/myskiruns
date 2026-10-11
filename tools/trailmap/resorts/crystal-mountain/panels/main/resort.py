"""Crystal Mountain, the main panel: the 2025-26 trail map PDF's one page (crystalmountainresort.com's trail-maps page,
behind a bot check: tools/trailmap/fetch_pdf.cjs). VistaMap's painting is vector art; every run is a 1.5 pt line in
its difficulty's colour, its name printed in a gap of it or beside it (FuturaPTCond-Medium 12 pt) with its symbol at
one end; the expert terrain's bowls, faces and chutes print a name and a symbol with no line. Symbols have rounded
corners; a double diamond is one fill. The Northway lift's terrain is the other panel. Read by
tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('crystal_mountain', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (36, 36, 2652, 1605)  # PDF points: the painting, above the partners' band
SCALE = 1.5  # map px per PDF point
# the map key (bottom left) and the partners' logos (bottom right), pt: no runs
LEGEND = [(36, 1300, 680, 1745), (2380, 1540, 2652, 1605)]
# the interactive map's SVG units (resorts-interactive.com map 1809) on the map image (px), for tools/trailmap/vicomap.py
# check: its painting registered with tools/trailmap/register_pages.py --ref (2995 inliers, median 0.42 px); its lines
# are a looser drawing than the print's (vicomap.py fit pairs only 501 of 5910 points), so they only settle choices
VICOMAP_AFFINE = (0.7351377, 0.0000207, -14.6882, -0.0000165, 0.7355344, -32.3592)
SOURCE = ('Crystal Mountain 2025-26 trail map PDF (main panel): tools/trailmap/resorts/crystal-mountain/prepare.py, the 1.5 pt '
          'green, blue and black strokes; percent of the map image')
SYMBOL_REACH = 14  # pt from a name's first or last character to its symbol
END_REACH = 10  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 6  # pt: a piece this close to most of a name's characters runs along it
ALONG_NEAREST = True
SYMBOL_CENTRE = True  # the expert terrain's symbols under (or over) the middle of their names

NAMES, AREA_OF, AS_PRINTED, PARKS = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED, TOP.PARKS
is_name = TOP.is_name


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in TOP.NOT_IN_REPORT')


# names printed in two parts (on two lines), in reading order; a part is its text, or (text, (x, y)): the label near
# that point (map px), where the same word is printed elsewhere (each is also printed whole under its parts: the parts
# are what pdf_resort.py keeps)
JOIN = [(('POWDER', (1324, 954)), ('BOWL', (1324, 972))), (('LITTLE', (1391, 1025)), 'PORTILLO'),
        (('LOWER', (2172, 1177)), 'CHANCE'), (('LITTLE', (1567, 1211)), 'SHOT'),
        (('LITTLE', (1082, 1418)), ('MAGOO', (1079, 1436))), ('WALLY’S', 'WAY'), ('BERRY', 'PATCH'),
        (('LOWER', (1113, 1526)), ('MAGOO', (1112, 1544))), ('AFTER', 'BURN'), ('EASY', 'STREET'),
        (('SNORTING ELK', (2216, 1008)), ('BOWL', (2194, 1025))), (('GREEN VALLEY', (1880, 957)), ('BOWL', (1878, 973))),
        (('ROLLING KNOLLS', (1250, 1470)), 'CHUTES')]
JOIN_GAP = 16  # pt
TWO_LINE = {'POWDER BOWL', 'LITTLE PORTILLO', 'LOWER CHANCE', 'LITTLE SHOT', 'LITTLE MAGOO', 'WALLY’S WAY',
            'BERRY PATCH', 'LOWER MAGOO', 'AFTER BURN', 'EASY STREET', 'SNORTING ELK BOWL', 'GREEN VALLEY BOWL',
            'ROLLING KNOLLS CHUTES'}
SPLIT = {}
NO_STRETCH = set()
LABEL_LINE = set()
# text in the names' style that isn't a run: the boundary, the private land, an arrow's "to", and a hidden copy of
# NIAGRAS with a typo of its own
DROP = [('DESIGNATED SKI AREA BOUNDARY', None), ('SOUTHBACK BOUNDARY', None), ('PRIVATE', None), ('PROPERTY', None),
        ('to', None), ('NIAGAAS', None), ('’', None)]
RENAME = dict(TOP.RENAME)
# Berry Patch's two branches below its name, labelled RIGHT and LEFT
RENAME_AT = [((2191, 1573), 'RIGHT', 'Berry Patch'), ((2238, 1566), 'LEFT', 'Berry Patch')]
# the report's runs printed as a peak's or a basin's name (navy, another style), each a marker at its label with the
# report's rating
EXTRA = [('A-Basin', 706, 995, 'double-diamond'), ('Campbell Basin', 1026, 980, 'double-diamond'),
         ('Silver Basin', 242, 1238, 'double-diamond'), ('Silver King', 587, 874, 'double-diamond'),
         ('The Throne', 849, 852, 'double-diamond'), ('Three Way Peak', 141, 1062, 'double-diamond')]
SYMBOL_FIX = []
# symbols printed under or over their name's end, out of the matching's reach: (x, y) in map px, the name
SYMBOL_OF = [((704, 1013), 'A-Basin'), ((1026, 1008), 'Campbell Basin'), ((1645, 1038), 'The Doors'), ((1717, 1080), 'Sunnyside'), ((1763, 1205), 'Memorial Forest'),
             ((1175, 932), "Double 00's Right"), ((1260, 964), "Double 00's Left"), ((589, 1070), 'S.E. Trees')]
RATING = {}
# names printed with no symbol, not in the report: the default of their kind (the playbook's conventions): a glade and
# chutes black, the expert terrain's ridge and Southback's run double black
DEFAULT_SYMBOL = {'Pixie Trees': 'diamond', 'Rolling Knolls Chutes': 'diamond', 'Gun Tower Ridge': 'double-diamond',
                  'The Airstrip': 'double-diamond'}
DISPLAY = {}
GLADES = set()
NO_LINE = {}
