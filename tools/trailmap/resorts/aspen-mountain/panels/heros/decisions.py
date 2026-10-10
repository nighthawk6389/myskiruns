"""Naming decisions for this panel, settled on crops, keyed by points in map px (work/aspen-mountain/heros/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # (work/aspen-mountain/heros/crops/) the line from the Sundeck down beside the gondola (the summit inset's EASY
    # CHAIR); the line from the Sundeck down to 1 & 2 LEAF's pill
    ((1368, 320), 'Easy Chair'), ((1190, 309), '1 & 2 Leaf'),
]
UNNAMED = [
    ((1146, 243), "the traverse from the Sundeck to the Hero's lift's top: no name printed"),
]
CUTS = []
TRACED = []
TRIMS = []
