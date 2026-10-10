"""Big Bear Mountain Resort's maps read on crops, where the interactive maps' groups lack something (prepare.py adds
these to what the groups give), in map px of each panel's print (work/big-bear/<panel>/map.png):

LABELS   {panel: [(NAME, first letter (x, y), last letter (x, y))]}: a printed name in no group, or on a panel whose
         groups' symbols aren't where the print has them (Snow Valley: its interactive map is an older edition)
SYMBOLS  {panel: [(kind, (x, y), NAME)]}: symbols the groups lack, each with its run (a label is made at each whose
         name has no LABELS entry on the panel)
LINES    {panel: [(NAME, class, [(x, y), ...])]}: on a panel whose lines are the interactive map's, a run it draws no
         line for, as points along the run's painted slope
"""
LABELS = {
    # Bear Mountain's names in no group (crops tiles/, tiles2/): the beginner runs, the parks' runs and pipes, the
    # Park Runs, Expressway, The Gulch, Showdown's two
    'bear-mountain': [
        ('Learning Curve', (373, 1012), (488, 933)),
        ('Easy Street', (458, 1100), (490, 1015)), ('Easy Street', (665, 1232), (770, 1265)),
        ('Easy Street', (1013, 1385), (1115, 1440)),
        ('Amusement Park', (1370, 1135), (1440, 1020)),
        ('Central Park', (1490, 1335), (1515, 1250)),
        ('Half Pipe (13ft)', (1530, 1410), (1570, 1325)), ('Modified Pipe (18ft)', (1615, 1430), (1655, 1340)),
        ('Expressway', (1710, 905), (1790, 835)), ('Expressway', (1965, 818), (2090, 790)),
        ('The Gulch', (1755, 962), (1830, 1030)),
        ('Park Run (Lower)', (1795, 1290), (1855, 1165)),
        ('Park Run (Face)', (1885, 1040), (1965, 955)),
        ('Park Run (Upper)', (2015, 485), (2095, 610)),
        ("Outlaw's Alley", (2228, 690), (2318, 758)),
        ('Street Scene', (2225, 730), (2295, 795)),
    ],
    # Snow Valley's names (tiles/, cat.png): all of them, the interactive map being an older edition whose names and
    # symbols the 2025-26 print has moved
    'snow-valley': [
        ('East Slide', (550, 350), (580, 445)), ('The Face', (630, 295), (642, 385)),
        ('Show Me', (725, 275), (745, 370)), ('Snake Run', (850, 265), (880, 385)),
        ('Nord Valley', (960, 195), (1085, 260)), ('West Slide', (1100, 295), (1200, 385)),
        ('Bobcat Alley', (630, 645), (738, 532)), ("Richard's", (645, 722), (737, 790)),
        ('Snow Bowl', (568, 780), (688, 845)), ('Upper Wine Rock', (540, 940), (570, 1145)),
        ('The EDGE', (390, 1035), (415, 1150)), ('Bubble Gum', (660, 925), (795, 1005)),
        ('West Run', (775, 1035), (880, 1090)), ('Quickie', (600, 1095), (615, 1180)),
        ('Race Peak', (695, 1110), (790, 1195)), ('Surprise Run', (790, 1120), (920, 1215)),
        ('Lower Wine Rock', (720, 1205), (905, 1315)), ('The Chute', (620, 1270), (628, 1385)),
        ('Big Bowl', (668, 1440), (695, 1545)), ('The Ladder', (735, 1410), (760, 1550)),
        ('Little Bowl', (532, 1520), (575, 1645)), ('Show Off', (648, 1555), (710, 1650)),
        ('East Bowl', (380, 1605), (455, 1700)), ('Mambo Alley', (880, 1545), (975, 1415)),
        ('Pipeline', (1045, 1520), (1075, 1425)), ('Lake Run', (925, 1755), (1005, 1670)),
        ('Thunder Mountain', (670, 1775), (715, 1995)), ('Eagle Flats', (395, 1850), (515, 1900)),
        ('Graduation', (335, 1885), (445, 1955)), ('Coyote Flats', (260, 1960), (395, 2030)),
        ('Cat Track', (895, 830), (1025, 760)),
    ],
}
SYMBOLS = {
    # Snow Summit's runs the interactive map has no group for (cc3, cc5 crops): Cruiser's circles by its two labels
    # and on its line, Skyline Creek's, Sundown's; Westridge Park's squares along its line (the report's Upper and
    # Lower: one line, the name printed three times), ZZYZX Park's by its label
    'snow-summit': [
        ('circle', (1531, 375), 'Cruiser'), ('circle', (1727, 490), 'Cruiser'), ('circle', (2001, 579), 'Cruiser'),
        ('circle', (2045, 716), 'Cruiser'),
        ('circle', (1557, 340), 'Skyline Creek'), ('circle', (1794, 469), 'Skyline Creek'),
        ('circle', (2328, 670), 'Skyline Creek'),
        ('circle', (2192, 759), 'Sundown'),
        ('square', (1619, 503), 'Westridge Park'), ('square', (1755, 766), 'Westridge Park'),
        ('square', (1849, 1032), 'Westridge Park'), ('square', (1597, 1348), 'Westridge Park'),
        ('square', (1671, 725), 'ZZYZX Park'),
    ],
    # Bear Mountain's (symfind on the print, each checked on tiles/ and tiles2/): by the names above, and Hidden
    # Valley's square (its group has only its park pill)
    'bear-mountain': [
        ('circle', (511, 904), 'Learning Curve'),
        ('circle', (567, 999), 'Easy Street'), ('circle', (621, 1231), 'Easy Street'),
        ('circle', (1008, 1369), 'Easy Street'),
        ('circle', (1456, 1027), 'Amusement Park'), ('square', (1498, 1236), 'Central Park'),
        ('square', (1807, 836), 'Expressway'), ('square', (2090, 775), 'Expressway'),
        ('circle', (1826, 1050), 'The Gulch'),
        ('circle', (1837, 1150), 'Park Run (Lower)'), ('circle', (1762, 1364), 'Park Run (Lower)'),
        ('square', (1985, 948), 'Park Run (Face)'), ('square', (2061, 878), 'Park Run (Face)'),
        ('square', (2024, 480), 'Park Run (Upper)'),
        ('square', (2281, 736), "Outlaw's Alley"), ('square', (2173, 708), 'Street Scene'),
        ('square', (1644, 1005), 'Hidden Valley'),
        # Geronimo's double diamonds, outlined with its letters in one fill of its group (ger.png)
        ('double-diamond', (318, 210), 'Geronimo'), ('double-diamond', (527, 620), 'Geronimo'),
    ],
    # Snow Valley's, read on tiles/: each by its name (the Cat Track prints none)
    'snow-valley': [
        ('diamond', (558, 315), 'East Slide'), ('diamond', (633, 255), 'The Face'),
        ('double-diamond', (720, 230), 'Show Me'), ('double-diamond', (848, 230), 'Snake Run'),
        ('square', (942, 180), 'Nord Valley'), ('square', (1077, 283), 'West Slide'),
        ('square', (612, 658), 'Bobcat Alley'), ('square', (627, 710), "Richard's"),
        ('square', (548, 770), 'Snow Bowl'), ('square', (542, 915), 'Upper Wine Rock'),
        ('square', (387, 1005), 'The EDGE'), ('square', (815, 1015), 'Bubble Gum'),
        ('diamond', (755, 1033), 'West Run'), ('diamond', (603, 1063), 'Quickie'),
        ('diamond', (695, 1082), 'Race Peak'), ('diamond', (768, 1110), 'Surprise Run'),
        ('square', (705, 1185), 'Lower Wine Rock'), ('square', (625, 1240), 'The Chute'),
        ('diamond', (670, 1413), 'Big Bowl'), ('double-diamond', (738, 1390), 'The Ladder'),
        ('diamond', (530, 1495), 'Little Bowl'), ('diamond', (643, 1535), 'Show Off'),
        ('square', (375, 1582), 'East Bowl'), ('square', (865, 1570), 'Mambo Alley'),
        ('diamond', (1027, 1540), 'Pipeline'), ('diamond', (912, 1772), 'Lake Run'),
        ('circle', (677, 1750), 'Thunder Mountain'), ('circle', (315, 1808), 'Eagle Flats'),
        ('square', (315, 1875), 'Graduation'), ('circle', (250, 1940), 'Coyote Flats'),
    ],
}
LINES = {
    # Snow Valley's cat track (cat2.png, bg.png): the red dashed line from the summit's east side round and down past
    # its label to the foot of Surprise Run (the interactive map has no group for it)
    'snow-valley': [
        ('Cat Track', 'blue', [(1100, 550), (1145, 575), (1180, 600), (1190, 640), (1160, 680), (1110, 700),
                               (1095, 725), (1080, 760), (1040, 780), (980, 795), (940, 810), (880, 830),
                               (840, 840), (800, 855), (788, 880), (795, 920), (815, 960), (845, 995), (872, 1022),
                               (895, 1060), (910, 1100), (920, 1150), (926, 1200), (928, 1260)]),
    ],
}
