"""Aspen Mountain's 2025-26 trail map (aspensnowmass.com, its trail-maps page: one Illustrator page, drawn like
Snowmass's): the whole mountain, and at the top right two insets drawing the summit and Hero's larger. Trail lines
are vectors over a 100 dpi painting: blue and black strokes, the extreme terrain a black line in a yellow casing;
names are white text on a pill in the run's colour, set on the run's line. Read by tools/trailmap/pdf_resort.py,
panel by panel (panels/<panel>/resort.py and decisions.py, which take NAMES, AREA_OF and the rest from here);
prepare.py extracts them."""

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('main', 'Whole mountain'), ('summit', 'Summit'), ('heros', "Hero's")]
# the printed summits, each with its elevation as printed: Hero's (the Hero's lift's top, printed in its inset) and
# Aspen Mountain's (the rest)
AREAS = [('heros', "Hero's", 11262), ('aspen-mountain', 'Aspen Mountain', 11212)]

# no trail report: Aspen Snowmass's grooming feed lists no trails for Aspen Mountain out of season (the reports
# README, "Aspen Snowmass"); the names as printed, spelled out here (NAMES matches each printed name to its spelling by
# its letters), names printed in parts joined first (each panel's JOIN)
NAMES = [
    "Hero's Chutes #1", "Hero's Chutes #2", 'Pancake House Glade', "Jim's", 'Cutoff', 'Buckhorn', "Walsh's", 'Copper',
    'Silver Bell', 'Summit', 'Midway Road', "Hyrup's", 'Rideout', 'Midnight', 'Midnight Glades', 'Kristi',
    'Dipsy Doodle', '1 & 2 Leaf', 'Bellissimo', "Blondie's", 'North American', 'Pump House Hill', 'Blazing Star',
    'Tourtelotte Park', 'Pussyfoot', 'Buddy System', 'Percy', 'Lower Kristi', 'Lazy Boy', 'Mike Drop', 'Silver Dip',
    "Lower Walsh's", "Seibert's", 'Hodge Podge', "Gretl's", "Knowlton's", 'North Star', 'Deer Park', "Red's Run",
    'Back of Bell #1', 'FIS Trail', 'Sunrise/Sunset', 'Back of Bell #2', 'Bear Paw', 'Face of Bell', 'Upper Roch Run',
    'Copper Connector', 'Keith Glen', 'International Road', 'S1', 'Glade #1', 'Bell Meadow', 'Short Snort',
    "Ruthie's Run", 'Ridge of Bell', 'Zaugg Dump', 'Copper Bowl', 'Glade #2', "Perry's Prowl", 'Shoulder of Bell',
    "Gene Reardon's Run", 'Roch Run', 'Glade #3', 'Last Dollar', 'Summer Road', 'Spar Gulch', "Gent's Ridge",
    'Nose of Bell', 'Schiller Road', 'Cone 1', 'Aztec', 'Cone 2', "Rayburn's", 'Silver Queen', 'Bonnie Bell',
    'Silver Queen Ridge', 'Spring Pitch', 'Traynor Ridge', 'Lower Roch Run', 'Jackpot', 'Silver Rush', 'T1', 'T2',
    'T3', 'T4', 'T5', 'T6', 'Kleenex Corner', 'Magnifico Road', 'Super 8', 'Corkscrew', 'Bingo Glades',
    'Corkscrew Gully', '1A Lift Line', 'Strawpile', 'Magnifico', 'Niagra', 'Upper Little Nell', 'Franklin Dump',
    'FIS Slalom Hill', 'Tower Ten Road', 'Lazy 8 Gully', 'Beattie Way', 'Tower 7 Road', 'Lower Corkscrew', 'W 5th Ave',
    'Little Nell', 'Normandy', 'Schuss Gully', 'Norway', 'Easy Chair', 'Starwalk', "Loushin's", 'First Tracks',
    "Harris's Wall", 'Lens Cap', 'Papa Bear', 'E.E.K.!', 'Powerline', 'Cory-Bob', "Here's To...", "Elli's", 'Rewrite',
    'Legal Tender', 'Fat City', "Ollie's Yot", "D'Kine Bowl", 'El Avalanchero Glade']
AS_PRINTED = True
# the runs off the Hero's lift (most printed only in its inset), and Walsh's, Hyrup's and Kristi above it (the map's
# notice groups them with Hero's terrain)
AREA_OF = {n: 'heros' for n in (
    "Hero's Chutes #1", "Hero's Chutes #2", 'Pancake House Glade', 'Buddy System', 'Rideout', "Jim's",
    "Lower Walsh's", 'Lower Kristi', 'Mike Drop', "Walsh's", "Hyrup's", 'Kristi', 'Hodge Podge', 'Powerline',
    "Harris's Wall", "Loushin's", 'Papa Bear', 'E.E.K.!', 'Cory-Bob', "Here's To...", 'Legal Tender', 'Rewrite',
    'Fat City', 'Starwalk', "Ollie's Yot", "D'Kine Bowl", 'Lens Cap', "Elli's", 'First Tracks',
    'El Avalanchero Glade', 'E=m(Ski)² Glade')}


def area(c):
    return 'aspen-mountain'


def is_name(label):
    return True  # prepare.py keeps the names (white text on a blue or black pill) only


# the rating is the pill's colour (prepare.py: a black name on a yellow-cased line, on a line with a pair of
# diamonds, or by an EX mark, is "expert"); the map has no green runs
COLOR_SYMBOL = {'green': 'circle', 'blue': 'square', 'black': 'diamond', 'expert': 'double-diamond'}
# names printed in parts (two or three lines), in reading order: each panel's JOIN (a part is its text, or (text,
# (x, y)): the label printing it near that point, in the panel's map px)
SPLIT = {}
# the printed typo GENTELMEN'S; E=m(SKI) GLADE with its squared 2 set on the second line
# (GENTELMEN'S RIDGE, printed along the ridge, and GENT'S RIDGE, at its foot, are on one line: one run)
RENAME = {'GENTELMEN’S RIDGE': "Gent's Ridge", 'E=m(SKI) GLADE 2': 'E=m(Ski)² Glade'}
DISPLAY = {}
GLADES = set()
PARKS = set()
