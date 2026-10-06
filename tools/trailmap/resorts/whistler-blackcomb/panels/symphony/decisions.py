"""Naming decisions settled on crops, keyed by points in map px (work/whistler-blackcomb/symphony/map.png), so they
survive a re-extraction: pdf_resort.py finds the piece through each point. `pdf_resort.py whistler-blackcomb/symphony
add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # sy_bottom.png, sy_top.png, sy_glades.png: the fan of lines below Jeff's Ode to Joy's second label, Crescendo printed on its line, The Glades' line leaving Harmony Ridge's end into its symbol
    ((1092, 870), 'JEFF’S ODE TO JOY'),
    ((1128, 874), 'JEFF’S ODE TO JOY'),
    ((1157, 895), 'JEFF’S ODE TO JOY'),
    ((1107, 365), 'CRESCENDO'),
    ((1435, 667), 'THE GLADES'),
    # r3/ady.png (the audit): the loop from the summit to the fork above Jeff's Ode to Joy's label (CUTS)
    ((843, 80), 'JEFF’S ODE TO JOY'),
]
UNNAMED = [
    # sy_top.png
    ((995, 470), 'a blue link from the Symphony Express lift line to Burnt Stew Trail, unnamed'),
    ((926, 112), 'a short black line under the summit with no name'),
]
CUTS = [
    # r3/ady.png (the audit): one blue stroke from Adagio's label up to the fork above Jeff's Ode to Joy's label, then
    # round a loop from the summit and back to the fork: cut at the fork (the loop's two sides are Jeff's Ode to Joy -
    # Upper's two routes from the top, in the resort's ArcGIS run lines, and Adagio - Upper starts on it there)
    ((747, 359), (805, 177)),
]
TRACED = [
]
