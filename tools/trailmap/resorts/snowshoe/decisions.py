"""Naming decisions for Snowshoe's map, settled on crops, keyed by points in map px (work/snowshoe/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # the blue line from Little Spruce's square down to Fox Chase's (the interactive map's Fox Chase; the print's two
    # squares start two runs: Little Spruce above, Fox Chase from its square on; fix crops g_ls, pair_b)
    ((2112, 536), 'Little Spruce'),
]
UNNAMED = [
    ((1370, 286), "the interactive map's stub at the end of Gangway's name: no line on the print there (Gangway's "
                  "line loops from its circle down to Camp 4)"),
]
CUTS = []
TRACED = [
    # Cant Hook: its green line's top, its circle and its name printed up along the purple dashes to Knife Blade's
    # line (the interactive map's line is only the bit below the circle; g_cant crop)
    ('Cant Hook', [(1822, 551), (1833, 540), (1850, 527), (1870, 512), (1888, 499), (1904, 488)]),
    # Upper Whistlepunk, printed on two lines: from its circle down along WHISTLEPUNK to its line's stub at Heisler
    # Way (g_upw crop)
    ('Upper Whistlepunk', [(1104, 238), (1120, 246), (1140, 256), (1160, 268), (1175, 282), (1186, 300)]),
]
TRIMS = []
