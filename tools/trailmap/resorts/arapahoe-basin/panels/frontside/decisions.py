"""Naming decisions for Arapahoe Basin's frontside panel, settled on crops, keyed by points in map px
(work/arapahoe-basin/frontside/map.png), so they survive a re-extraction: pdf_resort.py finds the piece through each point.
`pdf_resort.py arapahoe-basin/frontside add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # the Steep Gullies (crop 2700,1250-3800,2450): each gully's black line, its SG label printed beside it (no
    # symbol: the area's EX under THE STEEP GULLIES); SG 2's from the access gate past that EX
    ((2983, 1720), 'SG 1'), ((2965, 1333), 'SG 2'), ((3075, 1742), 'SG 2'), ((3191, 1752), 'SG 3'),
    ((3221, 1668), 'SG 4'), ((3315, 1684), 'SG 5'),
    ((1707, 2031), 'Ramrod'),  # its blue line on below the Aerial Adventure Park's outline (crop 1580,1880-1880,2150)
]
UNNAMED = [
    ((1259, 288), "the Via Ferrata's outline (a summer guided experience)"),
    ((1682, 2017), "the Aerial Adventure Park's outline (a summer experience)"),
    # the hiking routes (thin black lines with arrowheads and hiker icons: the legend's HIKING ROUTE) up the East Wall
    # to North Pole, Snorkel Nose, Willy's Wide and the Tree Chutes, and by Bald Spot
    ((576, 987), 'the hiking route up to the Tree Chutes'), ((1099, 445), "the hiking route up to Willy's Wide"),
    ((1720, 345), 'the hiking route along the ridge from the North Pole hiking gate'),
    ((3594, 1563), 'the hiking route below Bald Spot'),
    # the Steep Gullies hike back (the legend's HIKE BACK TRAIL, uphill from Rendezvous Point to the Pallavicini base)
    ((3113, 2352), 'the Steep Gullies hike back trail (uphill)'), ((2466, 2193), 'the Steep Gullies hike back trail (uphill)'),
    # crop 2330,620-2750,1000: the blue line with arrows from the Pallavicini lift top up to the foot of West Wall and
    # the start of Davis, no name printed
    ((2468, 876), 'a link from the Pallavicini lift top to West Wall and Davis: no name printed'),
]
CUTS = []
TRACED = []
TRIMS = []
