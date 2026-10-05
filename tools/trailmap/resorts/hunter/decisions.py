"""Hunter Mountain's naming decisions, settled on zoomed crops (grid_crop.py over work/hunter/map.png with the
pieces tagged id:name; the crop names in the comments are that session's scratch files). Every decision is a
POINT in map px (work/hunter/map.png, 4830x2485), so it survives a re-extraction: pdf_resort.py finds the piece
through it. `pdf_resort.py hunter add` records new ones.

CHECKED  [((x, y), NAME)]   the piece through the point is that trail (overrides the auto-match)
UNNAMED  [((x, y), why)]    the piece is not a trail
CUTS     [((x, y) on the piece, (x, y) to cut at)]  one drawn line carries two trails; the second part becomes a
                            new piece (appended, so the other ids stay put)
TRACED   [(NAME, [(x, y), ...])]  a stretch with no drawn line of its own
"""
CHECKED = [
    # close/parkave.png: the black line below the two-line PARK AVENUE / WEST label continues Park Avenue West (its stub runs into the diamond above the label)
    ((1594, 2098), 'PARK AVENUE WEST'),
    # close/crop_2700_780: the blue line beside the BELT PARKWAY BYPASS label and square, from the top down to Belt Parkway
    ((2943, 905), 'BELT PARKWAY BYPASS'),
]
UNNAMED = [
]
CUTS = []
TRACED = []
