"""Wildcat Mountain's 2025-26 trail map (skiwildcat.com, 20251226_WC_winter-trail_map_001). That PDF has its
names outlined and most trail lines flattened into a 1 px/pt painting, so the lines, names and symbols come from
an earlier export of the same artwork with live strokes and text (skimap.org map 33684): every one of its trail
names lands on the same outlined name, in the same colour, on the 2025-26 page, which is the same page shifted by
23.77 pt (a bleed margin; registered on the renders, scale 1.0000). Its dining box and partner logos differ, not
its trails. The map image is the 2025-26 page from Vail Resorts' image CDN (3575x4990, 3.38 px/pt; registered to
the PDF within 0.2 px). Read by tools/trailmap/pdf_resort.py; regen.sh downloads and extracts."""

# PDF points of the earlier export (= the 2025-26 page + 23.77): the painting down to the legend bar
CLIP = (23.77, 23.77, 1081.45, 1182.0)
SCALE = 3.380039  # map px per PDF point: the CDN image's 3575 px over the 2025-26 page's 1057.68 pt
SOURCE = ('Wildcat Mountain 2025-26 trail map (20251226_WC_winter-trail_map_001): strokes of the same artwork '
          'exported with live lines (skimap.org 33684), tools/trailmap/extract_pdf_vectors.py --clip '
          '23.77,23.77,1081.45,1182 --scale 3.380039, the 3.27 pt green, blue and black lines; percent of the map '
          'image')
SYMBOL_REACH = 22  # pt from a name's first or last character to its symbol
MATCH_ENDS = False  # names are printed on their lines, which run on past them (no gap)
CUT_AT_SYMBOLS = False  # symbols and names sit along the run (not at its start): lines are cut by hand (CUTS)
SYMBOL_OFF_LINE = 6  # pt: a symbol may sit this far beside its line (past its own size)
END_REACH = 6  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 4  # pt: a piece this close to most of a name's characters runs along it
JOIN_GAP = 18  # pt between the lines of a name printed on several


def is_name(label):
    # HelveticaNeue-CondensedBold 13.1 pt in a trail colour, or white (a halo copy); red is the lifts'
    return (label['font'].startswith('HelveticaNeue-Condensed') and abs(label['size'] - 13.1) < 0.2
            and tuple(label['color']) != (0.81, 0.12, 0.26))


# names printed in parts (two or three lines), in reading order
JOIN = [('LYNX', 'CONNECTION'), ('HAINESVILLE', 'PASS'), ("ANNIE’S", 'ALLEY'), ('LOWER', 'CAT', 'TRACK'),
        ("LEO’S", 'LEAP'), ('LOWER', 'CATENARY'), ('WILDCAT', 'PITCH'), ('MIDDLE', 'CATAPULT'), ('LYNX', 'LAIR'),
        ('CAT &', 'MOUSE'), ('OCELOT', 'WAY'), ('SNOWCAT', 'SLOPE'), ('SNOWCAT', 'TRAIL')]
TWO_LINE = {' '.join(p) for p in JOIN}  # printed beside or across their line: no stretch along them
NO_STRETCH = set()
LABEL_LINE = set()
# text in the name style that isn't a trail
DROP = [('WILDCAT MOUNTAIN', None), ('SUMMIT ELEVATION', None), ('4,062’', None), ('BASE ELEVATION', None),
        ('1,950’', None), ('PINKHAM', None), ('NOTCH', None), ('MAIN', None), ('BASE LODGE', None)]
RENAME = {}
EXTRA = []
SYMBOL_FIX = []
DISPLAY = {}
GLADES = set()
LOOSE_SYMBOLS = 'tree-skiing areas (a diamond, no name)'  # what the unnamed symbols off every line are
PARKS = set()
NO_LINE = {'CAT & MOUSE': 'A learning area at the base (circle and name, an arrow to the Snowbelt lift), no line: marker at its name'}
AREAS = [('wildcat', 'Wildcat Mountain', 4062)]  # id, name, elevation (ft, printed at the summit)


def area(c):
    """The area (AREAS id) of a name printed at c (map px)."""
    return 'wildcat'
