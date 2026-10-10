"""Naming decisions for this panel, settled on crops, keyed by points in map px (work/big-bear/snow-summit/map.png).

The crops: zoomed grid crops of the print with the pieces and the interactive map's symbols drawn on (grid_crop.py
--pieces --names --symbols), and the interactive map's lines over the print (its groups name each run's line, drawn
up to 40 px off the print's).

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # audit: Miracle Mile's lower line above Lower's first square (where Upper's line ends after the gap under its diamond) is Upper's
    ((1062, 1046), 'Miracle Mile (Upper)'),
    # the west side (crops c1.png, c7down.png, cc/crop_50_780.png, cc/crop_50_1200.png): Timber Ridge's blue line
    # in two parts either side of its upper label (the interactive map's Upper and Lower: one line, one square, the
    # name printed twice); 7 Down's line is the green one from its upper label to its lower one (its squares blue);
    # Perfect Pitches' blue line from the top square past its three squares, and its foot below its lower label;
    # Pipe Dream's under its label; Jo's from its label to lift 10's foot; Log Chute (Upper)'s end below its second
    # square (Lower's diamond is just below it)
    ((569, 524), 'Timber Ridge'),
    ((233, 978), 'Timber Ridge'),
    ((341, 896), '7 Down'),
    ((372, 1062), 'Perfect Pitches'),
    ((243, 1557), 'Perfect Pitches'),
    ((390, 1368), 'Pipe Dream'),
    ((412, 1476), "Jo's"),
    ((516, 782), 'Log Chute (Upper)'),
    # the chutes (cc/crop_480_850.png): Tommi's line below its label (the interactive map's), Log Chute (Lower)'s
    # the long one beside it
    ((549, 1303), "Tommi's"),
    # the middle (cc/crop_750_330.png, cc/crop_850_800.png, cc4): Dicky's line below its label; Miracle Mile (Lower)
    # from its first square down; Summit Run (Upper)'s line round east past its third circle and back to the
    # junction where Summit Run (Lower) and Summit Connection start; Summit Run (Lower) down to the base
    ((883, 726), "Dicky's"),
    ((989, 1265), 'Miracle Mile (Lower)'),
    ((1352, 893), 'Summit Run (Upper)'),
    ((1072, 1161), 'Summit Run (Lower)'),
    ((1142, 1499), 'Summit Run (Lower)'),
    ((1371, 703), 'Ego Trip'),
    # the east side (cc/crop_1250_300.png, cc2, cc3, cc5): Westridge Park's line from the summit (below East Why's
    # first square, where East Why's own line leaves it) round to the Westridge Park label and on down to the
    # Summit lift's foot; ZZYZX Park's under its label; Mainstream's below its label; Cruiser's from its circle under
    # its label and on to lift 9's foot; Skyline Creek's two parts; Sundown's; Last Chance's lower part
    ((1599, 512), 'Westridge Park'),
    ((1809, 1075), 'Westridge Park'),
    ((1662, 754), 'ZZYZX Park'),
    ((2036, 769), 'Mainstream'),
    ((1916, 540), 'Cruiser'),
    ((2047, 717), 'Cruiser'),
    ((2099, 825), 'Cruiser'),
    ((2219, 614), 'Skyline Creek'),
    ((2311, 843), 'Skyline Creek'),
    ((2234, 817), 'Sundown'),
    ((2151, 914), 'Last Chance'),
]
UNNAMED = [
    # the black mask's leftovers (cc/crop_480_850.png, pieces_view_c.png): a column of trees in the strip east of
    # Side Chute, one beside Tommi's label, and the lift 6 hut's icon
    ((710, 1006), "trees: a dark streak in the strip east of Side Chute's label"),
    ((551, 1064), "trees beside Tommi's label"),
    ((813, 686), "lift 6's hut icon"),
    ((807, 686), "lift 6's hut icon"),
]
CUTS = [
    # the line from East Why's first square: East Why's own line leaves it at its second square, Westridge Park
    # goes on east (cc5/crop_1300_290.png)
    ((1552, 492), (1505, 462)),
    # Miracle Mile's lower line: Upper's to Lower's first square, Lower's from it
    ((989, 1265), (1022, 1128)),
]
TRACED = [
    # Off Chute's foot: the short black line at its label's end, under the mask's 60 px (c1.png)
    ('Off Chute', [(712, 796), (728, 801), (745, 808), (754, 814)]),
]
