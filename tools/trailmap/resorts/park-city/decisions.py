"""Naming decisions settled on crops, keyed by points in map px (work/park-city/map.png), so they survive a
re-extraction: pdf_resort.py finds the piece through each point. `pdf_resort.py park-city add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # pc/zoom/sunrise_top.jpg: Sunrise's dashed line above the cut where Raptor Way's arc meets it
    ((2953, 1566), 'SUNRISE'),
    # audit, osm_lr_280.png, willow.jpg: the dashed line from behind the Rip Cord sign to the Canyons base is Willow Draw's run-out (its solid line ends at the sign's far side; OpenStreetMap's Willow Draw runs on to the base); Lookout Ridge, Outlaw and Sixes end on it
    ((3090, 1862), 'WILLOW DRAW'),
    # audit (pc/zoom/*, PDF strokes in drawing order (allstrokes.py), OpenStreetMap (osmcheck.py)): Silverado's black line goes on below its name to the Eagle junction (the Silverado Bowl oval has no line); Chrome Alley's line from its symbol up to Upper White Pine's name's end (its arrow points that way; drawn right before Chrome Alley's own stroke); the branch from Red Fox's line ending between the Red Fox and Hawkeye symbols (drawn with Red Fox's strokes; Hawkeye's own line is the one from Buckeye's); Sundog's line on below its symbol to where the blue runs meet (OpenStreetMap's Sundog runs there; 10th Mountain is printed in an oval); the line from Upper Crowning Glory's name's end to Middle Crowning Glory's symbol (Mystic Pines is printed in an oval); Panorama's dashed line on below its second name to the Dreamscape base (OpenStreetMap's Panorama runs there; McDonalds Meadow's line ends at it); Blaster's line from Belmont's down behind the Adventure Alley sign (drawn with Blaster's strokes)
    ((3184, 1499), 'SILVERADO'),
    ((1762, 1141), 'CHROME ALLEY'),
    ((711, 455), 'RED FOX'),
    ((633, 425), 'SUNDOG'),
    ((2540, 653), 'UPPER CROWNING GLORY'),
    ((667, 683), 'BLASTER'),
    ((2258, 728), 'PANORAMA'),
    # x_mimi.png, osm_mimi_516.png, c_ob.png: Mimi's Way's line beside its label (small text), from Blaise's Way's turn down to the gondola top (Blaise's Way's own line runs along its label and round the loop; OpenStreetMap's Mimi's Way is this one); the Transitions park's orange line on below its M sign down to Echo's symbol
    ((1610, 1014), 'MIMI’S WAY'),
    ((3456, 1003), 'TRANSITIONS'),
    # u1-u3, c_rp.png, osm_rp_504.png (and the PDF's drawing order): Copperhead's dashed line between its two labels; at the Red Pine base, the dashed easier way down from the top of the Over and Out lift drawn as one stroke into Sunrise's symbol (Sunrise's; Raptor Way branches off it at its own symbol), the arc from Doc's Run with its arrow onto that route drawn with Raptor Way's strokes (its start), and the line from Doc's Run across the route into Retreat's (drawn with Retreat's); Diablo's from Lookout Ridge into its symbol; Willow Draw's dashed end; Flume's dashed line from the top of the lift into its symbol; Lower Boa's dashed line on from its name along the slow zone
    ((2056, 1558), 'COPPERHEAD'),
    ((2981, 1631), 'SUNRISE'),
    ((3002, 1571), 'RAPTOR WAY'),
    ((3024, 1633), 'RETREAT'),
    ((3296, 1690), 'DIABLO'),
    ((3321, 1815), 'WILLOW DRAW'),
    ((3543, 1580), 'FLUME'),
    ((3748, 1625), 'LOWER BOA'),
    # s3.png, c_486.png, c_pd.png, c_428.png (and the PDF's drawing order): Upper Boa's dashed line from the top of the Super Condor lift into its symbol; Blaise's Way's line on from its name over the rise and down round the gondola station (its arrow points down it); Boogeyman's and Pipe Dream's black lines broken at the village roads, each drawn right after its own strokes; Copperhead's dashed line from Chrome Alley's arrow into its name's end
    ((4020, 847), 'UPPER BOA'),
    ((1664, 1060), 'BLAISE’S WAY'),
    ((2030, 1005), 'BOOGEYMAN'),
    ((2048, 1055), 'BOOGEYMAN'),
    ((1938, 958), 'PIPE DREAM'),
    ((1866, 1228), 'COPPERHEAD'),
    # s1.png, s2.png (and the PDF's drawing order): at the top of the Ninety-Nine 90 lift, Red Pine Road's dashed line from the lift top into its symbol, Grande's and Deschutes' black stubs from the lift top into their double diamonds; Snow Dancer's line on below its symbol to where Badger's Bypass leaves it and on (solid) down to the Saddleback base; Flying Salmon's from Snow Dancer's line past the Adventure Alley sign into its name's end
    ((2914, 747), 'RED PINE ROAD'),
    ((2912, 751), 'GRANDE'),
    ((2916, 776), 'DESCHUTES'),
    ((3138, 803), 'SNOW DANCER'),
    ((3083, 1022), 'SNOW DANCER'),
    ((3202, 705), 'FLYING SALMON'),
    # r1.png, c_hm_r.png, c_hm_l.png, c_hm_inset.png: in the High Meadow Park inset, Hidden Bear's green line from its symbol down to Mellow Moose's and Snow Dancer's below its symbol; the lines entering the inset from above print no name there (the inset is redrawn, not a copy of the main map, so its lines can't be matched to the main map's)
    ((3762, 170), 'HIDDEN BEAR'),
    ((3450, 358), 'SNOW DANCER'),
    # c_sc1.png, c_sc2.png, q1.png, q2.png, c_ob.png (and the PDF's drawing order): the Super Condor experts' runs are drawn line, name, double diamond, line: each one's line on down-left from its double diamond (Western Boundary, A Chute, Lone Pine and Funnel Cloud across EZ Street, Yard Sale, Sticks & Stones' stub to Spider Monkey); EZ Street's on from its switchback down under the Super Condor lift (its arrow points that way); Boomer's dashed line either side of its name; Mainline's from Upper Mainline's junction down into its name's end
    ((3738, 869), 'WESTERN BOUNDARY'),
    ((3764, 914), 'A CHUTE'),
    ((3717, 1006), 'LONE PINE'),
    ((3760, 964), 'LONE PINE'),
    ((3723, 1047), 'FUNNEL CLOUD'),
    ((3767, 1009), 'FUNNEL CLOUD'),
    ((3691, 1183), 'YARD SALE'),
    ((3632, 1288), 'STICKS & STONES'),
    ((3801, 1125), 'EZ STREET'),
    ((3424, 1360), 'BOOMER'),
    ((3303, 1228), 'BOOMER'),
    ((3371, 930), 'MAINLINE'),
    # p1.png, p2.png, c_315.png: Whitewater's line on across the road into Cascade's (drawn right after Whitewater's strokes); Apparition's on past the lift's icon box down beside the lift to its base; Cloud 9's black line on past the TOMBSTONE ALLEY label down to the slow zone
    ((2216, 1196), 'WHITEWATER'),
    ((2155, 1104), 'APPARITION'),
    ((2790, 1273), 'CLOUD 9'),
    # c_res1.png, c_res2.png, c_harm3.png, seqarea.py (the PDF draws each run's strokes one after another): in the Canyons village each run is drawn in short strokes broken at the road crossings: Serenity's from its symbol down to Lower Harmony's dashed route; Showcase's from Serenity's symbol down into its own and on past its name to Lower Crowning Glory; Sanctuary's from its symbol down to Lower Crowning Glory's line; Lower Crowning Glory's on down to the Sunrise base; Lower Harmony's dashed route between its two HARMONY labels; Twilight's on across the road to the first HARMONY label's symbol, where Whitewater's line starts
    ((2290, 932), 'TWILIGHT'),
    ((2482, 1184), 'LOWER CROWNING GLORY'),
    ((2521, 1301), 'LOWER CROWNING GLORY'),
    ((2497, 953), 'SANCTUARY'),
    ((2480, 1025), 'SANCTUARY'),
    ((2449, 1174), 'SANCTUARY'),
    ((2392, 957), 'SHOWCASE'),
    ((2405, 996), 'SHOWCASE'),
    ((2487, 1129), 'SHOWCASE'),
    ((2346, 964), 'SERENITY'),
    ((2345, 1036), 'SERENITY'),
    ((2361, 1079), 'SERENITY'),
    ((2288, 995), 'LOWER HARMONY'),
    ((2299, 1072), 'LOWER HARMONY'),
    ((2371, 1152), 'LOWER HARMONY'),
    # c_dawn.png, c_dsb.png, o1-o4 (and each piece's stroke in the PDF's drawing order, seq.py; OpenStreetMap's runs, osmcheck.py): Elk Dance's line from its name, broken by the DAWN label's halo, on down to the arrow into Upper Harmony (OpenStreetMap's Elk Dance covers it; it was matched to Upper Harmony's label by its arrow end); Lazy Day's from its name down into Elk Dance's; Backstreet's past the Day Break lift's icon to the Dreamscape base (drawn right after Backstreet's own stroke); Upper Harmony's dashed line on below its second label; OO2's dashed line on from its symbol to Panorama's; Oops' from its name's end down to Backstreet; Sanctuary's from Power Alley down into its name's end; Middle Crowning Glory's from its name's end down across Power Alley to Lower Crowning Glory; Rhapsody's from the Peak 5 base into its name's end
    ((2412, 611), 'ELK DANCE'),
    ((2442, 593), 'LAZY DAY'),
    ((2339, 753), 'BACKSTREET'),
    ((2394, 755), 'UPPER HARMONY'),
    ((2235, 529), 'OO2'),
    ((2263, 632), 'OOPS'),
    ((2503, 826), 'SANCTUARY'),
    ((2588, 731), 'MIDDLE CROWNING GLORY'),
    ((2656, 839), 'RHAPSODY'),
    # n1-n3, t12/t13 tiles: a black line from the Silver Star run across under its lift, through a diamond printed alone, into Ligety Split's line (OpenStreetMap's Ligity Split takes this way); Keystone's second branch down to Jupiter Access; the black line from Fool's Gold's end across Thaynes Canyon into Lite's Out's double diamond; Reaper's line drawn on from its symbol down to the Flat Iron lift (Trance's joins it); Bugle Ridge Bypass's from its name's end up to Pipe Dream; Panorama's dashed line from the top of the Dreamscape lift into its symbol
    ((1014, 1520), 'LIGETY SPLIT'),
    ((993, 1530), 'LIGETY SPLIT'),
    ((1152, 453), 'KEYSTONE'),
    ((1296, 827), 'LITE’S OUT'),
    ((1790, 832), 'REAPER'),
    ((1887, 737), 'BUGLE RIDGE BYPASS'),
    ((2077, 593), 'PANORAMA'),
    # l9-l11, c_2.png, c_div.png, c_95.png, l6.png, t20/t21 tiles: Alloy Alley's line under its name past the Adventure Alley sign to the Town lift; Bonanza's from under the Bonanza Express terminal down to the slow zone; Lower Silver Skis' from Homerun's dashed line into its symbol; Erika's Gold's arc from the top of the King Con lift down into its line; Rose Bud's dashed line on to the King Con lift's top
    ((367, 1304), 'ALLOY ALLEY'),
    ((412, 950), 'BONANZA'),
    ((524, 1097), 'LOWER SILVER SKIS'),
    ((769, 1043), 'ERIKA’S GOLD'),
    ((834, 1014), 'ROSE BUD'),
    # k490.png, c_stope.png, k373.png: Stope's line on from its name's end to where Turtle Trail's joins it (First Time's below); Dawn's line from the top of the Day Break lift down along it into its symbol (Elk Dance's starts beside the lift's top, along its name)
    ((621, 1505), 'STOPE'),
    ((2355, 527), 'DAWN'),
    # l1-l4, m1-m4 (crops of map.png, pieces drawn on): Georgeanna's dashed line from above into its symbol and on past the McConkey's lift (its solid branch down into Powder Monkey's label is Powder Monkey's top, as OpenStreetMap's Powder Monkey runs); Hawkeye's line on to Buckeye's; Lucky Boy's along the Pioneer lift to its base; Crescent's from the top of the Crescent lift to where Silver Skis leaves it; Mid-Mountain Meadows' past its label's end to the lift; Detonator's past the Adventure Alley sign to the Silverlode lift; Double Jack's from the Summit House; Claimjumper's from the Viking Yurt down the slow zone and dashed past the 3/4 Load junction into its symbol (Rose Bud starts at that junction; OpenStreetMap's Claim Jumper covers it)
    ((445, 426), 'GEORGEANNA'),
    ((561, 506), 'GEORGEANNA'),
    ((538, 506), 'POWDER MONKEY'),
    ((663, 472), 'HAWKEYE'),
    ((664, 550), 'LUCKY BOY'),
    ((598, 883), 'CRESCENT'),
    ((738, 639), 'MID-MOUNTAIN MEADOWS'),
    ((1030, 976), 'DETONATOR'),
    ((858, 525), 'DOUBLE JACK'),
    ((846, 947), 'CLAIMJUMPER'),
    ((660, 796), 'CLAIMJUMPER'),
]
UNNAMED = [
    # audit (pc/zoom/*, PDF strokes in drawing order (allstrokes.py), OpenStreetMap (osmcheck.py)): the green link from the top of the Crescent lift up to Homerun's dashed line (its arrow points to Homerun; 1/4 Load's own line leaves the lift top the other way); the blue link from Homerun's dashed line down to Silver Queen's arrow (drawn with the Loads, apart from Silver Queen's own strokes; Berg's Bowl is printed in an oval); the blue run-out below Phantasm's name across the Dreamcatcher lift to Apparition (OpenStreetMap ends Phantasm, Illusion, Chimera and Specter at the lift)
    ((601, 818), 'a green link from the top of the Crescent lift up to Homerun’s dashed line (its arrow points up to Homerun), with no name'),
    ((574, 853), 'a blue link from Homerun’s dashed line at the Viking Yurt down to Silver Queen’s arrow, with no name (drawn with the Loads’ strokes, not Silver Queen’s)'),
    ((2127, 935), 'the blue run-out from where Phantasm, Illusion, Chimera and Specter end, across the Dreamcatcher lift to Apparition, with no name of its own (OpenStreetMap ends those runs at the lift)'),
    # r1.png, c_hm_r.png, c_hm_l.png, c_hm_inset.png: in the High Meadow Park inset, Hidden Bear's green line from its symbol down to Mellow Moose's and Snow Dancer's below its symbol; the lines entering the inset from above print no name there (the inset is redrawn, not a copy of the main map, so its lines can't be matched to the main map's)
    ((3936, 53), 'a black line entering the High Meadow Park inset from above, its run named only on the main map'),
    ((3822, 65), 'a black line entering the High Meadow Park inset from above, its run named only on the main map'),
    ((3602, 246), 'a dashed blue line entering the High Meadow Park inset from above along the Saddleback lift, its run named only on the main map'),
    ((4138, 52), 'a blue line entering the High Meadow Park inset from above, its run named only on the main map'),
    # c_dawn.png, c_dsb.png, o1-o4 (and each piece's stroke in the PDF's drawing order, seq.py; OpenStreetMap's runs, osmcheck.py): Elk Dance's line from its name, broken by the DAWN label's halo, on down to the arrow into Upper Harmony (OpenStreetMap's Elk Dance covers it; it was matched to Upper Harmony's label by its arrow end); Lazy Day's from its name down into Elk Dance's; Backstreet's past the Day Break lift's icon to the Dreamscape base (drawn right after Backstreet's own stroke); Upper Harmony's dashed line on below its second label; OO2's dashed line on from its symbol to Panorama's; Oops' from its name's end down to Backstreet; Sanctuary's from Power Alley down into its name's end; Middle Crowning Glory's from its name's end down across Power Alley to Lower Crowning Glory; Rhapsody's from the Peak 5 base into its name's end
    ((2301, 763), 'the run-out beside the Dreamscape lift to its base, where McDonalds Meadow, Bliss, Day Dream and Deja Vu end, with no name of its own'),
    # l9-l11, c_2.png, c_div.png, c_95.png, l6.png, t20/t21 tiles: Alloy Alley's line under its name past the Adventure Alley sign to the Town lift; Bonanza's from under the Bonanza Express terminal down to the slow zone; Lower Silver Skis' from Homerun's dashed line into its symbol; Erika's Gold's arc from the top of the King Con lift down into its line; Rose Bud's dashed line on to the King Con lift's top
    ((461, 1113), "a blue link from Treasure Hollow's line to Homerun at the top of Waterfall, with no name"),
    ((1003, 1068), "a blue link from King Con's line down to High Card's, with no name"),
    ((820, 1296), "an arrowhead printed below Gotcha Cut-Off's name"),
    # l1-l4, m1-m4 (crops of map.png, pieces drawn on): Georgeanna's dashed line from above into its symbol and on past the McConkey's lift (its solid branch down into Powder Monkey's label is Powder Monkey's top, as OpenStreetMap's Powder Monkey runs); Hawkeye's line on to Buckeye's; Lucky Boy's along the Pioneer lift to its base; Crescent's from the top of the Crescent lift to where Silver Skis leaves it; Mid-Mountain Meadows' past its label's end to the lift; Detonator's past the Adventure Alley sign to the Silverlode lift; Double Jack's from the Summit House; Claimjumper's from the Viking Yurt down the slow zone and dashed past the 3/4 Load junction into its symbol (Rose Bud starts at that junction; OpenStreetMap's Claim Jumper covers it)
    ((469, 665), "the leader from the Mid Mountain Lodge's sign to the lodge"),
]
CUTS = [
    # l4.png: one black stroke from Crescent's label up to the fork below the top of the Crescent lift and down to
    # Silver Skis' label: cut at the fork
    ((560, 935), (588, 906)),
    # k96.png: one black arc from Picabo's name's end over the Eagle lift's station to Commitment's: two runs from
    # the station, cut where the arc passes it
    ((834, 1439), (847, 1441)),
    # k449.png: one blue line from UPPER LOOKOUT RIDGE's name's end down to LOOKOUT RIDGE's: cut where Thunder Rd
    # crosses it (OpenStreetMap ends Upper Lookout Ridge and starts Lookout Ridge by there)
    ((3294, 1574), (3293, 1605)),
    # k297.png: one dashed blue line from UPPER BOA's name's end down to LOWER BOA's: cut halfway
    ((4100, 1102), (4113, 1189)),
    # pc/zoom/sunrise_top.jpg: Sunrise's dashed line, from the top of the Red Pine gondola down to Raptor Way's
    # symbol, is met halfway by Raptor Way's arc from Doc's Run: cut it there, so Raptor Way's overlay joins it at
    # the arc's end rather than at the line's next drawn point above it (both halves stay Sunrise's)
    ((2956, 1572), (2972, 1600)),
]
TRACED = [
    # pc/zoom/ft_all.jpg: two runs whose name, printed on two lines, covers their line: Upper First Time's from the
    # end of its hook off the 3 Kings lift's top down through its name; Turtle Trail's from its symbol down through
    # its name to its short line into the First Time lift's top
    ('UPPER FIRST TIME', [(688, 1427), (688, 1436), (676, 1452), (664, 1468)]),
    ('TURTLE TRAIL', [(628, 1452), (632, 1464), (635, 1476), (635, 1482)]),
    # symbol_audit.py (off), pc/zoom/gaps.jpg: names printed on two or three lines (no stretch along them) or beside
    # the start of their line, between their symbol and the line: from the symbol through the name to the line
    ('LAZY DAY', [(2422, 516), (2440, 524), (2448, 531)]),
    ('MID-MOUNTAIN CUTOFF', [(582, 528), (587, 555), (598, 581)]),
    ('MIDDLE CROWNING GLORY', [(2542, 668), (2549, 679), (2561, 696), (2572, 716)]),
    ('BUGLE RIDGE BYPASS', [(1860, 718), (1872, 727), (1884, 737)]),
    ('ROAD TO THAYNES CANYON', [(1197, 1280), (1229, 1293), (1258, 1298)]),
    ('OOPS', [(2238, 632), (2252, 621), (2263, 613), (2262, 627)]),
]
