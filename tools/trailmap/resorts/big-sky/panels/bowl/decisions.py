"""Naming decisions for the bowl panel, settled on crops, keyed by points in map px
(work/big-sky/bowl/map.png), so they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on under another line: cut it nearest the
         second and drop the part beyond
"""
CHECKED = [
    # bs/bw_gul.png, bs/bw_tl.png, bs/bw_cc0.png, bs/bw_bl0.png (OpenStreetMap's runs): The Gullies' six lines (numbered 1 to 6, each with its symbol) below the Gullies Traverse; Cron's line leaving the first gully under TO CRON'S; Liberty Bowl's line from the summit down the switchbacks past its diamond (as on the South Face inset), hidden under the logo where it meets the Yeti Traverse; Highway's line from the top past its name and diamond to Blue Moon (Country Club is the bowl beside it, its name and diamond on the open slope); Rice Bowl's line below its name and diamond; Cow Flats' line from the Swift Current top west to its name
    ((1037, 733), 'The Gullies'),
    ((1079, 1041), 'The Gullies'),
    ((945, 782), 'The Gullies'),
    ((912, 859), 'The Gullies'),
    ((863, 858), 'The Gullies'),
    ((920, 1091), 'The Gullies'),
    ((1131, 812), "Cron's"),
    ((438, 394), 'Liberty Bowl'),
    ((589, 269), 'Liberty Bowl'),
    ((2683, 1869), 'Highway'),
    ((954, 2604), 'Rice Bowl'),
    ((353, 2521), 'Cow Flats'),
]
UNNAMED = [
    # bs/bw_cc0.png, bs/osm_bw_44.png, bs/osm_bw_52.png, bs/bw_sf0.png
    ((2548, 1989), "a link from where the LRT Traverse ends and Little Tree begins, east to Highway's line, with no name (Zucchini Patch is the tree area below it, its name and double diamond in the trees)"),
    ((1715, 1189), "a blue loop off Morningstar's line round the patrol hut, to the foot of the A-Z chutes' lines, with no name"),
    ((1337, 2221), "a short blue link from Morningstar's line down to White Wing's, with no name"),
    ((206, 2830), "a blue line from Stump Farm's down toward Lobo's, cut by the inset's frame, with no name on this inset"),
]
CUTS = [
    # bs/bwu2.png: one stroke carries the Turkey Traverse from the Powder Seeker top across the bowl, and Exit Chute
    # from where it turns downhill (its double diamond and name below) to the tram base: cut at the turn
    ((846, 1343), (510, 1826)),
]
TRACED = [
]
TRIMS = [
    # bs/c_lb2.png, bs/c_lb3.png (bs/overlaps.py): Liberty Bowl's line runs on from where it meets the Yeti Traverse
    # along the traverse to Otter Slide's foot; the traverse's line is the Yeti Traverse's
    ((356, 511), (550, 509)),
]
