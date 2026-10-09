"""Mt. Bachelor's 2025-26 trail map (James Niehues's painting; mtbachelor.com, its winter trail map page): one
InDesign page, the legend panel on the left, the map on the right. The painting is a 300 dpi raster; its vector layer
draws every trail line as a filled outline in the rating's colour, and every name as outlined capitals in the run's
colour. prepare.py extracts it; read by tools/trailmap/pdf_resort.py."""
import json
import os
import re

CLIP = (355, 0, 1904, 1080)  # PDF points: the map, right of the legend panel
SCALE = 3  # map px per PDF point
SOURCE = ('Mt. Bachelor 2025-26 trail map PDF (mtbachelor.com): its outlined blue, green and black trail lines read by '
          'their centre lines (tools/trailmap/pdf_outline_lines.py), tools/trailmap/resorts/mt-bachelor/prepare.py; '
          'percent of the map image')
SYMBOL_REACH = 12  # pt from a name's first or last character to its symbol
END_REACH = 8  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 4.5  # pt: a name printed beside its line, about a character's height off it


def is_name(label):
    """The trail names: in the runs' colours, or the near-black of the parks' and adventure zones' names; not the
    peaks', lodges' and elevations' labels (drawn first, up to 260, and last, from 3290 on, but the parks' after
    3580), nor the Whitebark Pine logo. The Moraine, a run the report lists (the open slope under the summit), is
    printed among the peaks' labels, with no symbol."""
    s = label['seq']
    return 260 < s < 3290 or 3580 <= s < 4100 or label['text'] == 'THE MORAINE'


# the resort's trail report (report.json: its DOR trail list, every winter run with its sector and rating). Its runs
# split into (upper), (middle) and (lower) are printed as one name: one trail each; but Sunrise Getback, whose three
# parts the map prints apart, each with its symbol: three trails.
REPORT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']


def _base(name):
    if name.startswith('Sunrise Getback'):
        return name
    return re.sub(r'\s*\((?:upper|middle|lower)\)$', '', name, flags=re.I)


# names as the report spells them (the map prints capitals)
NAMES = sorted({_base(n) for n, _a, _r in REPORT})
# the report's sectors, each with its highest elevation: the summit (9,065' as printed); the Frontside's Pine Marten
# Lodge (7,775' as printed, at the top of the Pine Marten Express); the Westside's Northwest Express (its base printed
# 5,700', plus its vertical, 2,365', from the resort's lift list: 8,065'); the Eastside's Sunrise Express (Sunrise
# Lodge printed 6,450', plus 808': 7,258'; the Cloudchaser goes higher, but no figure for it is published)
AREAS = [('summit', 'Summit', 9065), ('westside', 'Westside', 8065), ('frontside', 'Frontside', 7775),
         ('eastside', 'Eastside', 7258)]
_AREA_ID = {'Summit': 'summit', 'Westside': 'westside', 'Frontside': 'frontside', 'Eastside': 'eastside'}
# a run whose parts the report puts in two sectors (Wanoga Way, Ed's Garden) goes with its upper part's, where it
# starts
AREA_OF = {}
for _n, _a, _r in sorted(REPORT, key=lambda t: '(upper)' not in t[0]):
    if _a in _AREA_ID:
        AREA_OF.setdefault(_base(_n), _AREA_ID[_a])
# the Woodward Mountain Parks (the report's own sector) go with the side they are on, by the lifts that serve them
AREA_OF.update({'Start Park': 'eastside', 'Short Sands': 'eastside', 'Seaside': 'frontside',
                'Cannon Beach': 'frontside', 'The Point': 'frontside', 'Pacific City': 'frontside',
                'Progression Park': 'frontside', 'Halfpipe': 'frontside', 'Peace Park': 'frontside'})


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


# names printed in parts (two or three lines), in reading order
JOIN = [('NOR HWEST', 'CROSSOVER'), ('OLYMPIAN', 'SHUTTLE'), ('WEST', 'BOWLS'), ('THE', 'POINT'), ('CANNON', 'BEACH'),
        ('PACIFIC', 'CITY'), ('START', 'PARK'), ('SHORT', 'SANDS'), ('DILLY', 'DALLY', 'ALLEY'),
        ('ENCHANTED', 'FOREST'), ('PROGRESSION', 'PARK'), ('RAINBOW', 'ADVENTURE', 'NONE'), ('PEACE', 'PARK'),
        ('HALF', 'PIPE')]
