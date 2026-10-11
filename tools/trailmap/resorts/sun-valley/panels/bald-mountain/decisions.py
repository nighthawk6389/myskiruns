"""Naming decisions settled on crops, keyed by points in map px (the panel's work/sun-valley/<panel>/map.png), so
they survive a re-extraction.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # b1.png: the black arrows from the Flying Squirrel lift's top to Machine Rd's diamond, its line's upper half; the
    # blue line into Graduate's square from above
    ((2363, 555), 'Machine RD'),
    ((2283, 623), 'Graduate'),
    # b5.png: Mid Limelight's line on past Pete's Lane (the print draws it black)
    ((2507, 535), 'Mid Limelight'),
    # b2.png: the green line from Christmas Lane's end past Roundhouse Slope's circle
    ((1707, 678), 'Roundhouse Slope'),
    # b3.png: Aujus' line above its name; b4.png: the green line through Olympic Ridge's circle
    ((2363, 959), 'Aujus'),
    ((1563, 1097), 'Olympic Ridge'),
    # pmaiden.png: the way down's green dots under Maiden Lane's name, through its circle, from the blue dots' end to
    # Lower Warm Springs' dots
    ((2650, 695), 'Maiden Lane'),
    # p42.png: Lower College's line on west of Sunset Strip's circle (cut there below), under 42nd Street's name
    ((2061, 955), 'Sunset Strip'),
]
UNNAMED = [
    # b1.png: a dash between the Flying Squirrel lift's top and Upper Picabo's Street's diamond
    ((2281, 497), "a dash at the Flying Squirrel lift's top"),
]
CUTS = [
    # p42.png: Lower College's line turns west into Sunset Strip at its circle
    ((2150, 995), (2105, 987)),
]
TRACED = []
