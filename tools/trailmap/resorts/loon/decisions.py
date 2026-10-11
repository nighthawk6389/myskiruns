"""Naming decisions settled on crops, keyed by points in map px (work/loon/map.png), so they survive a re-extraction:
pdf_resort.py finds the piece through each point. `pdf_resort.py loon add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = []
UNNAMED = []
CUTS = []
TRACED = []