JOIN_GAP = 12
TWO_LINE = {' '.join(p) for p in JOIN}
NO_STRETCH = set()
LABEL_LINE = set()
# names whose letters the PDF draws grouped by shape (every G of a cluster of labels, then every R, ...), so they
# come apart into fragments: the fragments are dropped (map px) and each name placed by hand where it is printed
# (EXTRA), read on crops (c_er.png, frags1.png, frags2.png, c_shwb.png), with the symbol printed by it (SYMBOL_OF)
DROP = [('SHO', (2594, 2247)), ('YTR', (2596, 2295)), ('FIS', (4064, 2087)), ('H H', (4094, 2112)),
        ('AWK WING', (4164, 2162)), ('MA', (1252, 1981)), ('RSHM LLDW', (1314, 1922)), ('W ST B', (2672, 2118)),
        ('DA Y', (2682, 2234)), ('UN', (2677, 2189)), ('GREEN F', (568, 2204)), ('SH', (646, 2187)),
        ('LA', (621, 2191)), ('G G', (601, 2218)), ('N N', (570, 2231)), ('LO', (630, 2212)), ('LY R', (633, 2294)),
        ('ES', (680, 2266)), ('*START', (771, 2257)), ('PARK', (772, 2283)), ('V LCAN', (868, 1897)),
        ('ADVENTURE', (874, 1918)), ('NO', (857, 1940)), ('NE', (886, 1940)), ('REA', (684, 2302)),
        ('YAD', (636, 2324))]
# Z is N turned a quarter (one shape); the logo's T and B and a lost S; the parks' names on two lines
RENAME = {'CONVERGENCE NONE': 'CONVERGENCE ZONE', 'ATKESON’S NOOM': 'ATKESON’S ZOOM',
          'RAINBOW ADVENTURE NONE': 'RAINBOW ADVENTURE ZONE', 'NOR HWEST CROSSOVER': 'NORTHWEST CROSSOVER',
          'DEVIL’S SACKBONE': 'DEVIL’S BACKBONE', 'COFFEE WE T': 'COFFEE WEST', 'DDWNUNDER': 'DOWNUNDER',
          'WEST BOWLS': 'WEST BOWLS & GLADES', 'BACKSIDE BOWLS': 'BACKSIDE BOWLS & GLADES', 'HALF PIPE': 'HALFPIPE',
          'BUSHWHACKER': 'BUSHWACKER'}
EXTRA = [('Shorty', 2595, 2265), ('Fish Hawk Wing', 4116, 2124), ('Marshmallow', 1284, 1950),
         ('West Boundary', 2676, 2181), ('Green Flash', 592, 2200), ('Morning Glory', 594, 2237),
         ('Early Riser', 648, 2282), ('Day Break', 665, 2309), ('Volcano Adventure Zone', 873, 1917),
         ('Start Park', 771, 2269)]
SYMBOL_OF = [((2593, 2215), 'Shorty'), ((4041, 2063), 'Fish Hawk Wing'), ((1226, 2002), 'Marshmallow'),
             ((2665, 2057), 'West Boundary'), ((517, 2228), 'Green Flash'), ((523, 2282), 'Morning Glory'),
             ((582, 2312), 'Early Riser'), ((606, 2335), 'Day Break')]
SYMBOL_FIX = []
# names printed with no symbol: the report's rating (The Moraine, The Cone; the adventure zones, green; the parks
# are parks)
DEFAULT_SYMBOL = {'The Moraine': 'diamond', 'The Cone': 'diamond', 'Volcano Adventure Zone': 'circle',
                  'Rainbow Adventure Zone': 'circle', 'Dilly Dally Alley': 'circle', 'Enchanted Forest': 'circle'}
DISPLAY = {}
GLADES = set()
PARKS = {'Start Park', 'Short Sands', 'Seaside', 'Cannon Beach', 'The Point', 'Pacific City', 'Progression Park',
         'Halfpipe', 'Peace Park'}
NO_LINE = {}
