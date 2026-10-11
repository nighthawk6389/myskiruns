"""Naming decisions for Brighton's map, settled on crops, keyed by points in map px (work/brighton/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # Elk Park Access: the blue line under its name from the Great Western top to Elk Park's square; Elk Park from
    # its square down the left side and round to the Great Western mid-station, where Golden Needle goes on east
    # past its square (one stroke for the three: cut at the square and at the mid-station)
    ((520, 606), 'Elk Park Access'), ((519, 755), 'Elk Park'), ((428, 1120), 'Elk Park'),
    ((751, 1355), 'Golden Needle'), ((1029, 1460), 'Golden Needle'),
    # Elk Park Ridge: the black line along the ridge from the summit (a diamond), joining Elk Park's line, then off it
    # again to the diamond at its name
    ((445, 781), 'Elk Park Ridge'), ((428, 1221), 'Elk Park Ridge'),
    ((498, 654), 'Wrangler'),  # the black line from the summit (a diamond) straight on into Wrangler's
    # Rein's Run: the two black lines from Elk Park Access's end either side of its name, crossing at its double
    # diamond, both on to Lone Star's top
    ((726, 840), "Rein's Run"), ((754, 830), "Rein's Run"),
    ((920, 715), 'True Grit'), ((968, 876), 'True Grit'),  # from Western Trail's square to its double diamond; below
    ((722, 694), "Clark's Roost"), ((908, 919), "Clark's Roost"),  # from Western Trail's name; below its diamonds
    ((1038, 892), 'Western Trail'),  # its line back west from the bend to Lone Star's top (Thor, Thunderhead off it)
    # Pioneer: the blue line from the Snake Creek top past its square and name to the light-bulb sign; Great Divide
    # on from there along its name to Pine Martin's square (one stroke: cut at the sign)
    ((1385, 778), 'Pioneer'), ((1337, 1047), 'Great Divide'),
    ((1287, 1156), 'Chicken Out'),  # the branch off Great Divide through its square and along its name
    ((1505, 805), 'Hard Coin'),  # the black line by its name and double diamond, down past the lift's mid-station
    ((525, 1223), 'Golden Needle'),  # the blue line from Aspen Glo down to the mid-station, where Golden Needle starts
    # Silver Spur: its black line on past its diamond and a second one, down to Great Western's name
    ((804, 1633), 'Silver Spur'), ((996, 1775), 'Silver Spur'),
    ((1146, 2034), 'Great Western'),  # the blue run-out from under its name to the base
    ((1498, 1868), 'Scout'),  # its line on from the end of its name, past its square to the base
    # the Crest 6 top: Thunder Road's start from the light-bulb sign west to its square; Tantamount off Pacific
    # Highway's line past its square and along its name; Snow Drift off Pacific Highway past its square
    ((1927, 838), 'Thunder Road'), ((1862, 856), 'Thunder Road'), ((1899, 995), 'Tantamount'),
    ((2018, 1151), 'Snow Drift'),
    # the parks: My-O-My down to the pill above Candyland's name (one stroke: cut at the pill); Pee-Wee's line
    ((1729, 983), 'My-O-My'), ((1671, 1283), 'Candyland'), ((1763, 1269), 'Pee-Wee'),
    # the black line by the Majestic lift: Face from its diamond, 2nd Face along its name to the light-bulb sign,
    # Zane's from there to its name (one stroke: cut above 2nd Face's name and at the sign)
    ((1728, 1414), 'Face'), ((1733, 1512), '2nd Face'), ((1748, 1666), "Zane's"),
    # SS Traverse from its square down to JB's square, Powder Alley from there along its name (one stroke)
    ((1581, 1560), 'SS Traverse'), ((1571, 1777), 'Powder Alley'),
    # Shoulder: from the light-bulb sign along its name, down beside the lift to Mary Main's square
    ((1801, 1329), 'Shoulder'), ((1834, 1409), 'Shoulder'),
    ((1841, 1318), 'Pacific Highway'),  # its line on past the Crest 6 lift's label, down to Shoulder's
    ((1870, 1526), 'Cat Track'),  # the blue line along its name, down to Mary Main's
    # Mary Main from its square past the light-bulb sign and along its name to the next square, Lower Mary from
    # there along its name to the base (one stroke: cut at that square)
    ((1811, 1640), 'Mary Main'), ((1763, 1925), 'Lower Mary'),
    # Mary Back over the light-bulb sign and along its name to Lost Maid's circle, Lost Maid from there along its
    # name to the base (one stroke: cut at the circle)
    ((1930, 1360), 'Mary Back'), ((1806, 1860), 'Lost Maid'),
    ((1789, 1760), 'Lower Majestic'),  # from its circle down along its name (the link above it from Mary Back's)
    ((2010, 1893), 'Majestic Access'),  # the blue line along its name, from Canyon's name to the Majestic base
    ((1936, 2139), 'Milly Access'),  # its line on from its square to the base
    ((1537, 1203), 'Great Divide'),  # its line on past Pine Martin's square down to Pick 'Em Up's
    # Milly: Scree Slope from the Milly top past its diamond and along its name to Scree Chute's double diamond,
    # Scree Chute from there along its name, past its second diamond, both its lines to the base (one stroke)
    ((2795, 999), 'Scree Slope'), ((2535, 1371), 'Scree Chute'), ((2443, 1501), 'Scree Chute'),
    # Lone Pine from the Milly top past its diamond and along its name to Randy's Chute's double diamond, Randy's
    # Chute from there along its name past its second diamond to Canyon (one stroke)
    ((2978, 1058), 'Lone Pine'), ((2692, 1341), "Randy's Chute"),
    ((2868, 1272), 'Little Milly'),  # from Backbone's top past its diamond and along its name
    ((2898, 1358), "Devil's Dip"),  # from Backbone's line past its diamond and along its name to Canyon's
    # Chute 2 from Backbone's line past its diamond and along its name to the Milly mid-station, Wee Willow from
    # there along its name to its diamond and Canyon's circle (one stroke: cut at the mid-station)
    ((3001, 1365), 'Chute 2'), ((2415, 1705), 'Wee Willow'),
    # Main Street: the green line from Backdoor's name past its circle and the light-bulb signs, along its name,
    # and on south-west to Waterfall's circle; Canyon west from its junction past both its names to the base;
    # Waterfall from its circle along its name (two strokes, each cut at a junction)
    ((3147, 1336), 'Main Street'), ((2867, 1575), 'Main Street'), ((2767, 1533), 'Canyon'),
    ((2107, 2121), 'Canyon'), ((2720, 1866), 'Waterfall'), ((2354, 2117), 'Waterfall'),
    ((2341, 2085), 'Perris Bowl'),  # from Waterfall's line past its square and name to the base
    # Christy Bowl from Waterfall's circle past its square and along its name to the light-bulb sign, Slalom Hill
    # from there along its name (one stroke: cut at the sign)
    ((2570, 1901), 'Christy Bowl'), ((2218, 2264), 'Slalom Hill'),
    ((3145, 1179), 'Backdoor'),  # from under its name past its square down to Backbone's line
    ((3192, 1648), 'Backbone'),  # its line on below its squares to Easy Out's square
    ((3205, 1406), 'Evergreen'), ((3290, 1711), 'Evergreen'),  # from Backbone's top past its square, along its name
    ((3252, 1432), 'Sol Bright Access'),  # the black line from the Milly top to the Sol Bright gate by its name
]
UNNAMED = [
    ((1285, 1095), "a black stub with a diamond from under Great Divide's name down to Chicken Out's line, where "
                   "Lower Pioneer's blue line starts: no name printed by it"),
    ((970, 1598), "a blue link from Rockin' R's line past a square, across Old Western's, to Scout's name: no name "
                  "printed by it"),
    ((1253, 1975), "the Explorer lift's beginner lines (the report's Explorer Main and Simon's Way): no name printed"),
    ((1366, 1966), "the Explorer lift's beginner lines: no name printed"),
    ((1426, 1919), "the Explorer lift's beginner lines: no name printed"),
    ((1862, 908), 'a black line with a diamond from Thunder Road\'s square down to Wintergreen\'s: no name printed'),
    ((1800, 933), 'a black line with a diamond from Thunder Road\'s name down to Wintergreen\'s: no name printed'),
    ((1676, 1585), "the terrain-park lane (orange) down the Majestic lift: the report's Upper and Lower Majestic "
                   "parks, no name printed by it"),
    ((2940, 2194), 'the black line on from the Sol Bright gate down the ski-area boundary, past its diamonds, to '
                   'the Milly base: no name printed by it (the boundary\'s own label beside it)'),
    ((1074, 2095), 'the blue run-out from the square below Desperado and Elk Park Ridge to the base: no name printed '
                   'by it'),
]
CUTS = [((520, 606), (570, 668)), ((751, 1355), (607, 1307)), ((1385, 778), (1260, 900)),
        ((970, 1598), (1245, 1790)), ((1729, 983), (1666, 1198)), ((1728, 1414), (1730, 1470)),
        ((1748, 1666), (1735, 1648)), ((1581, 1560), (1556, 1612)), ((1811, 1640), (1782, 1809)),
        ((1930, 1360), (1954, 1563)), ((1834, 1409), (1831, 1365)), ((2535, 1371), (2607, 1227)), ((2978, 1058), (2815, 1170)),
        ((3001, 1365), (2564, 1641)), ((2767, 1533), (2905, 1556)), ((2720, 1866), (2748, 1725)),
        ((2570, 1901), (2333, 2197)), ((3252, 1432), (3322, 1470))]
TRACED = []
TRIMS = []
