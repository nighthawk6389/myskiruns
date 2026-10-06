"""Naming decisions settled on crops, keyed by points in map px (work/whistler-blackcomb/glacier/map.png), so they
survive a re-extraction: pdf_resort.py finds the piece through each point. `pdf_resort.py whistler-blackcomb/glacier
add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # gl_all.png: Glacier Road leaves the glacier's foot at its label
    ((832, 973), 'GLACIER ROAD'),
    # gl_all.png, gl_bowls.png, gl_tr.png: the glacier's line beside its name; each bowl's fall lines below or into its label; the line down to the ladder
    ((367, 547), 'BLACKCOMB GLACIER'),
    ((663, 673), 'SAPPHIRE BOWL'),
    ((781, 588), 'GARNET BOWL'),
    ((833, 576), 'DIAMOND BOWL'),
    ((696, 712), 'DIAMOND BOWL'),
    ((700, 809), 'DIAMOND BOWL'),
    ((866, 565), 'RUBY BOWL'),
    ((940, 525), 'RUBY BOWL'),
    ((907, 731), 'RUBY BOWL'),
    ((988, 368), 'SPANKY’S LADDER'),
]
UNNAMED = [
    # gl_all.png, gl_tr.png
    ((559, 287), 'the arrow pointing at Blow Hole'),
    ((1012, 333), 'the line from the Horstman Hut toward the Glacier Express, with no name on this inset'),
]
CUTS = [
]
TRACED = [
]
