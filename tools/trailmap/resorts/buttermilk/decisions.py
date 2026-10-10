"""Naming decisions for this panel, settled on crops, keyed by points in map px (work/buttermilk/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # Tiehack: the three lines through TIMBER DOODLE GLADE (a black box, the glade's name) from Klaus' Way down to
    # the lift: the glade's; the line through PTARMIGAN GLADE, from the boundary down to Sterner's: that glade's
    ((1349, 935), 'Timberdoodle Glade'),
    ((1323, 866), 'Timberdoodle Glade'),
    ((1298, 835), 'Timberdoodle Glade'),
    ((1497, 742), 'Ptarmigan Glade'),
    # one line runs from the West Summit along the boundary past KLAUS' WAY, then turns down past RACER'S EDGE (see
    # CUTS)
    ((1263, 764), "Klaus' Way"),
    ((741, 1155), "Racer's Edge"),
    # Buckskin's line runs on at its foot round the loop past RABBIT RUN (see CUTS)
    ((1168, 1201), 'Buckskin'),
    ((888, 1385), 'Rabbit Run'),
    # Main: the black line from the top through UNCLE CHUCK'S GLADES (a black box) down to Jacob's Ladder
    ((2003, 845), 'Uncle Chucks Glades'),
    ((1971, 953), 'Uncle Chucks Glades'),
    # the line from Lover's Lane's foot under MIDWAY AVENUE down to Homestead Road
    ((1889, 1023), 'Midway Avenue'),
    # Savio's line from the summit runs on east to Lover's Lane's top (see CUTS)
    ((1729, 744), 'Savio (Upper)'),
    # the green dots under the green BEAR pill, from Homestead Road down to the base: Bear's lower part
    ((1785, 1344), 'Bear'),
    ((1752, 1226), 'Bear'),
    # the black line from Homestead Road past SPRUCE turns at its foot and runs down the SUPERPIPE (see CUTS; Spruce
    # Face leaves it at the turn)
    ((2132, 1538), 'Spruce (Upper)'),
    ((1931, 1900), 'Super Pipe'),
    # West Buttermilk: the green line from the West Summit past BLUE GROUSE runs on past WESTWARD HO (see CUTS)
    ((2100, 709), 'Blue Grouse'),
    ((2392, 788), 'Westward Ho'),
    # Red's Rover's line (along the park's dots under the boundary, from the West Summit down to the lift) runs on
    # down to the foot of West Buttermilk and along it to the base (see CUTS)
    ((2508, 698), "Red's Rover"),
]
UNNAMED = [
    ((706, 1407), "from Buckskin's foot down below the Tiehack park to Oregon Trail: no name printed"),
    ((1910, 1029), "from the Jacob's Ladder junction down to Homestead Road: no name printed"),
    ((2601, 859), "from Westward Ho's foot under the lift to Camp Bird: no name printed"),
    ((1685, 847), "from Savio's foot across to Buckskin: no name printed"),
    ((1560, 705), "the traverse from the East Summit round the lift to Ptarmigan's and Buckskin's tops: no name "
                  "printed"),
    ((1812, 761), "a blue cut-across from Ridge Trail's top down to Lover's Lane's: no name printed"),
    ((2700, 922), "the green run-out along the foot of West Buttermilk to its base, where its green runs end: no name "
                  "printed"),
]
CUTS = [
    ((1263, 764), (891, 980)),  # Klaus' Way / Racer's Edge, where the line turns down
    ((1168, 1201), (846, 1303)),  # Buckskin / Rabbit Run, at Buckskin's foot
    ((2132, 1538), (2079, 1707)),  # Spruce (Upper) / Super Pipe, where Spruce Face leaves
    ((2100, 709), (2250, 756)),  # Blue Grouse / Westward Ho, between their names
    ((1729, 744), (1747, 805)),  # Savio's foot / the cut-across to Buckskin, at Lover's Lane's top
    ((1729, 744), (1673, 726)),  # Savio's foot / the summit traverse, at Savio's line
    ((2508, 698), (2535, 809)),  # Red's Rover / the run-out, at the lift
]
TRACED = []
TRIMS = []
