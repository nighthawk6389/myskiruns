"""Naming decisions for Solitude's map, settled on crops, keyed by points in map px (work/solitude/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = []
UNNAMED = []
CUTS = []
TRACED = []
TRIMS = [
    # Back Door's line runs on past the junction below its name, down Dynamite's line (its lower label): kept to the
    # junction (back-door cell, pieces draw 1840,240,2080,560)
    ((1940, 293), (1883, 332)),
]
