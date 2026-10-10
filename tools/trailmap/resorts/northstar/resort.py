"""Northstar's 2025-26 trail map (northstarcalifornia.com: 20251022_NS_winter-trail_map_001.pdf, page 1; skimap.org's
map 36907 is the same file): Alex Tait's painting under a vector layer; trail lines are filled outlines in the three
trail colours, names white outlined capitals printed on the line, each letter haloed in the line's colour, the
symbol on the line at the name's start. Read by tools/trailmap/pdf_resort.py; prepare.py extracts it."""
import json
import os

CLIP = (0, 0, 1328, 873)  # PDF points: the page (the legend, the inset and the boxes left out: prepare.py)
SCALE = 3  # map px per PDF point
SOURCE = ('Northstar 2025-26 trail map PDF (northstarcalifornia.com): the trail lines, filled outlines, by their '
          'centre lines, tools/trailmap/resorts/northstar/prepare.py; percent of the map image')
SYMBOL_REACH = 10  # pt from a name's first or last letter to its symbol (on the line before the name)
END_REACH = 6  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 3  # pt: a name is printed on its own line (the line runs on either side of it)
ALONG_NEAREST = True
ALONG_FIRST = True
NO_STRETCH_BESIDE = True

# the trail report's areas (report.json), each with the highest elevation printed on it: Mt. Pluto's summit (the
# Backside's runs start there too), the top of Lookout Mountain (8,120 ft, also the Northwest Territory's top, by
# the Lookout Link), the village (6,330 ft)
AREAS = [('mt-pluto', 'Mt. Pluto', 8610), ('backside', 'The Backside', 8610),
         ('northwest-territory', 'Northwest Territory', 8120), ('lookout-mountain', 'Lookout Mountain', 8120),
         ('village', 'Village at Northstar', 6330)]
_AREA_ID = {'Mt. Pluto': 'mt-pluto', 'The Backside': 'backside', 'Northwest Territory': 'northwest-territory',
            'Lookout Mountain': 'lookout-mountain', 'Village at Northstar': 'village', 'Terrain Parks': 'mt-pluto'}
# the resort's trail report (report.json: the terrain feed, February 2026)
REPORT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
NAMES = sorted({n for n, _a, _r in REPORT})
AS_PRINTED = True  # names are shown as the report spells them
AREA_OF = {}
for _n, _a, _r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


def is_name(label):
    return label.get('color') in ('blue', 'black', 'green', 'park')


# the rating is the symbol by the name, else its halo's colour (the parks' orange pills: blue)
COLOR_SYMBOL = {'green': 'circle', 'blue': 'square', 'black': 'diamond', 'park': 'square'}
# names printed in parts (two lines, or two runs of glyphs along one line), in reading order
JOIN = [('POWDER', 'BOWL'), ('UPPER', 'LION’S WAY'), ('DOWN', 'UNDER'), ('FOLLOW', 'ME'), ('CHRISTMAS', 'TREE'), ('NORTHERN', 'LIGHTS'),
        ('LOWER', 'LION’S WAY'), ('EASY', 'STREET'), ('OVERLAND', 'TRAIL'), ('LOOKOUT', 'ROAD'), ('EX', 'HANDLE')]
TWO_LINE = {' '.join(p) for p in JOIN}
JOIN_GAP = 40  # pt: the parts of a name are printed along its line, a run of glyphs apart
NO_STRETCH = set()
LABEL_LINE = {'Cowboy Pass', 'Bearly'}  # their labels are all of their lines (Cowboy Pass's from Lookout Road's foot
# to Goldmine; Bearly's from its circle by the Big Springs Gondola)
# the lifts' names (white on their red bands)
DROP = [(t, None) for t in ('VISTA EXPRESS', 'RENDEZVOUS', 'ARROW EXPRESS', 'TAHOE ZEPHYR EXPRESS',
                            'BIG SPRINGS EXPRESS GONDOLA', 'HIGHLANDS GONDOLA', 'THE BIG EASY', 'COMSTOCK EXPRESS',
                            'BACKSIDE EXPRESS', 'MARTIS CAMP EXPRESS', 'TIMBERLINE', 'VILLAGE EXPRESS',
                            'PROMISED LAND EXPRESS', 'LOOKOUT LINK')]
# as the report names them (NAMES spells the rest by their letters): words the glyph runs ran together or split
RENAME = {'UPPERJIBBOOM': 'Upper Jibboom', 'UPPER MA N ST.': 'Upper Main Street', 'LOWER PIONEE': 'Lower Pioneer',
          'SPRINGBOARD': 'Spring Board', 'TIMBER LINE': 'Timberline',
          'EX HANDLE': 'Axe Handle'}  # AXE's A and X are one glyph run with the E (read EX)
RENAME_AT = []
# the Kids Adventure Zone's four, printed as numbered smiley signs on the map and named only in its box (top left,
# left out), as the trail report spells them; and the Carpet Bowl learning area, printed only in the Mid-Mountain inset
EXTRA = [('Eagle Chute', 1344, 419, 'square'), ('Bobcat Bowl', 1536, 644, 'square'), ('Bear Crawl', 1060, 880, 'square'),
         ('Lynx Luge', 299, 1714, 'square'), ('Carpet Bowl', 2956, 2440, 'circle')]
SYMBOL_FIX = []
SYMBOL_OF = [((1999, 326), 'Monument Glade')]  # its diamond, a little beyond reach of its first letter
DISPLAY = {}
GLADES = set()
PARKS = {n for n, a, _r in REPORT if a == 'Terrain Parks'}
NO_LINE = {}
LOOSE_SYMBOLS = 'the square on the unnamed line below The Chute\'s foot'
