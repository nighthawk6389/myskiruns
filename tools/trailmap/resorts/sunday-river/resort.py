"""Sunday River's 2023-24 trail map, still the one on sundayriver.com for 2025-26 (its resort-maps page): one vector
PDF page with the main map and three insets. Trail lines are strokes in the difficulty colours (orange for freestyle
terrain); names are outlined glyphs on cream label boxes along their lines, coloured by difficulty, with black
names marked by a single or double diamond (green and blue names print no symbol). prepare.py extracts them; read by
tools/trailmap/pdf_resort.py."""

CLIP = (0, 0, 1920, 1080)  # PDF points: the whole page (main map, insets, key)
SCALE = 2.5  # map px per PDF point
SOURCE = ('Sunday River trail map PDF (sundayriver.com resort maps): 1 pt green, blue, black and orange strokes '
          '(0.49 pt in the North Peak inset, 1.53 pt Merrill Hill, 2.04 pt the base lodge inset), each cut to its own '
          'frame by tools/trailmap/resorts/sunday-river/prepare.py; percent of the map image')
SYMBOL_REACH = 12  # pt from a name's first or last character (or its centre) to its diamond
SYMBOL_CENTRE = True  # glade names print their diamonds above the middle of the name
END_REACH = 4  # pt from a name's end to the end of the line that runs into it
ALONG = 6  # pt: a piece this close to most of a name's characters runs along it (label boxes sit beside lines)
JOIN_GAP = 9  # pt between the lines of a name printed on two
ALONG_SHORT = True
ALONG_NEAREST = True  # names sit between parallel lines (the North Peak inset): each takes its nearest line
MATCH_ENDS = False  # names are printed on their lines (label boxes over the line), not in a gap


def is_name(label):
    return label.get('color') in ('green', 'blue', 'black', 'orange')


# names printed in parts (two lines), in reading order
JOIN = [('UPPER', 'HARD BALL'), ('LOWER', 'HARD BALL'), ('UPPER', 'CHUTZPAH'), ('LOWER', 'CHUTZPAH'),
        ('UPPER', 'NORTH WOODS'), ('LOWER', 'NORTH WOODS'), ('JIM’S', 'WHIM'), ('POMA', 'ROAD'),
        ('UPPER', 'CARAMBA'), ('UPPER', 'WIZARD’S GULCH'), ('LOWER', 'WIZARD’S GULCH'),
        ('UPPER', 'WIZARDS GULCH'), ('LOWER', 'WIZARDS GULCH')]
TWO_LINE = {' '.join(p) for p in JOIN}
NO_STRETCH = set()
# printed at the top end of Grand Rapids' line, by the lodge, over the line's last stretch: a stretch along the name
LABEL_LINE = {'PEAK EASY'}
# text in the name style that isn't a trail: peak names, inset titles, boot-up signs
DROP = [(t, None) for t in ('OZ', 'AURORA', 'PEAK', 'SPRUCE', 'BARKER', 'MOUNTAIN', 'LOCKE', 'WHITE', 'CAP', 'NORTH',
                            'JORDAN', 'BOWL', 'NORTH PEAK', 'NORTHPEAK', 'BOOTS ON', 'BOOTS OFF', 'BAG DROP')]
# the North Peak inset names two lines without the Upper / Lower the main map gives their two sections: those inset
# lines are left unnamed (decisions.py) rather than made into a third trail each (close/inset_risky.png)
DROP += [('RISKY BUSINESS', (3599, 478)), ('VORTEX', (3733, 640))]
RENAME = {'SLU CE': 'SLUICE', 'OVER DRAFT': 'OVERDRAFT', 'LOWERCARAMBA': 'LOWER CARAMBA',
          'UPPER WIZARDS GULCH': 'UPPER WIZARD’S GULCH', 'LOWER WIZARDS GULCH': 'LOWER WIZARD’S GULCH',
          '3 MILE TRAIL': 'THREE MILE TRAIL', '3MILETRAIL': 'THREE MILE TRAIL'}
EXTRA = []
SYMBOL_FIX = []
DISPLAY = {'UPPER 3D': 'Upper 3D', 'LOWER 3D': 'Lower 3D'}
# names printed over trees with no line (a diamond or two, no line): glades, markers at the name (noline/sheet_*)
LOOSE_SYMBOLS = "the North Peak inset's Vortex diamonds (its line is left unnamed there)"
GLADES = {'STARWOOD', 'STARSTRUCK', 'UPPER HARD BALL', 'LOWER HARD BALL', 'UPPER CHUTZPAH', 'LOWER CHUTZPAH',
          'HOLLYWOOD', 'LAST TANGO', 'UPPER NORTH WOODS', 'LOWER NORTH WOODS', 'CELESTIAL', 'YETIVILLE',
          'FLYING MONKEY', 'POPPY FIELDS', 'UPPER WIZARD’S GULCH', 'LOWER WIZARD’S GULCH', 'DOUBLE BLIND',
          'BLIND AMBITION'}
PARKS = {'UPPER T72', 'LOWER T72', 'LOWER 3D', 'STARLIGHT', 'WONDERLAND', 'FLOW STATE', 'WHO-VILLE'}
NO_LINE = {'POMA ROAD': 'Printed in the trees between Cascades and Monday Mourning, with its diamond and no line: marker at its name',
           'ENCHANTED FOREST': 'A kids\' adventure area by the North Peak base, named with no line: marker at its name',
           'ROCKING CHAIR': 'Printed beside Flow State\'s orange freestyle line, with no line of its own: marker at its name'}
# the map prints no elevations; 3,140 ft is the resort's published summit (Oz / Jordan Bowl)
AREAS = [('sunday-river', 'Sunday River', 3140)]


def area(c):
    """The area (AREAS id) of a name printed at c (map px)."""
    return 'sunday-river'
