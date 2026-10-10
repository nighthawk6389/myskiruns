"""Naming decisions for this panel, settled on crops, keyed by points in map px (work/big-bear/<panel>/map.png).

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = []
UNNAMED = []
CUTS = []
TRACED = [
    # Easy Street (audit sheet 1, tiles/crop_300_850.png): one green run printed three times, from its circle below
    # the summit down the west side round to the base: along its painted slope through its three labels (the
    # labels' stretches alone, joined, would cut across the trees)
    ('Easy Street', [(567, 999), (520, 1020), (482, 1040), (470, 1080), (475, 1120), (520, 1180), (580, 1215),
                     (621, 1231), (700, 1245), (770, 1265), (850, 1295), (930, 1340), (1013, 1385), (1065, 1412),
                     (1115, 1440)]),
    # Outlaw's Alley (tiles2/crop_2130_650.png): along its curved label, its square printed in the middle of it
    ("Outlaw's Alley", [(2228, 690), (2255, 700), (2285, 718), (2305, 738), (2318, 758)]),
]
