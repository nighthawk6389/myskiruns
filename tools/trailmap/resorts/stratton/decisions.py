"""Naming decisions for Stratton, settled on crops, keyed by points in map px (work/stratton/map.png), so they survive
a re-extraction: pdf_resort.py finds the piece through each point. `pdf_resort.py stratton add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map draws)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    ((225, 1056), 'Lower Kidderbrook'), ((276, 1018), 'Lower Kidderbrook'),  # on up from its label to the uphill route
    ((22, 1439), 'Lower Kidderbrook'), ((92, 1695), 'Lower Kidderbrook'),  # from its circle down the boundary to the base
    ((780, 791), 'Free Fall'),  # below its double diamond, down to Churchill Downs
    ((1001, 650), 'Free Fall Gully'),  # its line beside its name (double dashes this season)
    ((1085, 845), 'Way Home'),  # from its square to its name
    ((2888, 954), 'Lower West Meadow'),  # from its name down through the family zone to Drifter Link's
    ((1554, 1168), 'Grizzly Access'),  # from its name down across Runaway to Lad's Legacy's
    ((1608, 440), 'Big D'),
    ((2945, 952), 'Lower Wanderer'), ((3005, 1144), 'Lower Wanderer'),  # either side of where it leaves the map  # its line beside its name, from The Chute down to Upper Tamarack's diamond
]
UNNAMED = [
    # the boxes' and names' leaders (black 1 pt strokes)
    ((1654, 194), "Summit Deck's leader"), ((1788, 219), "Hubert Haus's leader"), ((2591, 506), "the Family Zone's leader"),
    ((324, 790), "the boundary note's leader"), ((1960, 216), "Mike's Cut Through's leader (no line drawn for it)"),
    # lines the 2020-21 export draws that this season's map does not (its parks redrawn; Beeline and Betwixt now a
    # park's pill and a name, Spillway's and Yodeler's tops drawn again some 10 px off: TRACED)
    ((2047, 1055), 'no longer drawn'), ((2068, 1127), 'no longer drawn'), ((2187, 1276), 'no longer drawn'),
    ((1947, 1055), 'no longer drawn'), ((2068, 1543), 'no longer drawn'), ((2204, 1643), 'no longer drawn'), ((1810, 1096), 'drawn again elsewhere'), ((1893, 1188), 'drawn again elsewhere'),
    ((1903, 1523), 'a link with no name, from Lower Tamarack into the learning zone'),
    ((1974, 1018), "a lone dash by Tink's Link's name, all this season keeps of a line to the old Beeline"),
]
# Lower Wanderer's line runs off the image's right edge and back (the 2020-21 page is wider than this season's
# painting): cut where it comes back, and the part beyond the edge trimmed away (TRIMS); the overlay's two parts are
# joined along the edge
CUTS = [((3042, 1060), (3019, 1137))]
# lines this season's map draws where the 2020-21 export has none, read on crops of this season's image
# (tools/trailmap/trace_ink.py along the line's colour)
TRACED = [
    ('Suntanner', [(1838, 1050), (1874, 1063), (1904, 1079), (1935, 1098), (1952, 1109), (1989, 1149), (2013, 1176),
                   (2038, 1203), (2055, 1222)]),  # from the Mid Mountain Lodge to its square
    ('Suntanner', [(2140, 1308), (2163, 1337), (2200, 1377), (2250, 1430), (2288, 1470), (2300, 1487), (2333, 1527),
                   (2367, 1571), (2380, 1590)]),  # on from its name between the two lifts to the base
    ('Spillway', [(1789, 1080), (1836, 1130), (1847, 1143)]),  # from the lodge to its square
    ('Yodeler', [(1847, 1143), (1855, 1149), (1888, 1179), (1923, 1211), (1937, 1222)]),  # on to its square
    ('Shortcut Big Ben', [(1292, 1016), (1269, 1041), (1256, 1056)]),  # from Shortcut Gentle Ben's name to its own
    ('Shortcut Big Ben', [(1186, 1236), (1179, 1260), (1165, 1286), (1158, 1303), (1147, 1330), (1140, 1360),
                          (1139, 1423), (1131, 1427)]),  # from its square down to Tree Top Way's top
    ('Village Walk', [(2164, 1630), (2178, 1637), (2193, 1648), (2214, 1667)]),  # on past its name
    ('Tyrolienne', [(2242, 1582), (2253, 1593), (2265, 1603), (2312, 1645)]),  # on past its name to the base
]
TRIMS = [((2945, 952), (3022, 1018))]  # Lower Wanderer: the part beyond the map's right edge
