"""Naming decisions settled on crops, keyed by points in map px (work/beaver-creek/map.png), so they survive a
re-extraction: pdf_resort.py finds the piece through each point. `pdf_resort.py beaver-creek add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # cent_up.png, cent crops: Centennial's parts: Hohum's green line from the summit's circle to the lift, Spruce Face's black line from there past its diamond to Spruce Saddle, Willy's Face's line on down past Dally to Finish Face's diamond (the report's Flats, no name or symbol), Finish Face's from its diamond to the base
    ((1748, 528), 'Centennial - Hohum'),
    ((1620, 780), 'Centennial - Hohum'),
    ((1520, 872), 'Centennial - Spruce Face'),
    ((1443, 1112), 'Centennial - Spruce Face'),
    ((1613, 1783), "Centennial - Willy's Face"),
    ((1704, 2155), 'Centennial - Finish Face'),
    # wap.png: Wapiti's line from the square at the end of its name on down
    ((4062, 2541), 'Wapiti'),
    # mge.png, mge2.png: Middle Golden Eagle's line from its double diamond down to Lower Golden Eagle's diamond, both branches round the trees above it
    ((2231, 1161), 'Middle Golden Eagle'),
    ((2289, 1302), 'Middle Golden Eagle'),
    # z7, p211.png, p45.png: each cut line's two parts, either side of the second run's symbol
    ((1336, 2438), 'Highlands Skiway'),
    ((1943, 2714), 'Charter Skiway'),
    ((2886, 2253), 'Maverick'),
    ((3335, 2549), 'Second Chance'),
    # z7, p75.png, p45.png: Upper Golden Eagle's line from its double diamond down to Middle Golden Eagle's; Barrel Stave's square on this line (Gold Dust's is on the one beside it); Meander's line from its circle down to where Maverick starts
    ((1982, 954), 'Golden Eagle - Upper'),
    ((1008, 1450), 'Barrel Stave'),
    ((2938, 2220), 'Meander'),
    # z5, p175.png, z6, p204b.png, p211.png, p222.png: the line each continues or forks from
    ((877, 937), 'Ripsaw'),
    ((1879, 698), 'Golden Eagle - Upper'),
    ((1570, 980), 'Goshawk Upper'),
    ((3677, 2044), 'Cabin Fever'),
    ((1028, 836), 'Red Buffalo'),
    ((1374, 2419), 'Highlands Skiway'),
    ((2196, 1802), 'Harrier - Lower'),
    # crops/p128.png: a second black line through Thresher Glade, beside the one its name is printed along (OpenStreetMap's Thresher Glade covers it); z4: Coyote Glade's line from under its label; p102: Cabin Fever's line from its upper name down across Primrose to its lower circle
    ((2869, 1800), 'Thresher Glade'),
    ((3305, 2225), 'Coyote Glade'),
    ((3678, 2136), 'Cabin Fever'),
    # crops/p104.png: the blue line down to the square above the Piece O' Cake road, Wapiti's diamond and line below it (OpenStreetMap's Wapiti Upper covers it all); p73: Roughlock's square at this line's top, ROUGHLOCK beside it
    ((3938, 2286), 'Wapiti'),
    ((3681, 2691), 'Roughlock'),
    # crops/pf.png: President Ford's black line (20) runs on past the Intertwine catwalk as this blue line under the Strawberry Park lift, Stacker's (23) as the other; the blue squares on them mark where they turn blue (the report's President Ford's - Lower and Stacker - Lower)
    ((2208, 2298), "President Ford's - Lower"),
    ((2259, 2296), 'Stacker - Lower'),
]
UNNAMED = [
    # b262.png: no trail
    ((1570, 465), "a gladed zone's brown mark by a kids' adventure zone icon above Mystic Island, no name"),
    # z5, p197.png: no trail
    ((1135, 1130), "a 6 px stub by Keller Glade's diamond (the glade is a marker)"),
    ((1340, 1129), 'a blue link from the catwalk down to the lime-green line, no name'),
    # crops/sk.png, p73.png, p102.png, p135b.png: lines with no name or symbol of their own
    ((2894, 2675), 'a link from Bedstraw to Elkhorn Skiway'),
    ((2537, 2770), 'a dotted branch west off McCoy Skiway, no name'),
    ((3589, 1319), "a blue line from the Larkspur lift's top down to McCoy Park, no name or symbol"),
    ((3638, 2205), "the traverse west from Zach's Cabin, under Sourdough's Slide's icons: no name or symbol"),
    ((3856, 2132), "a link from the top of lift 17 to the Zach's Cabin traverse"),
    ((1996, 1276), "a black traverse with two diamonds from the end of West Fall Road to Golden Eagle, no name (the report's Golden Eagle Connector, probably)"),]
CUTS = [
    # z7, p211.png: the dotted skiway from Highlands Skiway's circle down past Charter Skiway's circle to lift 14:
    # Highlands Skiway down to the circle, Charter Skiway from it
    ((1336, 2438), (1610, 2660)),
    # z7: the green line from Upper Stirrup's circle round past lift 17 to Lower Stirrup's circle and on down: Upper
    # Stirrup to the circle, Lower Stirrup from it
    ((3931, 2040), (3795, 2218)),
    # p45.png: the line from Maverick's circle round to Second Chance's circle and on to lift 15: Maverick to the
    # circle, Second Chance from it
    ((2886, 2253), (3175, 2381)),
]
TRACED = [
    # toyota.png: the Toyota Race Center's course, the red line between its two race icons beside the logo
    ('Toyota Race Center', [(1494, 1622), (1492, 1700), (1491, 1780), (1489, 1848)]),
    # dakota.png: Dakota Skiway, new on the 2025-26 image: its dotted line from its circle to the base of lift 17
    ('Dakota Skiway', [(4267, 3075), (4284, 3061), (4312, 3055), (4337, 3052), (4366, 3049), (4394, 3042), (4419, 3033),
                       (4441, 3017), (4456, 3002), (4469, 2992)]),
]
