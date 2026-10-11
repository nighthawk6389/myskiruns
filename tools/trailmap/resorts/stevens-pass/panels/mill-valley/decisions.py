"""Naming decisions settled on crops, keyed by points in map px (the panel's work/stevens-pass/<panel>/map.png), so
they survive a re-extraction.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # mb.png: from the square where Aquarius' dashed line meets Gemini's, the solid line down to Lower Aquarius' (and
    # Aquarius' name above the square only); the dashed line on down from that square to Outer Limits' name is Outer
    # Limits' (its name printed in a gap of it); Gemini's line runs on solid past its name down to where Lower
    # Aquarius' and Lower Gemini's start (cut there: CUTS); the black line past the diamond by Borealis' name (the
    # auto-match gave it Outer Limits'), and the one past Lower Voltage's diamond and name from Outer Limits' square
    ((963, 1290), 'LOWER AQUARIUS'),
    ((886, 1332), 'OUTER LIMITS'),
    ((981, 1685), 'BOREALIS'),
    ((910, 1787), 'LOWER VOLTAGE'),
    # ma.png: the black line from Corona Bowl's double diamond down; Aquarius Face's from its diamond up to South Divide
    ((689, 1066), 'CORONA BOWL'),
    ((1231, 742), 'AQUARIUS FACE'),
    ((918, 1326), 'GEMINI'),
    ((1175, 1526), 'LOWER AQUARIUS'),
]
UNNAMED = []
CUTS = [((918, 1326), (1011, 1367))]  # Gemini / Lower Aquarius, where the line from Aquarius' square joins
TRACED = []
