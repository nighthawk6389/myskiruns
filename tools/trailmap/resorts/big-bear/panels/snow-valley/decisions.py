"""Naming decisions for this panel, settled on crops, keyed by points in map px (work/big-bear/<panel>/map.png).

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = []
UNNAMED = [
    # bg.png: the interactive map's Bubble Gum goes on down from its square along what the 2025-26 print draws as the
    # cat track's red dashes (the Cat Track's own line, names.py): no part of Bubble Gum here
    ((916, 1090), "the cat track's dashes, the older interactive map's Bubble Gum"),
]
CUTS = []
TRACED = []
