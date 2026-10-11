"""Stevens Pass's winter trail map (stevenspass.com's trail-maps page: 20241115_SV_winter-trail_map_001.pdf, the
2024-25 edition its page still links; the map is the PDF's second page): two paintings under one vector layer, the
Front Side and Mill Valley (the back side, drawn at a larger scale). Runs' lines are strokes in the three trail
colours, every name outlined black glyphs printed along its run, the symbol by it. Read by tools/trailmap/
pdf_resort.py, panel by panel (panels/<panel>/resort.py and decisions.py, which take AREA_OF and the rest from here);
prepare.py extracts them."""

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('front-side', 'Front Side'), ('mill-valley', 'Mill Valley')]
# the lifts (the app's areas), each with its top: OpenStreetMap's lift line on the USGS's 10 m elevation model
# (tools/trailmap/lift_tops.py; the map prints none)
AREAS = [('seventh-heaven', '7th Heaven', 5659), ('southern-cross', 'Southern Cross', 5601),
         ('double-diamond', 'Double Diamond', 5595), ('skyline', 'Skyline Express', 5238),
         ('tye-mill', 'Tye Mill', 5181), ('jupiter', 'Jupiter Express', 5167), ('kehrs-chair', "Kehr's Chair", 4902),
         ('brooks', 'Brooks Express', 4850), ('hogsback', 'Hogsback Express', 4826), ('daisy', 'Daisy', 4362)]
# each name's lift, read on the map: the lift whose top it is skied from (the trail list the resort publishes in season
# names the lifts too, but no capture of it holds a trail)
_AREAS = {
    'seventh-heaven': ['BOBBY CHUTE', 'NANCY CHUTE', 'SOLITUDE'],
    'double-diamond': ['BIG CHIEF BOWL', 'DOUBLE DIAMOND', 'LOWER DIAMOND', 'TRAPPER', 'WILD KATZ', 'SCHIM’S MEADOW'],
    'kehrs-chair': ['SHOWCASE', 'I-5', 'ELEVATOR'],
    'tye-mill': ['TYE BOWL', 'SKID ROAD', 'CREST TRAIL', 'ROLLER COASTER', 'PROMENADE'],
    'daisy': ['TYE CREEK', 'EASY STREET', 'TRAINING GROUNDS', '76 ROAD'],
    'hogsback': ['HAGEN HILL', 'SLOW POKE', 'HOOT ’N HOLLER', 'WALLS ST.', 'ROCK’N BLUE', 'BLUE TRAIL', 'PARACHUTE 1',
                 'PARACHUTE 2', 'INTERNATIONAL', 'HOG HEAVEN', 'HOG WILD', 'LOWER ROCK GARDEN', 'LITTLE TREE',
                 'CLOUD 9', 'ROCK GARDEN'],
    'skyline': ['SKYLINE', 'PANORAMA', 'EXHIBITION', 'MARMOT MEADOWS', 'COURT’S MEADOW', 'BARRIER BOWL',
                'BARRIER RIDGE', 'WINNIE CHUTES', 'LOWER TERMINAL'],
    'brooks': ['BROADWAY', 'MIDWAY', 'UPPER MAVERICKS', 'LOWER MAVERICKS', 'WATERFALL', 'ONE LIGHT', 'BRENNAN’S TRAIL'],
    'jupiter': ['WAYBACKS', 'AQUARIUS', 'AQUARIUS FACE', 'CORONA BOWL', 'GEMINI', 'LOWER GEMINI', 'LOWER AQUARIUS',
                'SHOOTING STAR', 'BOREALIS', 'OUTER LIMITS', 'LOWER VOLTAGE', 'SOUTH PARK'],
    'southern-cross': ['ORION', 'ORION CHUTES', 'PEGASUS', 'PEGASUS GULCH', 'ANDROMEDA FACE', 'POLARIS', 'SOUTH DIVIDE'],
}
AREA_OF = {n: a for a, ns in _AREAS.items() for n in ns}
# what the glyph reading runs together or misses (a word gap too narrow, letters on a curve), as the map prints them
RENAME = {'CRESTTRAIL': 'CREST TRAIL', 'BLUETRAIL': 'BLUE TRAIL', 'MARMOTMEADOWS': 'MARMOT MEADOWS',
          'P ANORAMA': 'PANORAMA', 'ONELIGHT': 'ONE LIGHT', 'PARACHUTE2': 'PARACHUTE 2', 'SLOWPOKE': 'SLOW POKE',
          'WALL ST.': 'WALLS ST.', 'CORO BOWL': 'CORONA BOWL', 'RION CHUTES': 'ORION CHUTES'}
# as the resort spells them (straight apostrophes; title case lowers the rest)
DISPLAY = {'HOOT ’N HOLLER': "Hoot 'n Holler", 'ROCK’N BLUE': "Rock 'n Blue", 'SCHIM’S MEADOW': "Schim's Meadow",
           'COURT’S MEADOW': "Court's Meadow", 'BRENNAN’S TRAIL': "Brennan's Trail", 'WALLS ST.': 'Walls St.'}
# the parks (orange, with their features' sizes: XS-S, S-M, M-L)
PARKS = {'TRAINING GROUNDS', 'MIDWAY', 'UPPER MAVERICKS', 'LOWER MAVERICKS'}
# names printed with no symbol and no line: the map's own note calls eleven of them "for reference only and not
# designated trails or runs" (Big Chief Bowl, Court's Meadow, Schim's Meadow, Tye Bowl and Winnie Chutes on the Front
# Side; Pegasus Gulch, Andromeda Face, Waybacks, Orion Chutes, South Park and Polaris Bowl in Mill Valley); with Barrier
# Bowl and Elevator they are markers at their names, black (the playbook's convention for an unrated bowl or face); the
# parks blue
REFERENCE = {'BIG CHIEF BOWL', 'COURT’S MEADOW', 'SCHIM’S MEADOW', 'TYE BOWL', 'WINNIE CHUTES', 'PEGASUS GULCH',
             'ANDROMEDA FACE', 'WAYBACKS', 'ORION CHUTES', 'SOUTH PARK', 'POLARIS'}
DEFAULT_SYMBOL = {**{n: 'square' for n in PARKS}, **{n: 'diamond' for n in REFERENCE | {'BARRIER BOWL', 'ELEVATOR'}}}
# what every panel drops: the lifts' names (printed along them), the peaks, the boundary's and the cliffs' notices
DROP = [(t, None) for t in (
    'TYE MILL', 'KEHR’S CHAIR', 'DAISY', 'HOGSBACK EXPRESS', 'SKYLINE EXPRESS', 'BROOKS', 'EXPRESS', '7TH HEAVEN',
    '7th HEAVEN', 'JUPITER EXPRESS', 'SOUTHERN', 'CROSS', 'BULL ’S TOOTH', 'BIG CHIEF MOUNTAIN', 'COWBOY MOUNTAIN',
    'MT STUART', 'THE CRADLE', 'MT DANIEL', 'MTHINMAN', 'COWBOY', 'MOUNTAIN', 'AREA', 'BOUNDARY', 'OUT', 'Of', 'BOUNDS',
    'DANGER', 'CLIFF AREA')]


def is_name(label):
    return True
