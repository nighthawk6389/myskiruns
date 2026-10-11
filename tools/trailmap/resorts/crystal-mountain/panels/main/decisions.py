"""Naming decisions for Crystal Mountain's main panel, settled on crops, keyed by points in map px (work/crystal-mountain/main/map.png), so they survive
a re-extraction: pdf_resort.py finds the piece through each point. `pdf_resort.py crystal-mountain/main add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map draws)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # each by the name printed along it, the symbol at its end, or the run it continues (the interactive map's line
    # where it settles a choice: Bull Run, Little Shot, Little Portillo, Employee Housing)
    ((961, 1586), 'Snow Garden'), ((966, 1641), 'Easy Street'),  # through their circles
    ((1074, 1149), "Upper Chappelle's"),  # from the Forest Queen top to its square
    ((1375, 1577), 'Broadway'),  # from the Midway down to its circle
    ((1262, 1594), 'After Burn'),  # beside its name, down from Sideburn's square
    ((1330, 1458), "Wally's Way"),  # from its square
    ((1454, 1323), "Gandy's Run"),  # from Lucky Shot down to its square
    ((1531, 1282), 'Little Shot'), ((1572, 1419), 'Little Shot'),  # its zigzag from its square to Upper Arwine's top
    ((1504, 1397), "Mel's Left"),  # down to its square
    ((1384, 1112), 'Little Portillo'),  # from its diamond to Lucky Shot's top
    ((1930, 1951), "Lower Arwine's"),  # on past its name to the Chinook base
    ((1713, 1632), "Middle Ferk's"), ((1818, 1258), "Middle Ferk's"),  # from Upper Ferk's end to Lower Ferk's diamond
    ((1864, 1893), "Lower Ferk's"),  # on below its name to the Chinook base
    ((1889, 1327), 'Bull Run'), ((1843, 1160), 'The Plunge'),  # down to their symbols
    ((2027, 1276), 'Exterminator'),  # from West Face's diamond to its double diamond
    ((2265, 1296), 'Sluiceway'),  # down to its diamond
    ((2242, 1259), 'Huckleberry'),  # on from its name down to the Green Valley base
    ((2436, 1189), "Willie's Run"), ((2499, 1244), 'Right Angle'),  # from the road to their diamonds
    ((2484, 1479), 'I-405'), ((2400, 1512), 'I-405'),  # on from its name across Right Angle Trees to Kelly's Gap Road
    ((1663, 1602), 'Cutover'),  # on past Deer Fly's diamond
    ((1255, 1838), 'Boondoggle'),  # its hook off the line above Quicksilver's base
    ((1644, 1985), 'Discover Meadow'), ((1863, 2072), 'Discover Meadow'),  # the learning area's lines
    ((2849, 1916), 'To Lot H'), ((2869, 1777), 'To Lot H'),  # either side of its name
    ((2717, 1653), 'Employee Housing'),  # on below its name to I-5
    ((1823, 2269), 'Bluebell Trail to Parking Lot C'),  # on past its name
    ((1186, 1388), 'Rolling Knolls'),  # the tick from Downhill to its square
    ((1112, 1477), 'Little Magoo'), ((1165, 1568), 'Lower Magoo'),  # below their squares
]
UNNAMED = [
    ((1061, 1477), "a link from Lower Chappelle's to the Magoos, no name printed on it"),
    ((2895, 1315), 'the Otto Bahn traverse on into Northway past the N10 gate, named only on the Northway panel'),
]
# the Magoos: one line beside the Forest Queen, Mr. Magoo from its name, Little Magoo from its square, Lower Magoo from
# its (each name printed left of the line by its square)
CUTS = [((1104, 1450), (1104, 1436)), ((1150, 1545), (1147, 1531))]
TRACED = []
TRIMS = []
