"""Schweitzer's maps read on crops, where the interactive maps' groups lack something (prepare.py adds these to what
the groups give), in map px of each panel's image (work/schweitzer/<panel>/map.png; tools/archive/schweitzer/show.py
draws the groups' labels and symbols over it, diamonds.py finds the black diamonds the Outback groups lack):

GROUP_NAMES {panel: {group name: (NAME, why)}}: a group named otherwise than the print and the report name it
LABELS   {panel: [(NAME, first letter (x, y), last letter (x, y))]}: names in no group, or in a group with no letters
SYMBOLS  {panel: [(kind, (x, y), NAME)]}: symbols the groups lack, each with its run
NO_SYMBOL {panel: {NAME: why}}: a group's symbol the print doesn't show
LINES    {panel: [(NAME, [(x, y), ...])]}: cat tracks (navy lines) the interactive map draws no line for, as waypoints
         along the print's line, through the gaps where its name and symbol are printed (prepare.py routes them on it)
"""
GROUP_NAMES = {
    'schweitzer-bowl': {
        'Crystal': ('Southside Park', 'its letters are the print\'s SOUTHSIDE PARK (a park by its orange pill), where '
                                      'the interactive map keeps an older run'),
        'Stiles': ('Stiles (upper)', 'the upper STILES (the lower is Lower Stiles: the report\'s Stiles (lower))'),
    },
    'outback-bowl': {
        '': ('Slapshot', 'a group with no name, its letters SLAPSHOT'),
    },
}

LABELS = {
    'schweitzer-bowl': [
        ("Britt's Bowl", (1686, 679), (1771, 536)),
        ('Loophole (lower)', (2325, 1707), (2543, 1629)),  # LOWER LOOPHOLE, along the boundary
        ('Stomping Grounds Terrain Park', (689, 971), (1011, 1286)),
        ('Bermuda', (1100, 1243), (1171, 1350)),
        ('Bunny Hills', (1632, 1589), (1614, 1671)),  # BUNNY / HILLS, on two lines
    ],
    'outback-bowl': [
        # Schweitzer Bowl's runs whose names the Outback map prints too, at its west edge
        ('Loophole Loop', (510, 1023), (713, 920)),
        ('Caboose', (607, 1027), (710, 957)),
        ('Skid Row', (683, 1037), (783, 960)),
        ('Trial Run', (740, 1050), (853, 963)),
        ('Down the Hatch', (880, 1067), (927, 880)),
        ('The Great Divide', (1194, 710), (1426, 602)),
        ('Vagabond', (1303, 1140), (1423, 1243)),
        ('Short Cut', (861, 1256), (889, 1180)),  # SHORT / CUT, on two lines
        ('North Ridge', (2291, 583), (2473, 653)),
        ('Kaniksu (upper)', (1887, 730), (1956, 489)),  # UPPER KANIKSU
        ('Blue Grass', (1661, 859), (1794, 756)),
        ('Casper', (1622, 894), (1733, 867)),
        ('Lakeside Runout', (1324, 1092), (1504, 908)),
        ("Will's Runout", (1396, 1136), (1530, 966)),
        ('Right On', (1420, 1176), (1492, 1104)),
        ('Triple Bypass', (1526, 1144), (1644, 964)),
        ('Roller Ghoster', (1610, 1410), (1670, 1157)),
        ('Colburn School', (2387, 1147), (2570, 967)),
        ('Know Fun', (1778, 989), (1856, 1110)),
        ('G-3 (upper)', (772, 1233), (872, 1322)),  # UPPER G-3
        ('Snow Ghost (upper)', (1863, 820), (2017, 937)),  # its upper printing (the group's letters are the lower)
        ("Pucci's Chute", (2270, 585), (2233, 793)),
    ],
}

