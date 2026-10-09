"""Naming decisions for this panel, settled on crops, keyed by points in map px (work/mammoth/<panel>/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch along the run where no piece runs
"""
CHECKED = []
UNNAMED = []
CUTS = []
TRACED = []
