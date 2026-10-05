"""Hunter Mountain's 2025-26 trail map: one vector PDF page (huntermtn.com). The painting itself is vector art;
every trail is a thin line in its difficulty colour that runs into its name, printed in a gap of the line with
its symbol at one end (FuturaPTCond-Medium 3.8 pt text). Symbols have rounded corners; a double diamond is one
outline. Read by tools/trailmap/pdf_resort.py; regen.sh downloads the PDF and extracts it."""

CLIP = (34, 13, 1000, 510)  # PDF points: the painting from the logo to the top of the code-of-conduct box
SCALE = 5  # map px per PDF point
SOURCE = ('Hunter Mountain 2025-26 trail map PDF (20251122_HU_winter-trail_map_001.pdf): '
          'tools/trailmap/extract_pdf_vectors.py --clip 34,13,1000,510 --scale 5, the 0.38 pt green, blue and black '
          'strokes; percent of the map image')
SYMBOL_REACH = 6  # pt from a name's first or last character to its symbol
END_REACH = 4  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 3  # pt: a piece this close to most of a name's characters runs along it


def is_name(label):
    return label['font'] == 'FuturaPTCond-Medium' and abs(label['size'] - 3.8) < 0.1


# names printed in two parts (two lines, or two text objects on one line): joined into one name
JOIN = [('UPPER EAST', 'SIDE DRIVE'), ('BELT PARKWAY', 'BYPASS'), ('MAD', 'BOX'), ('PARK AVENUE', 'WEST')]
# names on two lines, printed beside their line rather than in a gap of it: no stretch along them
TWO_LINE = {'BELT PARKWAY BYPASS', 'MAD BOX', 'PARK AVENUE WEST'}
NO_STRETCH = set()  # other names printed beside their line
# names whose label is all the line they have (printed in an open snow band with no line on either side): the
# stretch along the label is their overlay (close/upper_crossover_plain.png)
LABEL_LINE = {'UPPER CROSSOVER'}
DROP = []  # (printed text, (x, y) or None): text in the name style that isn't a trail
RENAME = {}  # printed text -> NAME, where the map misprints a name
EXTRA = []  # (NAME, x, y[, symbol]): names printed some other way (another font, a sign)
SYMBOL_FIX = []  # ((x, y), kind): a symbol the extraction misreads, as read on a crop
DISPLAY = {'KMC DRIVE': 'KMC Drive'}  # NAME -> display spelling, where title case gets it wrong
GLADES = set()  # glades whose name doesn't say so (the three glades here say so: tree icon, diamond, no line)
# trails with freestyle terrain: the orange pill printed on their line (the legend's FREESTYLE TERRAIN)
PARKS = {'PARK AVENUE', 'PARK AVENUE WEST', 'LOWER 42ND STREET'}
NO_LINE = {'LEARNING ZONE': 'A beginner area at the Hunter East base, named with no line: marker at its name'}
AREAS = [('hunter', 'Hunter Mountain', 4040)]  # id, name, elevation (ft, printed at the summit)


def area(c):
    """The area (AREAS id) of a name printed at c (map px)."""
    return 'hunter'
