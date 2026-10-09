"""Naming decisions settled on crops, keyed by points in map px (work/steamboat/map.png), so they survive a
re-extraction: pdf_resort.py finds the piece through each point. `pdf_resort.py steamboat add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs

Every piece is named by its interactive-map group (resort.GROUPED); these are where the print differs from it. A
traced stretch is read with tools/trailmap/trace_ink.py (the cheapest path along the print's line pixels between
points read off a grid crop) and checked on its --show crop.
"""
CHECKED = [
]
UNNAMED = [
    # miss/bashor_p.png against miss/bashor_new.png: the interactive map's Bashor and Bear Claw lines lie 20-30 px off
    # the print's (an earlier drawing of the parks' area): left out, and the print's lines traced (TRACED)
    ((1199, 1295), "the interactive map's Bashor, off the print's line: traced instead"),
    ((1344, 1272), "the interactive map's Bashor, off the print's line: traced instead"),
    ((1442, 1222), "the interactive map's Bear Claw, off the print's line: traced instead"),
    ((1482, 1172), "the interactive map's Bear Claw, off the print's line: traced instead"),
    # miss/conc_p.png against miss/conc.png, miss/vag_p.png, miss/whynot_top.png: the 2026-27 artwork redrew the
    # middle of Sunshine (Concentration's line and name, Rudi's Run, Vagabond's head): the interactive map's lines
    # there are off the print's; left out and the print's traced (TRACED)
    ((1056, 1009), "the interactive map's Concentration, off the print's line: traced instead"),
    ((1148, 899), "the interactive map's Concentration, off the print's line: traced instead"),
    ((1229, 803), "the interactive map's head of Vagabond, off the print's line: traced instead"),
    ((1192, 771), "the interactive map's Rudi's Run, a stub off the print's line: traced instead"),
    # All Out, printed "(closed to public)": no run the report lists (resort.DROP leaves out its label)
    ((1534, 1419), 'All Out, closed to public: no run the report lists'),
    ((1513, 1319), 'All Out, closed to public: no run the report lists'),
    ((1521, 1243), 'All Out, closed to public: no run the report lists'),
]
CUTS = [
]
TRACED = [
    # miss/t_bashor.png: the blue line between Rabbit Ears Terrain Park and Maverick's, from Bear Claw's foot down to
    # the Bashor lift's base (the interactive map's Bashor, as it lies on the print)
    ('Bashor', [(1368, 1228), (1337, 1230), (1255, 1254), (1167, 1294), (1163, 1298)]),
    # miss/t_conc.png: Concentration's black line from Vagabond's down past its diamond and along its name (read
    # straight along the letters) to Betwixt's
    ('Concentration', [(1163, 848), (1158, 868), (1151, 891), (1146, 909), (1135, 920), (1112, 936), (1100, 947),
                       (1063, 1010), (1058, 1028)]),
    # miss/whynot_top.png: Rudi's Run is its name with a dash each side, from its square by Thunderhead
    ("Rudi's Run", [(1262, 778), (1245, 778), (1215, 781), (1178, 783)]),
    # miss/vag_p.png: Vagabond's head, from Thunderhead past its square and along its name to the line below it
    ('Vagabond Upper', [(1270, 791), (1243, 805), (1228, 812), (1172, 838), (1160, 840)]),
    # miss/t_bear.png: Bear Claw's line from Jess' Cut-Off down along its name to Bashor's head
    ('Bear Claw', [(1478, 1168), (1458, 1186), (1449, 1190), (1446, 1196), (1436, 1204), (1424, 1206), (1415, 1213),
                   (1408, 1211), (1387, 1221), (1372, 1224), (1370, 1228)]),
]
