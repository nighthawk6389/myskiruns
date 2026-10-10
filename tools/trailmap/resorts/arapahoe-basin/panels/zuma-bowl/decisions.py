"""Naming decisions for Arapahoe Basin's zuma-bowl panel, settled on crops, keyed by points in map px
(work/arapahoe-basin/zuma-bowl/map.png), so they survive a re-extraction: pdf_resort.py finds the piece through each point.
`pdf_resort.py arapahoe-basin/zuma-bowl add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # crop 780,500-1400,1250: the blue line on from Gentling's foot (GENTLING printed along its line from its square),
    # NED'S CACHE printed beside it from its square, down to the Zuma lift base
    ((919, 916), "Ned's Cache"),
    # crop 250,480-900,1050: the black line on west along the ridge from ZUMA CORNICE's EX (the name printed on it from
    # Il Rifugio) to Elephant's Trunk's EX, where that run drops
    ((594, 633), 'Zuma Cornice'),
]
UNNAMED = [
    ((887, 1439), 'the Zuma hike back trail (uphill, ZUMA HIKE BACK TRAIL printed by it)'),
]
CUTS = []
# ELEPHANT'S TRUNK, printed on two lines down the fall line from its EX to its short line: the stretch along the name
TRACED = [("Elephant's Trunk", [(358, 735), (346, 800), (333, 878)])]
TRIMS = []
