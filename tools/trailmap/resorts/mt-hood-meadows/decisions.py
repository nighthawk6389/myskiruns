"""Naming decisions settled on crops, keyed by points in map px (work/mt-hood-meadows/map.png), so they survive a
re-extraction: pdf_resort.py finds the piece through each point. `pdf_resort.py mt-hood-meadows add` records new
ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # q95.png: the blue line through Forest Park's orange band (its S/M/L sign on it), from Tamarack's name down to
    # Forest Park's
    ((1571, 1989), 'FOREST PARK'),
    # q120.png: a black stub above 1 Bowl's name and diamond, the bowl's only line
    ((1622, 1146), '1 BOWL'),
    # qgul.png: one stroke from Boulevard's line past Gulch's square and name, on down to Gingivitis' square (where
    # Gingivitis starts, its name below it): Gulch's
    ((1451, 1029), 'GULCH'),
    # q124.png: the green line from Mitchell Creek's into South Canyon's, above its name
    ((990, 1391), 'SOUTH CANYON'),
    # q134.png: Discovery Ridge's line forks at its foot: the lower branch; Outer Limits' line forks above the
    # Shooting Star lift's top: the branch down to it
    ((1868, 1291), 'DISCOVERY RIDGE'),
    ((2059, 1109), 'OUTER LIMITS'),
    # q137.png: the black lines below Accordion Bowl's name and Hinterlands', which meet and run on down the canyon to
    # Heather Canyon Runout's name
    ((2697, 1471), 'ACCORDION BOWL'),
    ((2637, 1510), 'HINTERLANDS'),
    ((2772, 1899), 'HEATHER CANYON RUNOUT'),
]
UNNAMED = [
    # q0b.png: a black line from the trees below Elk Bowl into Heather Canyon Runout's bend, no name or symbol on it
    ((2251, 2303), 'a way out of the trees below Elk Bowl into Heather Canyon Runout, with no name'),
]
CUTS = [
    # q137.png: Hinterlands' line, then (below where Accordion Bowl's joins it) the canyon's way down to the runout
    ((2637, 1510), (2680, 1556)),
]
TRACED = []
