"""Naming decisions for Telluride's main panel, settled on crops, keyed by points in map px
(work/telluride/main/map.png), so they survive a re-extraction: pdf_resort.py finds the piece through each point.
`pdf_resort.py telluride/main add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
# every undecided piece of the first build settled on per-piece crops (the piece in magenta, its neighbours named), and
# the tangled spots on renders of the PDF at 6-14x
CHECKED = [
    # Gold Hill and Bon Vivant: the lines on below a run's symbol to the run it meets
    ((1727, 922), 'Electra'),  # from ELECTRA's EX down to Lower Woozley's Way
    ((1696, 980), 'Buzz’s Glade'),  # from BUZZ'S GLADE's EX down to Lower Woozley's Way
    ((2140, 1067), 'Little Rose'),  # from LITTLE ROSE's double diamond to the Gold Hill Express base (z_e: Little
    ((2171, 955), 'Andy’s Gold'),  # Rose's line is the one from its diamond; Andy's Gold's passes the avalanche gate)
    ((1576, 1008), 'Happy Thought'),  # from HAPPY THOUGHT's double diamond down to Ophir Loop's square
    ((1495, 1086), 'Chongo’s'),  # from CHONGOS's double diamond down to Ophir Loop
    ((1361, 1168), 'Allais Alley'),  # from ALLAIS ALLEY's double diamond down to the Polar Queen base
    ((1377, 1210), 'Sully’s'),  # from SULLY'S's double diamond down to the Polar Queen base
    ((1463, 1268), 'Giant Steps'),  # from GIANT STEPS's double diamond to the base
    ((1565, 1026), 'Woozley’s Way'),  # from WOOZLEY'S WAY's squares east to Ophir Loop's top
    ((1314, 884), 'Woozley’s Way'),  # its start: down from See Forever under the Apex lift's top
    # the Plunge lift's side (spiral.png, p120.png: 14x and 12x renders)
    ((782, 1192), 'Spiral Stairs'),  # from the Plunge junction down to SPIRAL STAIRS's double diamond
    ((618, 1347), 'Spiral Stairs'),  # the stub from the lift line to the foot of its label
    ((772, 1199), 'Plunge'),  # the stub from the junction above PLUNGE's label to its top
    ((973, 891), 'Kant-Mak-M'),  # from the Plunge lift's top to KANT-MAK-M's double diamond (r1a.png)
    ((906, 1435), 'North Chute'),  # from NORTH CHUTE's double diamond up to the Lookout runs
    ((305, 1880), 'Mine Shaft'),  # the report's Mine Shaft (below Bail Out): from Bail Out's foot to MINE SHAFT
    ((556, 2004), 'Stumper'),  # from the Cimarron and Easy Out junction down to STUMPER's diamond
    ((906, 1131), 'Last Chance'),  # the stub from Plunge's line to LAST CHANCE's label
    ((897, 1237), 'Last Chance'),  # from its label down to See Forever
    ((881, 1349), 'Lookout – Upper'),  # from LOOKOUT's squares up to See Forever
    # See Forever, the Village and the Gorrono runs
    ((1206, 836), 'See Forever'),  # its curve from the Apex lift's top down to the Lift 7 side
    ((1288, 843), 'See Forever'),  # its line below the Apex lift's top
    ((890, 1569), 'Telluride Trail'),  # its start from the San Sophia ridge to its square
    ((960, 1540), 'Telluride Trail'),
    ((984, 1670), 'Butterfly'),  # from the San Sophia first aid down to BUTTERFLY
    ((1273, 1763), 'Butterfly'),  # on from its label east to Misty Maiden
    ((1237, 1707), 'Smuggler'),  # from SMUGGLER's square down to Misty Maiden
    ((1222, 1671), 'Hermit'),  # from HERMIT's square down to Misty Maiden
    ((1383, 1603), 'Humboldt Draw'),  # from HUMBOLDT DRAW's squares down to Gorrono
    ((1304, 1657), 'Village Bypass'),  # its green dots round Gorrono
    ((1848, 1970), 'Village Bypass – Lower'),  # z_c.png: under the Free Gondola into LOWER VILLAGE BYPASS
    ((1932, 2294), 'Village Bypass – Lower'),  # from its label's circles to the Meadows base
    ((1715, 2304), 'The Peaks'),  # from THE PEAKS east to the chondola's station
    ((393, 2195), 'Kids Hill'),  # from KID'S HILL down to the Carhenge station
    # Boomerang (z_a.png): from BOOMERANG's square the line forks, the right fork Sheridan Headwall, the one down
    # through the trees Boomerang, on to its LOWER BOOMERANG part below the Village Bypass
    ((1560, 1510), 'Boomerang'), ((1628, 1657), 'Boomerang'), ((1660, 1565), 'Sheridan Headwall'),
    # Polar Queen's runs round Bon Vivant (r2a.png, r2b.png)
    ((1639, 1071), 'Ophir Loop'),  # its two starts off Lower Woozley's Way, joining at its square
    ((1587, 1224), 'Ophir Loop'), ((1661, 1312), 'Ophir Loop'),  # from its upper label to its lower one
    ((1719, 1065), 'Stormin’ Norman'),  # from the restrooms down to its square
    ((1710, 1249), 'Stormin’ Norman'),  # from its label down to Dew Drop
    ((1791, 1065), 'Polar Queen'),  # from the Dew Drop fork down to its label
    ((1879, 1266), 'Silver Tip'),  # from Polar Queen's line to SILVER TIP's square
    # Sunshine and Ute Park
    ((2800, 1359), 'Holy Cow'),  # its line under the Sunshine Express, from the top to its label
    ((2607, 1366), 'Sundance'),  # from the warming huts down to the blue SUNDANCE
    ((2187, 1684), 'Sundance'),  # the green stub from the Teddy's Way fork to the green SUNDANCE's circles
    ((2869, 1568), 'Teddy’s Way'),  # on east from its label
    ((2937, 1827), 'Lower Galloping Goose'),  # from its label's circles down to BRIDGES
    ((3176, 1849), 'Lower Galloping Goose'),  # between its two labels
    ((2881, 1572), 'Double Cabin'),  # from its upper label round to its lower one
    ((2921, 1394), 'Enchanted Forest'), ((2916, 1394), 'Enchanted Forest'), ((2904, 1367), 'Enchanted Forest'),
    ((2998, 1415), 'Enchanted Forest'),  # ench.png: its loop and squares, from the Beginner Park icons down to
    # where Runaway Train's black line leaves it
    ((2934, 1527), 'Runaway Train'),  # from Enchanted Forest down to its double diamond
    ((2839, 1242), 'UTE Park'), ((2791, 1246), 'UTE Park'),  # its line past the lift's foot to Beginner Park
    ((2841, 1078), 'Nellie'),  # its start at the Ute and Lynx tops
    # Prospect Bowl (z_d.png, pb.png)
    ((2297, 1120), 'Sandia'),  # from the Prospect Express base up under PROSPECT BOWL into Sandia's line
    ((2158, 1141), 'Woozley’s Way – Lower'),  # on past the Gold Hill Express base to the Prospect Express base
    ((2201, 1346), 'Prospect Creek'),  # from The Roll down to PROSPECT CREEK's diamond
    ((2905, 821), 'Magnolia'), ((2979, 816), 'Magnolia'),  # its top from the Prospect Express top
    ((3043, 927), 'Stella'),  # from STELLA's squares up to Galloping Goose
    ((2922, 998), 'Madison'),  # on east from its circles
    ((3004, 990), 'May Girl'),  # from MAY GIRL's circles up to Galloping Goose
    # the second build: one stroke holding two runs' lines from the Black Iron Bowl gate (cut below), the green
    # stub from Madison's line into MAY GIRL, Lower Bail Out's foot
    ((2848, 768), 'Genevieve'), ((2872, 768), 'La Rosa'), ((2885, 785), 'Crystal'), ((2870, 810), 'Confidence'),
    ((2783, 1052), 'May Girl'),
    # the audit (aud_main): Jackpot's line from the hike-to top down to its double diamond (not Audrey's, whose label
    # sits on the line beside it); Nellie's line on below its circles to the Sunshine icons (not Beginner Park's)
    ((3180, 919), 'Jackpot'), ((2932, 1258), 'Nellie'),
    # lm.png: the green line between MADISON's two labels is Madison's (Little Maude's joins it at the lower one);
    # the black line from Jackpot's diamonds down along WILDCAT to its double diamond is Wildcat's
    ((2700, 1073), 'Madison'), ((3084, 1039), 'Wildcat'),
    # mn.png: the green line from the Mountain Village chondola station round into THE PEAKS is The Peaks' start
    ((1528, 2195), 'The Peaks'),
    ((2880, 1089), 'Nellie'),  # nel.png: its line from the Lynx and Ute Park tops round into its label
    # sat_strokes.png (each PDF stroke drawn alone): the stroke from the junction by the Plunge lift's top down under
    # SATISFACTION, its diamond on it, is Satisfaction's (not Plunge's, whose line leaves Spiral Stairs's lower down)
    ((838, 1165), 'Satisfaction'),
    ((475, 1947), 'Lower Bail Out'),
    # the parks' orange freestyle strokes (ute.png): Hoot Brown's under its name; the two by the Ute Park lift, the
    # left one UTE PARK's (its green name printed on it), the right one BEGINNER PARK's (its orange name by it); and
    # the green stub from the Ute Park top into LITTLE MAUDE
    ((1314, 1895), 'Hoot Brown Terrain Park'), ((2793, 1141), 'UTE Park'), ((2861, 1123), 'Beginner Park'),
    ((2785, 1088), 'Little Maude'),
]
UNNAMED = [
    ((1766, 1045), 'a link under Bon Vivant from Ophir Loop\'s top to the tops of Stormin\' Norman, Dew Drop and Polar '
                   'Queen: no name printed'),
    ((1743, 1021), 'a stub from Lower Woozley\'s Way to the Bon Vivant restrooms: no name printed'),
    ((2277, 1168), 'the arrowed link from Prospect Bowl west to the Gold Hill Express base: no name printed'),
    ((1379, 993), 'a 4 pt black stub by the Apex lift: no run'),
    # arrows from icons and labels to the places they mark
    ((1642, 748), 'the arrow from the Alpino Vino icon'), ((1546, 759), 'the arrow from the Tempter House icon'),
    ((2594, 388), 'the arrow to the Gold Hill Stairs'), ((1923, 1317), 'the arrow from GOLD RUSH to its glade'),
    ((2995, 666), 'the arrow from HIKE TO TERRAIN'), ((2454, 469), 'the arrow from a backcountry access point'),
    ((2149, 472), 'the arrow from a backcountry access point'), ((935, 825), 'the arrow from a backcountry access point'),
    ((2908, 1516), 'the arrow from RUNAWAY TRAIN to its line'), ((2199, 1171), 'an arrowhead on the arrowed links'),
    # the audit (nel.png): the green link from Nellie's line across the Ute Park lift to UTE PARK's circle (Ute Park's
    # own line starts at the lift's top): no name printed
    ((2874, 1116), 'a link from Nellie across the Ute Park lift to Ute Park: no name printed'),
] + [((x, y), 'an arrowhead on the arrowed links between the Gold Hill and Prospect Express bases')
     for x, y in ((2173, 1189), (2199, 1183), (2229, 1178), (2256, 1173), (2286, 1166), (2345, 1174), (2316, 1170),
                  (2218, 1204), (2104, 1115), (2132, 1124), (2160, 1142), (2179, 1160), (2198, 1184), (2214, 1212))]
# Boomerang's line runs on into Sheridan Headwall's fork: cut it at the fork (z_a.png)
CUTS = [((1618, 1544), (1608, 1540)),
        # the lines to GENEVIEVE and LA ROSA, and to CRYSTAL and CONFIDENCE, each one stroke from the junction by the
        # Prospect Express top up to both labels (m_00.jpg): cut at the junction
        ((2853, 762), (2811, 839)), ((2894, 774), (2811, 839))]
# LOWER VILLAGE BYPASS, printed on two lines in a gap of its line (z_c.png): its line through the label
TRACED = [('Village Bypass – Lower', [(1879, 2091), (1890, 2140), (1902, 2190), (1912, 2239), (1919, 2264)]),
          # SILVER GLADE, printed down a gap of its line from its diamond (sg_strokes.png: a stub above the diamond,
          # one below the label): the line through the label
          ('Silver Glade', [(1380, 983), (1376, 1005), (1365, 1040), (1360, 1085), (1356, 1130)])]
TRIMS = []
