"""Naming decisions for the Top of Gondola panel, settled on crops, keyed by points in map px
(work/heavenly/top-of-gondola/map.png), so they survive a re-extraction: pdf_resort.py finds the piece through each
point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on under another line: cut it nearest the
         second and drop the part beyond
"""
CHECKED = [
    # hv/reg/inset_top.png, hv/reg/main_tam.png: Von Schmidt's line across the top of the inset, from the west into
    # its square and on east past its label (direction arrows on it) to the panel's edge, as on the main map, where
    # it runs on to California Trail's square
    ((159, 157), 'Von Schmidt'),
    ((1609, 53), 'Von Schmidt'),
    ((2104, 94), 'Von Schmidt'),
]
UNNAMED = [
    # hv/inset/crop_1150_0.png
    ((2044, 116), 'the way from Tamarack Lodge to the California side, labelled TO CALIFORNIA (no run name)'),
    ((1818, 358), 'the arrow from Tamarack Lodge up to the TO CALIFORNIA way'),
    # hv/inset/crop_0_0.png
    ((88, 274), 'an arrow pointing to the Nevada side, labelled TO NEVADA (no run name)'),
]
CUTS = []
TRACED = []
TRIMS = []
