"""Naming decisions for this panel. The pieces are names.py's own lines, each named by it (resort.GROUPED): nothing
is left to decide, so these stay empty unless a check shows a line to cut or a stretch to add.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = []
UNNAMED = []
CUTS = []
TRACED = []
TRIMS = []
