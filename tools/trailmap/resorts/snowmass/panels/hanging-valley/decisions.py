"""Naming decisions for the Hanging Valley inset, settled on crops, keyed by points in map px
(work/snowmass/hanging-valley/map.png), so they survive a re-extraction: pdf_resort.py finds the piece through each
point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # sm/hv2, sm/hv3 crops: one cased line runs from High Alpine west along the boundary, then down past UPPER LADDER
    # and LOWER LADDER (see CUTS): the boundary traverse is the report's High Pass (Lower BD) (Hanging Valley's,
    # expert: the cased traverse along the boundary below High Pass), the upper ladder and the lower are the two
    # names printed on it; the upper of the two lines along the ridge to High Alpine is the same traverse
    ((700, 177), 'High Pass (Lower BD)'),
    ((939, 132), 'High Pass (Lower BD)'),
    ((343, 340), 'Upper Ladder'),
    ((200, 469), 'Lower Ladder'),
    # the cased line from the Hanging Valley Glades junction down past WEIRD WOODS, its double diamond, then on past
    # GLADE TWO: Weird Woods above the glades' junction, Glade Two below (see CUTS)
    ((694, 427), 'Weird Woods'),
    ((596, 475), 'Glade Two'),
    # the line from below HANGING VALLEY GLADES to the Weird Woods junction: the glades' own
    ((899, 330), 'Hanging Valley Glades'),
    # from the Weird Woods / Glade Two junction down to GLADE THREE's line: its upper part (the stroke and the
    # casing, drawn both)
    ((632, 486), 'Glade Three'),
    ((635, 484), 'Glade Three'),
]
UNNAMED = [
    # sm/hv2/crop_80_140.png: a cased line between Valley Valley's and Wall One's with a double diamond, no name printed
    # on it (the main map's lines differ here)
    ((331, 402), 'a run between Valley Valley and Wall One that no name is printed on'),
    # the traverse along the foot of the runs, with its double diamond, and its exit down to Sandy Park: no names
    ((325, 572), 'the traverse along the foot of Hanging Valley: no name printed'),
    ((249, 603), "the exit from the foot of Hanging Valley down to Sandy Park: no name printed"),
]
CUTS = [
    ((700, 177), (431, 265)),  # the boundary traverse / Upper Ladder, where the line turns down
    ((343, 340), (261, 394)),  # Upper Ladder / Lower Ladder, between their names
    ((694, 427), (641, 448)),  # Weird Woods / Glade Two, where Glade One joins
]
TRACED = []
