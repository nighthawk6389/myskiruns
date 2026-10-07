"""Naming decisions for the alpine-back panel, settled on crops, keyed by points in map px
(work/palisades-tahoe/alpine-back/map.png), so they survive a re-extraction: pdf_resort.py finds the piece through
each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # pt/ab1-ab3.png, pt/abB.png, pt/abD.png (PDF strokes in drawing order, seq.py): Ray's Rut's, Leisure Lane's, Return Road's, Winter Road's, Sherwood Run's, Maid Marian's, Robin Hood's, Reily's Run's, Scott Meadow's, Twilight Zone's and Nottingham's Notch's lines through their symbols (Sherwood Run's is one stroke from the Sherwood top along the ridge and round to the base; Robin Hood's goes on below where Maid Marian's joins it, one stroke); Sherwood Face's, Mountain View's and Standard Run's lines on below their names; Shooting Star's beside its symbol, from the end of Outer Limits' name down to the Lakeview chair
    ((2717, 886), 'Ray’s Rut'),
    ((3531, 331), 'Leisure Lane'),
    ((2755, 484), 'Return Road'),
    ((3493, 406), 'Winter Road'),
    ((2021, 848), 'Sherwood Run'),
    ((2368, 400), 'Maid Marian'),
    ((2381, 595), 'Robin Hood'),
    ((3053, 662), 'Reily’s Run'),
    ((3337, 560), 'Scott Meadow'),
    ((3800, 405), 'Twilight Zone'),
    ((2531, 492), 'Nottingham’s Notch'),
    ((2269, 674), 'Sherwood Face'),
    ((3536, 455), 'Mountain View'),
    ((3328, 491), 'Standard Run'),
    ((3426, 669), 'Shooting Star'),
]
UNNAMED = [
    # pt/ab1.png, pt/abB.png: drawn with Nottingham's Notch's line, but its name and symbol are on the other one
    ((2420, 413), "a link from Sherwood Run's line along the ridge down to Maid Marian's"),
]
CUTS = [
]
TRACED = [
]
