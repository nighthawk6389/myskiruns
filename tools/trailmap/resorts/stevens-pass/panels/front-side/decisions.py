"""Naming decisions settled on crops, keyed by points in map px (the panel's work/stevens-pass/<panel>/map.png), so
they survive a re-extraction.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # fd.png: Double Diamond's line runs on past Lower Diamond's diamond: cut there (CUTS), each part its run's
    ((593, 741), 'DOUBLE DIAMOND'),
    ((931, 1202), 'LOWER DIAMOND'),
    # fc.png: the black line past I-5's diamond and name, down to the base
    ((1060, 1337), 'I-5'),
    # fb.png, d1.png: the blue line through International's square and name; the black line beside Parachute 2's name
    # (the auto-match gave it Parachute 1's, whose own line is the one beside); Hog Heaven's stroke runs on as Hog
    # Wild's: cut at Hog Wild's square
    ((2445, 1041), 'INTERNATIONAL'),
    ((2264, 1196), 'PARACHUTE 2'),
    ((2552, 899), 'HOG HEAVEN'),
    ((2063, 1496), 'HOG WILD'),
    # z4.png: Broadway's dashed line ends at Midway's park and goes on solid under the Brooks lift; the solid line
    # through the parks' bands is Waterfall's (its name on it; Midway and the Mavericks are parks along it)
    ((2788, 1189), 'BROADWAY'),
    ((3123, 1021), 'BROADWAY'),  # its dashed line down to Midway's park, its name along it (the auto-match: Midway's)
    ((2583, 1363), 'WATERFALL'),
    # d3.png: Rock Garden's stroke runs on past its double diamond, from Little Tree's top, as Lower Rock Garden's
    # dashes (its name along them): cut there
    ((2679, 455), 'ROCK GARDEN'),
    ((2363, 679), 'LOWER ROCK GARDEN'),
    # fe.png: the black line along Solitude's name and past its double diamond (the auto-match gave it Nancy Chute's,
    # whose own line is the one beside)
    ((3132, 506), 'SOLITUDE'),
    # fb.png: the black line along Panorama's name past its diamond (not Skyline's: Skyline is blue)
    ((2505, 1223), 'PANORAMA'),
]
UNNAMED = [
    # z4.png: a dashed track from Broadway's foot at Midway west to Skyline, no name
    ((2890, 1110), 'a dashed track from Broadway at Midway to Skyline, with no name'),
    # fc.png: a green line through the learning terrain, no name
    ((1577, 1520), 'a green way through the learning terrain, with no name'),
]
CUTS = [
    ((593, 741), (828, 1107)),  # Double Diamond / Lower Diamond, at Lower Diamond's diamond
    ((2552, 899), (2440, 1203)),  # Hog Heaven / Hog Wild, at Hog Wild's square
    ((2679, 455), (2519, 557)),  # Rock Garden / Lower Rock Garden, where Little Tree leaves it
]
TRACED = []
