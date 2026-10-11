"""Naming decisions settled on crops, keyed by points in map px (the panel's work/sun-valley/<panel>/map.png), so
they survive a re-extraction.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # dpair3.png: Elkhorn Bowl's line from the Elkhorn lift's top round the bowl's rim and down; Arrowhead Way's from the
    # lift's top down to Joint Venture's circle, where Joint Venture's runs on down beside the lift (one stroke: cut)
    ((1300, 485), 'Elkhorn Bowl'),
    ((1977, 346), 'Arrowhead Way'),
    ((1435, 658), 'Joint Venture'),
    # dpair4.png: the green line from the Dollar lift's top west to Forbidden Fruit's, and its line on below its name
    ((2902, 365), 'Forbidden Fruit'),
    ((2185, 1013), 'Forbidden Fruit'),
    # dpair2.png: the green line from the Half Dollar lift's top west to Cabin Practice's circle; the line from Sluice
    # Box's name (a park) to Poverty Flats' circle
    ((3861, 992), 'Cabin Practice'),
    ((2983, 1204), 'Poverty Flats'),
]
UNNAMED = [
    # dpair3.png: a short line under the Elkhorn lift's top this season's print doesn't draw
    ((1849, 300), "a 2023 line this season's print doesn't draw"),
    # dpair2.png: Graduation's line (2023): this season's print draws none there, the Name Dropper park's name instead
    ((4149, 1046), "Graduation's 2023 line: gone from this season's print"),
    ((4143, 1384), "Graduation's 2023 line: gone from this season's print"),
]
CUTS = [((1977, 346), (1721, 487))]  # Arrowhead Way / Joint Venture, at Joint Venture's circle
# lines this season's print draws that the 2023 export doesn't (g_old.png, g_sepp.png): Old Bowl's blue line from the
# Dollar lift's top round and down past its square; Sepp's green dotted line past its circle down to Sluice Box
TRACED = [
    ('Old Bowl', [(3480, 412), (3550, 404), (3620, 410), (3680, 428), (3700, 460), (3693, 500), (3670, 540),
                  (3652, 575), (3645, 610), (3645, 640), (3655, 700), (3668, 760), (3678, 800), (3688, 850),
                  (3693, 900), (3690, 950), (3680, 1000)]),
    ("Sepp's Bowl", [(2805, 375), (2780, 420), (2760, 460), (2745, 505), (2740, 560), (2737, 620), (2730, 660),
                     (2705, 690), (2670, 712), (2645, 740), (2628, 785), (2632, 830), (2650, 862), (2668, 895),
                     (2687, 940), (2707, 990), (2732, 1040), (2762, 1088), (2795, 1125)]),
]
