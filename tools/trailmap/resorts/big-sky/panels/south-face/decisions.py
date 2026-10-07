"""Naming decisions for the south-face panel, settled on crops, keyed by points in map px
(work/big-sky/south-face/map.png), so they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on under another line: cut it nearest the
         second and drop the part beyond
"""
CHECKED = [
    # bs/sfu3.png: Ace's line from Tohelluride's top symbol down along its name, beside King's
    ((2014, 613), 'Ace'),
    # bs/sfu1.png, bs/sfu2.png, bs/sf_cow.png, bs/sf_grill.png (OpenStreetMap's runs): Gullies Traverse's line from Marx's to its symbol; Liberty Bowl's line through its diamond and on up to the summit ridge past its second diamond; Skittles Road on east of Cow Flats under the pointer TO MOUNTAIN VILLAGE, and from the Shedhorn grill to where its stroke starts; White Pine's line through its name and diamond (Bitterroot's is beside it); Yogi's line below its name to its diamond; Screaming Left's line on across Upper Sunlight's to the grill
    ((1763, 440), 'GULLIES TRAVERSE'),
    ((1282, 566), 'Liberty Bowl'),
    ((1391, 272), 'Liberty Bowl'),
    ((3226, 1063), 'Skittles Road'),
    ((2246, 1522), 'White Pine'),
    ((3102, 975), "Yogi's"),
    ((1761, 1031), 'Screaming Left'),
    ((1855, 1046), 'Skittles Road'),
]
UNNAMED = [
]
CUTS = [
    # bs/sf_cow.png, bs/sfu2.png, bs/sf_grill.png (OpenStreetMap's runs): one stroke carries Skittles Road from the
    # Shedhorn grill east and Cow Flats' upper part north from where they meet; one carries Upper Sunlight down to
    # where Mule Skinner's line from the grill crosses it and Sunlight below; one carries Dakota Road down to where
    # Hippy Highway's line joins it and Hippy Highway on east
    ((2445, 1149), (2884, 1061)),
    ((1709, 974), (1747, 1143)),
    ((1449, 1577), (1693, 1626)),
]
TRACED = [
]
TRIMS = [
    # bs/c_ym.png, bs/c_ace.png (bs/overlaps.py: lines lying along another): Yellow Mule's black line runs its last
    # stretch under Lupine's blue one; Ace's line and King's both run from their shared double diamond along the
    # traverse, which goes on to King's: Ace's starts where it turns down
    ((2230, 1129), (2549, 1451)),
    ((2023, 651), (2003, 586)),
]