SYMBOLS = {
    'outback-bowl': [
        ('diamond', (737, 940), 'Caboose'), ('diamond', (808, 945), 'Skid Row'), ('diamond', (861, 941), 'Trial Run'),
        ('diamond', (1100, 966), 'Debbie Sue'), ('diamond', (1142, 940), "Toomey's Trail"),
        ('diamond', (1314, 989), 'Shoot the Moon'), ('diamond', (1519, 897), 'Lakeside Runout'),
        ('diamond', (1540, 951), "Will's Runout"), ('diamond', (1658, 950), 'Triple Bypass'),
        ('diamond', (1669, 1066), 'Slapshot'), ('diamond', (1677, 1130), 'Roller Ghoster'),
        ('diamond', (1198, 1182), 'No Joke'), ('diamond', (1177, 1239), 'Revenge'),
        ('diamond', (1132, 1362), 'Glade-iator'), ('diamond', (894, 1344), 'G-3 (upper)'),
        ('diamond', (1294, 1646), 'G-3 (lower)'), ('diamond', (963, 1730), "Kathy's Yard Sale"),
        ('diamond', (673, 2318), "Phineas' Forest"), ('diamond', (1976, 500), 'Kaniksu (upper)'),
        ('diamond', (1812, 743), 'Blue Grass'), ('diamond', (1750, 870), 'Casper'),
        ('diamond', (2062, 867), 'Downhill Run'), ('diamond', (2401, 916), 'Siberia Runout'),
        ('diamond', (2571, 946), 'Colburn School'), ('diamond', (2665, 952), 'Study Hall'),
        ('diamond', (2701, 1180), 'Detention'), ('diamond', (2627, 1363), 'Recess'),
        ('double-diamond', (1790, 540), 'Lakeside Chutes'), ('double-diamond', (1711, 695), 'Misfortune'),
        ('double-diamond', (1586, 738), 'Whiplash'), ('double-diamond', (1524, 783), 'Australia'),
        ('double-diamond', (2177, 773), "Kohli's Big Timber"), ('double-diamond', (2217, 819), "Pucci's Chute"),
        ('double-diamond', (2452, 711), "Wayne's Woods"), ('double-diamond', (2506, 782), 'Siberia'),
    ],
}

NO_SYMBOL = {
    'schweitzer-bowl': {'Southside Park': 'the interactive map\'s square for its old run Crystal: the print has the '
                                          'park\'s orange pill'},
}

LINES = {
    'outback-bowl': [
        # the navy line from the summit down to Rowdy Grouse: The Great Divide to Down the Hatch's square, then Down
        # the Hatch to where the line turns east at the bottom, Vagabond on round and down to Cedar Park's square,
        # and Cedar Park down to the Outback Inn
        ('The Great Divide', [(1711, 444), (1600, 505), (1522, 550), (1445, 585), (1180, 708), (1050, 762),
                              (983, 795), (950, 830), (945, 848)]),
        ('Down the Hatch', [(945, 848), (940, 880), (937, 947), (933, 1013), (915, 1060), (905, 1090)]),
        ('Vagabond', [(905, 1090), (950, 1075), (1008, 1051), (1100, 1030), (1153, 1039), (1230, 1100), (1303, 1140),
                      (1423, 1243), (1453, 1263), (1497, 1320), (1547, 1447), (1503, 1537), (1493, 1603),
                      (1510, 1697), (1570, 1763), (1613, 1820), (1640, 1905)]),
        ('Cedar Park', [(1640, 1905), (1656, 2000), (1667, 2094), (1683, 2133)]),
        # from the top of the Idyle Our T-Bar down the boundary, its name printed twice in a gap of its line, to
        # the Outback Inn
        ('Little Blue Ridge Run', [(2800, 650), (2815, 800), (2834, 900), (2860, 1000), (2841, 1060), (2773, 1120),
                                   (2796, 1209), (2798, 1255), (2788, 1315), (2765, 1373), (2742, 1412), (2675, 1443),
                                   (2523, 1541), (2426, 1605), (2380, 1644), (2250, 1732), (2118, 1821), (2115, 1844),
                                   (2070, 1885), (1890, 1988), (1760, 2030)]),
    ],
}
