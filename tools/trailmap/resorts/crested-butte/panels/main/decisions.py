"""Naming decisions for Crested Butte's main panel, settled on crops, keyed by points in map px
(work/crested-butte/main/map.png), so they survive a re-extraction: pdf_resort.py finds the piece through each point.
`pdf_resort.py crested-butte/main add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
# every undecided piece of the first build settled on per-piece crops (the piece in magenta, its neighbours named)
CHECKED = [
    # the summit and the front side
    ((2460, 733), 'Ruby Road'),  # the traverse under Triangle and Monument, its name printed in its gap to the west
    ((2206, 735), 'Ruby Road'), ((2260, 733), 'Ruby Road'), ((2305, 733), 'Ruby Road'),
    ((2591, 755), 'Upper International'),  # from the gate in the fence down to its diamond
    ((2443, 719), 'Monument'),  # a dash of its line below its name
    ((2280, 675), 'Triangle'),  # the right leg below its diamond
    ((2414, 861), 'Twister'),  # the solid line from its diamond (the dashed one beside its name too)
    ((2336, 566), 'Windy Gap'),  # the tick below its square
    ((3349, 1051), 'Banana Exit'),  # its line west of its diamond
    ((3434, 1529), 'Lower International'),  # on from its name down to the base
    ((2440, 1196), 'Rollercoaster'),  # the dash between ROLLER and COASTER
    ((2577, 1257), 'Peanut'),  # the second line from its name, down to the lift
    ((2863, 1160), 'Lower Twister'),  # the line down into its circle
    # Yellow Brick Road: from the top of the Paradise lift (its circle on the dashed line at the EZ sign) east to the
    # front side, then back on itself (the switchback above Aspen Park Road)
    ((1794, 867), 'Yellow Brick Road'), ((1842, 889), 'Yellow Brick Road'), ((1886, 897), 'Yellow Brick Road'),
    ((1930, 897), 'Yellow Brick Road'), ((2624, 994), 'Yellow Brick Road'), ((2400, 1052), 'Yellow Brick Road'),
    ((2091, 941), 'Yellow Brick Road'),  # through its EZ sign west of its name
    # Aspen Park Road: on east from its name, down through the Championships in a zigzag (EZ signs) to T-Bar Road
    ((3240, 1110), 'Aspen Park Road'), ((3298, 1154), 'Aspen Park Road'), ((3186, 1269), 'Aspen Park Road'),
    ((3101, 1300), 'Aspen Park Road'), ((3093, 1319), 'Aspen Park Road'), ((3129, 1328), 'Aspen Park Road'),
    ((3311, 1290), 'Aspen Park Road'), ((3409, 1331), 'Aspen Park Road'),
    # the back side (the Paradise lift's west side: each square on its run's dashed line)
    ((1990, 738), 'Upper Ruby Chief'),  # a dash right of its square
    ((1751, 856), 'Paradise Bowl'),  # down from its name
    ((1744, 1155), 'Upper Canaan'),  # on from its name to the lift's top
    ((1749, 1169), 'Bear'),  # the first dash below its square
    ((1636, 1234), 'Lower Canaan'), ((1603, 1349), 'Lower Canaan'),  # through its square
    ((1624, 1235), 'Upper Gallowich'),  # up from its square
    ((1656, 1503), 'Lower Ruby Chief'),  # on past its square to the Paradise base
    ((1277, 1609), 'Upper Treasury'),  # on down to Lower Treasury's square
    ((1377, 1659), 'Middle Gallowich'),  # a tick beside its square
    ((1921, 1382), 'Ruby Access'),  # on down to the square where Gus' Way starts
    ((1918, 1548), "Gus' Way"), ((1924, 1698), "Gus' Way"),  # from that square down past its second one to its name
    ((2003, 1241), "Bubba's Shortcut"),  # its line's west end
    ((2112, 1280), 'Mineral Point'),  # up from its line toward Ruby Access
    # Ten Peaks
    ((2693, 1863), 'Gunsight Pass'), ((2605, 1869), 'Gunsight Pass'),  # its arrowed line west past the Umbrella Bar
    ((2800, 1818), "Splain's Gulch"),  # its arrow's tail
    ((3020, 1750), 'Topsy'),  # up from its name to Houston Canyon
    ((3290, 1647), 'Houston Canyon'),  # on east from its name to Warming House Hill's circle
    ((3740, 1682), 'Warming House Hill'),  # from its circle to its name
    ((3485, 2135), 'Homeowners'),  # on down the boundary to the Gold Link base
    ((3115, 2403), 'Elko Park'),  # from its square down to the base
    ((3205, 2117), 'Cascade'),  # the branch east of the lift from its name
    # lines that run on from one name into the next run's: the first run's
    ((2698, 1470), 'Upper Smith Hill'),  # from its name to Lower Smith Hill's
    ((2704, 1199), 'Peanut'),  # from its circle to Lower Twister's
    ((2592, 989), 'Crystal'),  # from its name across Yellow Brick Road to Lower Crystal's
    ((1369, 1582), 'Daisy'),  # from its square to Middle Gallowich's
    ((3051, 1175), 'Lower International'),  # black: down from Aspen Park Road (green) to its name
    ((3169, 1187), 'Upper Championship'),  # its line on past its name to Middle Championship's
    ((3535, 1305), 'Middle Championship'),  # on from its name to Lower Championship's diamond (one run in three parts)
    ((1634, 645), 'Schofield Road'),  # on east past its diamond to the top of Paradise Bowl
    ((1538, 683), 'Schofield Road'),  # up to its diamond
    ((1958, 732), 'Upper Ruby Chief'),  # a tick by its square
    ((1355, 1658), 'Middle Gallowich'),  # a tick by its square
    ((1595, 1371), 'Lower Canaan'),  # on below its square
]
UNNAMED = [
    # gates in the boundary and closure fences (yellow bars)
    ((1559, 1929), 'a gate'), ((1332, 1913), 'a gate'), ((2371, 541), 'a gate'), ((2563, 695), 'a gate'),
    ((2751, 850), 'a gate'), ((2260, 475), 'a gate'), ((2257, 467), 'a gate'), ((2279, 485), 'a gate'), ((2068, 375), 'a gate'), ((2066, 368), 'a gate'), ((2065, 367), 'a gate'),
    ((2087, 385), 'a gate'), ((753, 772), 'a gate'), ((585, 1121), 'a gate'), ((584, 1125), 'a gate'),
    ((1023, 895), 'a gate'), ((1955, 291), 'a gate'), ((711, 856), 'a gate'),
    ((228, 1324), 'a tick of the closed area\'s fence'), ((3155, 1712), 'a tick by Grand Traverse\'s name'),
    # arrowheads on Gunsight Pass, Splain's Gulch and Little Lizzy
    ((2026, 1884), 'an arrowhead'), ((2054, 1866), 'an arrowhead'), ((2056, 1899), 'an arrowhead'),
    ((1884, 1897), 'an arrowhead'), ((1912, 1878), 'an arrowhead'), ((1915, 1912), 'an arrowhead'),
    ((2533, 1893), 'an arrowhead'), ((2522, 1878), 'an arrowhead'), ((2809, 1811), 'an arrowhead'), ((2808, 1828), 'an arrowhead'),
    ((2933, 1688), 'an arrowhead'), ((2901, 1679), 'an arrowhead'), ((2730, 1743), 'an arrowhead'),
    ((2748, 1748), 'an arrowhead'),
    # letters of the lifts' and the base area's names, and the charging icon at Paradise
    ((3193, 2167), 'a letter'), ((2986, 991), 'a letter'), ((3024, 1047), 'a letter'), ((4164, 1737), 'a letter'),
    ((3704, 1392), 'a letter'), ((3712, 1394), 'a letter'),
    ((1389, 1729), 'an icon'), ((1405, 1730), 'an icon'), ((1386, 1735), 'an icon'),
]
CUTS = []
TRACED = []
TRIMS = []
