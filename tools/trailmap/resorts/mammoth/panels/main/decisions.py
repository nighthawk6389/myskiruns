"""Naming decisions for this panel, settled on crops, keyed by points in map px (work/mammoth/<panel>/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch along the run where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on too far: cut it nearest the second and drop
         the part beyond
"""
CHECKED = [
    # mm/f1/crop_780_1000.png: the interactive map ends Back for More (Upper) in the middle of its second UPPER BACK FOR
    # MORE label; the label, with its blue diamond at its lower end, is printed on Upper's stretch (see CUTS)
    ((931, 1112), 'Back for More (Upper)'),
    # mm/f2/crop_2380_300.png: the interactive map's Skyline runs on from the ridge down the face along both SCOTTY'S
    # labels to St. Anton: that descent is Scotty's (the back-side inset draws Skyline ending on the ridge and
    # Scotty's going down; this panel's interactive map has no Scotty's line) (see CUTS)
    ((2578, 569), "Scotty's"),
]
UNNAMED = []
CUTS = [
    ((931, 1112), (882, 1134)),  # Back for More: Upper down to its label's diamond, Lower below
    ((2578, 560), (2565, 452)),  # Skyline on the ridge, Scotty's from its first label down
]
TRACED = []
TRIMS = [
    # mm/mt_plain.png: the printed dotted traverse ends by Dry Creek's diamond; the interactive map's Main Traverse
    # runs on through the closed area's hatching and the CHINA BOWL label to the gondola
    ((1809, 613), (1879, 643)),
]
