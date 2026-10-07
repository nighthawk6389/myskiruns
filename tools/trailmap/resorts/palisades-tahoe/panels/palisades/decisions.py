"""Naming decisions for the palisades panel, settled on crops, keyed by points in map px
(work/palisades-tahoe/palisades/map.png), so they survive a re-extraction: pdf_resort.py finds the piece through
each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # pt/burk.png: the line from the Gold Coast junction round the oval's right end and along its bottom edge carries Burkhart's square (its name is printed inside the oval above it), to the top of Spring Bowl's name; one stroke
    ((2804, 850), 'Burkhart’s'),
    # pt/bg2.png: the line from the ridge past Main Backside's diamond (printed on it) down to Bottleneck Gully's diamond; Bottleneck Gully's own line is below its name (OpenStreetMap's Main Backside runs from the ridge to the bottom)
    ((4362, 361), 'Main Backside'),
    # pt/u1-u4.png, pt/saddle.png, pt/lll.png, pt/yt.png, pt/j98.png, osm_b_*.png (PDF strokes in drawing order, seq.py; OpenStreetMap's runs, osmcheck.py): Monument Ridge's line from its name past Mainline Pocket to the Emigrant Face line; Spring Bowl's link from Mountain Run's line to its symbol; Saddle Face's short line above its name; Women's Downhill's line from the KT-22 top to Champs Elysees; Schimmelpfennig Bowl's line below its name; Upper Dog Leg's from its name down; Poulsen's Gully's lines above and below its name; Nose's line from the KT-22 top past its symbol; Attic's above its name; Bottleneck Gully's below its name; Monkey Flower's from The Mora's line down to its own; Start Me Up's beside its name; Lower Yellow's link at the Gold Coast lodge; Jagged Edge's line past its symbol down to Mountain Run (Bullet's line ends just above it); the Lost Lake Loop (its arrows and symbol; Mountain Run's line runs under its MOUNTAIN RUN label beside it); Yellow Trail's line past its symbol beside its name (Newport's joins it lower down)
    ((3719, 300), 'Monument Ridge'),
    ((2504, 1079), 'Spring Bowl'),
    ((2262, 857), 'Saddle Face'),
    ((1518, 886), 'Women’s Downhill'),
    ((1982, 1437), 'Schimmelpfennig Bowl'),
    ((995, 1284), 'Upper Dog Leg'),
    ((891, 1823), 'Poulsen’s Gully'),
    ((602, 1246), 'Poulsen’s Gully'),
    ((1887, 1069), 'Nose'),
    ((4199, 302), 'Attic'),
    ((4574, 662), 'Bottleneck Gully'),
    ((3850, 474), 'Monkey Flower'),
    ((1394, 2098), 'Start Me Up'),
    ((2803, 777), 'Lower Yellow'),
    ((2442, 818), 'Jagged Edge'),
    ((2563, 764), 'Lost Lake Loop'),
    ((2879, 659), 'Yellow Trail'),
]
UNNAMED = [
    # pt/ba.png
    ((3268, 848), "a 2 pt stub of black line at the corner of Broken Arrow's diamond; the run has no line (its name and diamond only)"),
    # pt/j98.png, pt/gates.png: the green link from the foot of Gold Coast, Gold Coast Face, Mystery and Emigrant Gully down to Ramp Run's line (drawn on from their meeting point, apart from every run's strokes); the black dashed traverse along the High Camp gates
    ((3309, 556), "a green link from where Gold Coast, Gold Coast Face, Mystery and Emigrant Gully end, down to Ramp Run's line, with no name"),
    ((4127, 701), 'the black dashed traverse along the High Camp gates (Gate 1 to Gate 7), with no name of its own'),
]
CUTS = [
    # pt/hr2.png: one stroke from the end of MOUNTAIN RUN's label down to a fork and on down-left into HOME RUN's
    # label; Mountain Run's own line goes on straight down from the fork (OpenStreetMap's Home Run leaves Mountain
    # Run there): cut at the fork
    ((2477, 1125), (2467, 1153)),
]
TRACED = [
    # pt/aud2/palisades/001_*.jpg: Bottleneck Gully's line runs from its diamond (where Main Backside's ends) down
    # under its name, printed on two lines in a gap of it, to the short line below
    ('Bottleneck Gully', [(4544, 523), (4561, 546), (4562, 570), (4566, 600), (4570, 635)]),
]
