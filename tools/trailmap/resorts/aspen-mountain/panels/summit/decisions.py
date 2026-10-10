"""Naming decisions for this panel, settled on crops, keyed by points in map px (work/aspen-mountain/summit/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # (work/aspen-mountain/summit/crops/) a line carrying two runs, each stretch named by the name printed on it, cut
    # at the junction between them (or between the names where none is)
    ((420, 399), "Walsh's"), ((105, 614), "Lower Walsh's"),
    ((405, 492), 'Kristi'), ((140, 643), 'Lower Kristi'),
    # MIDNIGHT from the top to Dipsy Doodle's line, Dipsy Doodle's on to the Ajax Express's foot, SPAR GULCH below
    ((1377, 495), 'Midnight'), ((1484, 932), 'Dipsy Doodle'), ((1645, 1290), 'Spar Gulch'),
    # 1 & 2 LEAF (printed on both its lines) from the top to where its other line joins, SILVER DIP below
    ((1017, 675), 'Silver Dip'), ((705, 351), '1 & 2 Leaf'),
    ((526, 633), 'North Star'), ((331, 1172), "Gent's Ridge"),
    ((524, 1058), 'Copper'), ((640, 1288), 'Copper Bowl'),
    # the line beside PUMP HOUSE HILL; the second line under SUNRISE/SUNSET (two runs, two lines); the cased line down
    # beside the gondola (the main map's Ridge of Bell); the line along the boundary that Rideout leaves (Buddy System)
    ((1565, 661), 'Pump House Hill'), ((1397, 984), 'Sunrise/Sunset'), ((1063, 1335), 'Ridge of Bell'),
    ((129, 388), 'Buddy System'),
]
UNNAMED = [
    ((775, 127), "the traverse from the gondola's top to the Hero's lift's: no name printed"),
]
CUTS = [
    ((420, 399), (214, 542)), ((405, 492), (242, 594)), ((1377, 495), (1437, 656)), ((1484, 932), (1627, 1166)),
    ((1017, 675), (889, 520)), ((526, 633), (263, 881)), ((524, 1058), (575, 1175)),
]
TRACED = []
TRIMS = []
