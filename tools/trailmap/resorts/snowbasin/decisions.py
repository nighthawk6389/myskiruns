"""Naming decisions for Snowbasin's map, settled on crops, keyed by points in map px (work/snowbasin/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # (work/snowbasin/crops/: each piece settled on a crop of it alone, the map's own lines visible under it)
    # names printed beside a line of their own that the auto-match gave another name, or none: WFO (three letters),
    # The Walrus, Dog Leg and Sunshine (each a leader line to its line), Needles Way, LMM (Lower Moose Mound: Moose
    # Mound's line on past its foot, blue), 119 (black type on its blue line, the square at its foot), FTS (see CUTS)
    ((292, 1069), 'WFO'), ((1329, 619), 'The Walrus'), ((1883, 500), 'Dog Leg'), ((1952, 500), 'Sunshine'),
    ((2057, 477), 'Needles Way'), ((1849, 1168), 'Lower Moose Mound'), ((2175, 1083), '119'),
    # Wildflower Downhill on past where a black line leaves it (its yellow casing and its diamond)
    ((3147, 1520), 'Wildflower Downhill'),
    # Dan's Run's blue line on past the foot of Cirque and Grizz to 25th St's (the only line on, no other name)
    ((1607, 1091), "Dan's Run"),
    # Hohmann's: its line forks at its diamond, one branch to Last Chance, the other to Coyote Bowl
    ((731, 1799), "Hohmann's"),
    # the black line from the Porcupine lift's top along the ridge to Powderhound Bowl (Porky Face leaves it)
    ((2620, 487), 'Powderhound Bowl'),
    # Lower Bear Springs' second line from its name down to the DeMoisy lift's foot
    ((928, 2312), 'Lower Bear Springs'),
    # Upper Elk Ridge on past its name to where Mid Elk Ridge's path starts (two lines leave it on the way)
    ((925, 596), 'Upper Elk Ridge'),
    # Strawberry Traverse's line west of the gondola's top: one straight line from the Elk Ridge runs across Mid Main
    # Street's top to where the name is printed
    ((1051, 710), 'Strawberry Traverse'), ((1253, 739), 'Strawberry Traverse'),
    # the link from Two Bit Street's foot to 119's (a square at either end): Two Bit Street's
    ((2135, 1135), 'Two Bit Street'),
    # one path, two runs (CUTS): Twist & Shout above the black link from Lower Elk Ridge, Gordon's Gully below
    ((869, 1082), 'Twist & Shout'), ((577, 1634), "Gordon's Gully"),
    # Trappers Trail above Upper Bear Springs' foot, Lower Bear Springs below
    ((1326, 1511), 'Trappers Trail'), ((1089, 2086), 'Lower Bear Springs'),
    # Mid Elk Ridge down to the junction at Gordon's foot, Lower Elk Ridge below
    ((1040, 1093), 'Mid Elk Ridge'), ((715, 1554), 'Lower Elk Ridge'),
    # Mid Main Street from Upper Main Street's foot (its square, then its name), and down to the junction where Coyote
    # Bowl and Trapper's Bypass leave it; Lower Main Street below (its square, its name)
    ((1123, 609), 'Mid Main Street'), ((1229, 792), 'Mid Main Street'), ((1159, 1566), 'Lower Main Street'),
    # Trapper's Bypass's path: from the gondola's top (its square) into Mid Main Street, then drawn again along Mid
    # Main Street's line (UNNAMED), then its own line from the junction
    ((1317, 801), 'Mid Main Street'), ((1311, 1375), 'Trapper’s Bypass'),
    # No Name from the ridge's east end (where Shooting Star leaves it) down; the ridge above, UNNAMED
    ((4364, 773), 'No Name'),
    # FTS from the John Paul lift's line down (see UNNAMED for the line above)
    ((3705, 1881), 'FTS'),
    # Hollywood down to where Grizzly Downhill joins, Grizzly Finish below
    ((3497, 1074), 'Hollywood'), ((3315, 1609), 'Grizzly Finish'),
    # Grizzly Start down to John Paul Lodge, Wildflower Start back up from it
    ((3708, 548), 'Grizzly Start'), ((3854, 546), 'Wildflower Start'),
    # Wildcat Ridge down to where Bash leaves it, Centennial below (its diamond, its name)
    ((2511, 1236), 'Wildcat Ridge'), ((2692, 1557), 'Centennial'),
    # Porcupine Traverse to Middle Bowl Traverse's line, Needles down beside the gondola to where City Hill leaves it,
    # Showboat below
    ((1891, 645), 'Porcupine Traverse'), ((2645, 1117), 'Needles'), ((2949, 1977), 'Showboat'),
    # Slo Road (round its loop) to the junction at 25th St's foot, Bear Hollow to where Stein's and Becker Face
    # leave it, Snow Shoe below
    ((1799, 1322), 'Slo Road'), ((2144, 1508), 'Bear Hollow'), ((2446, 2070), 'Snow Shoe'),
]
UNNAMED = [
    ((909, 1350), "the black link from Lower Elk Ridge and Wolverine down to Gordon's Gully's top: no name printed"),
    ((3587, 1144), "from the foot of The Jungle and Snow King down to Hollywood (Ellison's and The Burn leave it): "
                   "no name printed"),
    ((1049, 503), "from Upper Elk Ridge's top across White Room's foot to Upper Main Street's: no name printed"),
    ((3852, 1568), "from the foot of No Name and Shooting Star along the Lower Pyramids to the John Paul lift's line "
                   "(The Burn, Ellison's and Deane's end on it): no name printed"),
    ((3230, 1447), "the black line from Wildflower Downhill, where its casing turns away, down to Grizzly Finish: no "
                   "name printed"),
    ((1254, 1046), "Trapper's Bypass's path drawn again along Mid Main Street's line"),
    ((4148, 557), "the ridge from the tram's top past the patrol hut to No Name's top (Wildflower Start, Easter Bowl and "
                  "Shooting Star leave it): no name printed"),
]
CUTS = [
    ((869, 1082), (881, 1390)), ((1326, 1511), (1280, 1749)), ((1040, 1093), (1043, 1191)),
    ((1049, 503), (1097, 546)), ((1229, 792), (1238, 1228)),
    ((1311, 1375), (1242, 1215)), ((1317, 801), (1266, 877)),
    ((3852, 1568), (3600, 1658)), ((3251, 1109), (3209, 1349)), ((3497, 1074), (3338, 1357)),
    ((3708, 548), (3637, 671)), ((2511, 1236), (2679, 1477)),
    ((1891, 645), (2235, 781)), ((2645, 1117), (3049, 1740)),
    ((1799, 1322), (1922, 1302)), ((2144, 1508), (2269, 1649)),
    ((4364, 773), (4341, 514)),
]
TRACED = []
TRIMS = []
