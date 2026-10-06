"""Naming decisions settled on crops, keyed by points in map px (work/whistler-blackcomb/main/map.png), so they
survive a re-extraction: pdf_resort.py finds the piece through each point. `pdf_resort.py whistler-blackcomb/main
add` records new ones.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # wb/fl/kid.png (an auditor's flag): the green line on below Yellow Brick Road's label, ending by the KID TRAIL label (Kid Trail is the purple line from the Magic Chair)
    ((1745, 1974), 'YELLOW BRICK ROAD'),
    # r2/sbc.png, r2/ob.png, gistopo.py (where two trails' lines meet on the map, the resort's ArcGIS run lines should
    # meet too): the blue Cruiser line from Wishbone runs under both CRUISER labels down to Cruiser - Lower's symbol;
    # the black line on from Overbite's name's end to Blueline (the GIS lines have Overbite end on Blue Line, where
    # Davies Dervish starts); below where Big Easy's line joins Over Easy's, the green line on to Sunnyside Up is Big
    # Easy's (the GIS Big Easy - Lower; Over Easy ends at that junction)
    ((1109, 1314), 'CRUISER'),
    ((645, 789), 'OVERBITE'),
    ((1530, 1075), 'BIG EASY'),
    ((1431, 993), 'OVER EASY'),
    # r2/sunny.png: the green line from Sunset Boulevard's symbol down past the end of Sunnyside Up's label (where Sunnyside Up, from Easy Out, ends) and on past Gear Jammer and Slingshot to Greenline: Sunset Boulevard's, as the resort's ArcGIS run lines have it (Sunnyside Up ends where Sunset Boulevard starts; Gear Jammer - Lower starts on Sunset Boulevard, which ends at Green Line - Mid)
    ((1732, 1099), 'SUNSET BOULEVARD'),
    ((1595, 1252), 'SUNSET BOULEVARD'),
    ((1379, 1331), 'SUNSET BOULEVARD'),
    # r2/ddo.png, r3/bb.png (the audit): Dave's Day Off's line from Crystal Traverse, past the end of Brownlie Basin's
    # name, through its symbol and along its name (the resort's ArcGIS run starts at Crystal Traverse); Brownlie
    # Basin, printed beside it with no symbol, is the basin, with no line
    ((647, 722), 'DAVE’S DAY OFF'),
    # r2/ss3_pdf.png, r2/ss4.png, r2/p158c.png, r2/icon_pdf.png, r2/dd.png, r2/p185_pdf.png, r2/tl.png: the Straight Shot label is printed over two lines from the Crystal Ridge top, its own black one (a dash before the label, on after it) and a blue one: White Light's upper part (the resort's ArcGIS run lines have Trapline, White Light and Straight Shot all from the Crystal Ridge top to one junction at Crystal Road, where their lower parts start); there the blue line meets a blue symbol printed alone, which starts Straight Shot - Lower (the resort's blue part of Straight Shot), and a stub to White Light's symbol; Trapline's line on from its name's end; Davies Dervish's either side of its name; Dakine's below the Blueline crossing; Rider's Revenge's glade either side of its name
    ((558, 835), 'WHITE LIGHT'),
    ((679, 992), 'STRAIGHT SHOT - LOWER'),
    ((668, 1037), 'TRAPLINE'),
    ((649, 843), 'DAVIES DERVISH'),
    ((694, 903), 'DAVIES DERVISH'),
    ((715, 796), 'DAKINE'),
    ((567, 950), 'RIDER’S REVENGE'),
    ((626, 1023), 'RIDER’S REVENGE'),
    # r2/sc.png, r2/sy.png, r2/sch.png, r2/sb_top.png: Showcase's line beside its name from the top of the T-bar; Showcase Traverse's from the 7th Heaven top into its label; Sylvain's from its name's end to Saudan Couloir; Cougar Chute's printed across by its name; Jersey Cream Bowl's running into its name; the line from Secret Bowl down to Glacier Drive (the resort's ArcGIS run lines have Secret Bowl joining Glacier Drive - Upper; Secret Chute, beside it, has no line)
    ((753, 367), 'SHOWCASE'),
    ((853, 433), 'SHOWCASE TRAVERSE'),
    ((934, 553), 'SYLVAIN'),
    ((894, 710), 'COUGAR CHUTE'),
    ((1042, 694), 'JERSEY CREAM BOWL'),
    ((808, 680), 'SECRET BOWL'),
    # r2/p68.png, r2/gjl.png, r2/base.png: Slingshot's line from its name's end; Gear Jammer - Lower's from its name's end down to the tube park; the two learning areas' outlines
    ((1483, 1214), 'SLINGSHOT'),
    ((1790, 1629), 'GEAR JAMMER - LOWER'),
    # r2/gl2.png, r2/gl_pdf.png, r2/jp2.png, r2/dl.png, r2/ss.png: Come-a-long's and Greenline's dashed lines either side of where they meet, and Greenline's on from its second label down to Mainline - Lower's symbol; Strawline's and Jackpot's either side of Jackpot's symbol; Download Road's round its label and down; Grub Stake's from its name's end; Catskinner Traverse's through its symbol; So Sweet's glade printed across by its name
    ((962, 1133), 'COME-A-LONG'),
    ((931, 1302), 'GREENLINE'),
    ((1152, 1189), 'STRAWLINE'),
    ((1268, 1415), 'JACKPOT'),
    ((1141, 1586), 'GREENLINE'),
    ((1351, 1420), 'DOWNLOAD ROAD'),
    ((1351, 1558), 'GRUB STAKE'),
    ((1134, 990), 'CATSKINNER TRAVERSE'),
    ((1395, 1083), 'SO SWEET'),
    # r2/b2.png, r2/ret_pdf.png, r2/b3z.png, r2/ross.png, r2/cat.png, r2/lr.png, r2/lrw.png, r2/ren_pdf.png: Xhiggy's Meadow's line from its name's end; Everglades' glade below its name; Southside Green's dashed line on from its label to Expressway's symbol; the arrowed line into 7th Avenue's symbol; Ross' Gold's line from the lift into its symbol; the second line into Catskinner's symbol; the glades Bark Sandwich is printed beside and Where's Joe's and Raptor's Ride's from their names' ends; Magic Castle's family-area outline
    ((1344, 442), 'XHIGGY’S MEADOW'),
    ((1342, 661), 'EVERGLADES'),
    ((1162, 657), 'SOUTHSIDE GREEN'),
    ((1185, 766), 'SOUTHSIDE GREEN'),
    ((1275, 740), '7TH AVENUE'),
    ((1117, 834), 'ROSS’ GOLD'),
    ((1233, 828), 'CATSKINNER'),
    ((1328, 864), 'BARK SANDWICH'),
    ((1653, 867), 'WHERE’S JOE'),
    ((1643, 904), 'RAPTOR’S RIDE'),
    ((1395, 1006), 'MAGIC CASTLE'),
    # r2/b1z.png, r2/b1w_pdf.png, r2/p178.png: 7th Avenue's green line on from its name's end to the 7th Heaven Express base; Hugh's Heaven's blue line from its name's end (behind Angel Dust's label) to the same base
    ((1495, 614), '7TH AVENUE'),
    ((1541, 614), 'HUGH’S HEAVEN'),
    # r2/nl2.png, r2/lo.png: Northern Lights' blue lines from Lower Olympic's slow zone: the one through its symbol, and the one below its name joining it (the third runs into its name's end)
    ((2314, 1751), 'NORTHERN LIGHTS'),
    ((2383, 1762), 'NORTHERN LIGHTS'),
    # r2/emer.png, r2/gun.png, r2/lrf.png, r2/uo.png: Burnt Stew Trail's and Sidewinder's lines either side of Sidewinder's symbol; the two chutes Gun Barrels is printed across (Boomer Bowl, above, is the open bowl with no line); Lower Ratfink's green line under its label; the blue link from its end into Coyote's line under Coyote's label; the dashed line from the Emerald lift into Upper Olympic's name's end
    ((2152, 817), 'BURNT STEW TRAIL'),
    ((2280, 1000), 'SIDEWINDER'),
    ((2241, 767), 'GUN BARRELS'),
    ((2214, 765), 'GUN BARRELS'),
    ((2253, 898), 'LOWER RATFINK'),
    ((2278, 927), 'COYOTE'),
    ((2320, 1113), 'UPPER OLYMPIC'),
    # r2/sep2.png, r2/p171.png, r2/p213.png, r2/p3.png: Seppo's black line from its diamond to the blue label, and Seppo's - Lower's blue line branching off it and printed across by its name; Bear Paw's line on down from its symbol; Stefan's Chute's line through its symbol beside its name; the Snow School learning area's outline
    ((2504, 1166), 'SEPPO’S'),
    ((2530, 1278), 'SEPPO’S - LOWER'),
    ((2605, 1338), 'BEAR PAW'),
    ((3855, 447), 'STEFAN’S CHUTE'),
    # r2/creek.png, r2/gg.png, r2/dmdl.png, r2/kad2c.png: Goat's Gully's line from its name's end to Mid Station; Dave Murray Downhill's line either side of the Expressway crossing, and Lower's from its name's end to the base; the black branch from Expressway into it; Cross Roads' line after ROADS; Franz's on down from its name's end; Kadenwood Trail's from Franz's end into its symbol, under its name and on to the houses
    ((3195, 1347), 'GOAT’S GULLY'),
    ((3040, 1395), 'UPPER DAVE MURRAY DOWNHILL'),
    ((3400, 1500), 'DAVE MURRAY DOWNHILL - LOWER'),
    ((3213, 1477), 'DAVE MURRAY DOWNHILL - LOWER'),
    ((3748, 1886), 'DAVE MURRAY DOWNHILL - LOWER'),
    ((3416, 1443), 'CROSS ROADS'),
    ((3637, 1738), 'FRANZ’S'),
    ((3749, 1543), 'KADENWOOD TRAIL'),
    # r2/a.png, r2/pony_pdf.png, r2/p301top_pdf.png, r2/lrr.png, r2/oly.png, r2/crab.png: Tree Fort's family-area outline round its name; Banana Peel's line from its name's end to the easiest way down; Little Red Run's from its name's end; Pony Trail's and Expressway's lines under their labels either side of Mid Station; Expressway's on west to Upper Olympic; the dashed branch and the solid line into Lower Olympic's symbol; the blue line from Expressway into Crabapple's
    ((3029, 1038), 'TREE FORT'),
    ((3017, 942), 'BANANA PEEL'),
    ((3101, 913), 'LITTLE RED RUN'),
    ((3144, 1194), 'PONY TRAIL'),
    ((2851, 1474), 'EXPRESSWAY (WHISTLER)'),
    ((2529, 1451), 'EXPRESSWAY (WHISTLER)'),
    ((2417, 1448), 'EXPRESSWAY (WHISTLER)'),
    ((2474, 1479), 'LOWER OLYMPIC'),
    ((2458, 1557), 'LOWER OLYMPIC'),
    ((2595, 1500), 'CRABAPPLE'),
    # q_8.png, q_coyote.png, q_jgg_wide.png, q_ench.png: Ego Bowl's two lines beside their labels, Coyote's under its name, Green Acres' top under its name; Marmot and Whiskey Jack's lines into their symbols; Ptarmigan's into its symbol. r2/jgg2.png, r2/ef.png, r2/ef2.png: Jolly Green Giant's line from Green Acres under its name to Ego Bowl (as the resort's ArcGIS run lines draw it), the Enchanted Forest adventure trail's purple line from there to its name, and the blue line from Ego Bowl's label past Emerald Forest's symbol, where Emerald Forest's line joins it (the run polygons give both as Emerald Forest, the run the resort's report calls the Enchanted Forest entrances)
    ((2729, 782), 'EGO BOWL - UPPER'),
    ((2490, 954), 'EGO BOWL - LOWER'),
    ((2338, 898), 'COYOTE'),
    # r3/bob.png (the audit): the park's own line is orange, through its pill, from by Green Acres' symbol down to Bean
    # Sprout; the blue line under the park's label, from Green Acres' symbol to where Coyote's and Bobcat's lines part,
    # is Green Acres' (the resort's ArcGIS run lines have Coyote and Bobcat both start on Green Acres - Main)
    ((2506, 808), 'GREEN ACRES'),
    ((2531, 827), 'BOBCAT AND CHIPMUNK PARK'),
    ((2689, 675), 'GREEN ACRES'),
    ((2540, 749), 'MARMOT'),
    ((2750, 839), 'LOWER WHISKEY JACK'),
    ((2843, 802), 'UPPER WHISKEY JACK'),
    ((2621, 774), 'JOLLY GREEN GIANT'),
    ((2574, 889), 'EMERALD FOREST'),
    ((2564, 875), 'ENCHANTED FOREST'),
    ((2556, 982), 'PTARMIGAN'),
    # q_mcc.png, q_camel.png, q_gs.png, q_gs2.png, q_jgg_pdf.png, q_glades.png: McConkey's printed across its line, Low Roll's line either side of its name, Die Hard's into its symbol, the line between Harmony Horseshoes' end and Camel Humps' symbol (Camel Humps': the Symphony inset prints Camel Humps between the Horseshoes and the lift, and the resort's ArcGIS run lines have Camel Humps from Pika's Traverse down to Harmony Piste, as this line runs, while the Horseshoes are short chutes ending in their bowl), Harmony Piste's line on past its name and down to G.S., Cougar's past its name, Rabbit Tracks' under its name, Harmony Ridge's below its symbol, The Glades' either side of its name
    ((2714, 484), 'McCONKEY’S'),
    ((2638, 479), 'LOW ROLL'),
    ((2712, 542), 'LOW ROLL'),
    ((2686, 592), 'DIE HARD'),
    ((2873, 406), 'CAMEL HUMPS'),
    ((2764, 526), 'HARMONY PISTE'),
    ((2764, 712), 'COUGAR'),
    ((2626, 647), 'RABBIT TRACKS'),
    ((2290, 626), 'HARMONY RIDGE'),
    ((2274, 627), 'THE GLADES'),
    ((2173, 711), 'THE GLADES'),
    ((2416, 706), 'HARMONY PISTE'),
    # q_roundhouse.png, q_rh_51.png, q_pale.png: Little Whistler's line beside its name; T-Bar Run's line after its name; Pony Trail's from the Roundhouse into its name's end; Closed Captions printed on its line; Franz's Meadows' line along its name; Old Man's line through its symbol; Pika's Traverse to the Roundhouse
    ((3018, 370), 'LITTLE WHISTLER'),
    ((3095, 593), 'T-BAR RUN'),
    ((2981, 670), 'PONY TRAIL'),
    ((2908, 709), 'CLOSED CAPTIONS'),
    ((3199, 696), 'FRANZ’S MEADOWS'),
    ((3120, 763), 'OLD MAN'),
    ((2825, 574), 'PIKA’S TRAVERSE'),
    # q_peak.png, regions 2880_0, 3360_0, 3360_360: the Couloir's line below its symbols, Pika's Traverse up to Little Whistler, the lines in Whistler Bowl beside its name, Doom & Gloom's two lines either side of its name, Monday's and Cockalorum's lines into their symbols; the closed-area labels' leaders
    ((3282, 344), 'THE COULOIR'),
    ((2953, 358), 'PIKA’S TRAVERSE'),
    ((3531, 229), 'WHISTLER BOWL'),
    ((3471, 461), 'WHISTLER BOWL'),
    ((3423, 426), 'WHISTLER BOWL'),
    ((3572, 629), 'DOOM & GLOOM'),
    ((3524, 642), 'DOOM & GLOOM'),
    ((3741, 416), 'MONDAY’S'),
    ((3787, 402), 'COCKALORUM'),
    # the glades either side of their names (Outer Limits, Arthur's Choice, Log Jam) and lines running into names (Twist & Shout, Backstage Pass, Glacier Road)
    ((272, 830), 'OUTER LIMITS'),
    ((164, 962), 'OUTER LIMITS'),
    ((142, 975), 'OUTER LIMITS'),
    ((175, 1019), 'ARTHUR’S CHOICE'),
    ((319, 919), 'TWIST & SHOUT'),
    ((482, 1072), 'BACKSTAGE PASS'),
    ((409, 995), 'BACKSTAGE PASS'),
    ((405, 960), 'LOG JAM'),
    ((403, 884), 'LOG JAM'),
    ((635, 1375), 'GLACIER ROAD'),
    ((134, 915), 'GLACIER ROAD'),
]
UNNAMED = [
    # r2/loops.png, r2/cm_pdf.png: a purple family-area outline (now extracted whole: closed outlines used to collapse to a point)
    ((1008, 832), 'the outline of a family area round the Cougar Milk label, with no name on this map'),
    # r2/rh.png, gistopo.py: the green loop from the Roundhouse east and back to Pony Trail at Porcupine's symbol is
    # the resort's Peak Traverse (its ArcGIS run lines: from the Roundhouse back to Pony Trail - Upper; Porcupine
    # starts on Pony Trail), a name this map doesn't print
    ((3115, 668), 'a traverse from the Roundhouse back to Pony Trail, not named on this map (the resort calls it Peak Traverse)'),
    # r2/p68.png, r2/gjl.png, r2/base.png: Slingshot's line from its name's end; Gear Jammer - Lower's from its name's end down to the tube park; the two learning areas' outlines
    ((1643, 1800), 'the outline of the Snow School learning area at Base 2'),
    ((1776, 1955), 'the outline of the Snow School learning area at the Blackcomb base'),
    # r2/gl2.png, r2/gl_pdf.png, r2/jp2.png, r2/dl.png, r2/ss.png: Come-a-long's and Greenline's dashed lines either side of where they meet, and Greenline's on from its second label down to Mainline - Lower's symbol; Strawline's and Jackpot's either side of Jackpot's symbol; Download Road's round its label and down; Grub Stake's from its name's end; Catskinner Traverse's through its symbol; So Sweet's glade printed across by its name
    ((1188, 1187), 'a black line through the Gemini Freestyle Centre (a training area), with no run name'),
    ((1215, 1283), 'a black line through the Gemini Freestyle Centre (a training area), with no run name'),
    # r2/b2.png, r2/ret_pdf.png, r2/b3z.png, r2/ross.png, r2/cat.png, r2/lr.png, r2/lrw.png, r2/ren_pdf.png: Xhiggy's Meadow's line from its name's end; Everglades' glade below its name; Southside Green's dashed line on from its label to Expressway's symbol; the arrowed line into 7th Avenue's symbol; Ross' Gold's line from the lift into its symbol; the second line into Catskinner's symbol; the glades Bark Sandwich is printed beside and Where's Joe's and Raptor's Ride's from their names' ends; Magic Castle's family-area outline
    ((1393, 845), "a blue link from Easy Out's line, under Last Resort's label, with no name"),
    ((1464, 880), "a blue link from Easy Out's line, under Last Resort's label, with no name"),
    # r2/b1z.png, r2/b1w_pdf.png, r2/p178.png: 7th Avenue's green line on from its name's end to the 7th Heaven Express base; Hugh's Heaven's blue line from its name's end (behind Angel Dust's label) to the same base
    ((1401, 533), "a stub of black line between the Hugh's Heaven and Angel Dust labels, the rest hidden under them"),
    # r2/sep2.png, r2/p171.png, r2/p213.png, r2/p3.png: Seppo's black line from its diamond to the blue label, and Seppo's - Lower's blue line branching off it and printed across by its name; Bear Paw's line on down from its symbol; Stefan's Chute's line through its symbol beside its name; the Snow School learning area's outline
    ((3831, 1847), 'the outline of the Snow School learning area at Creekside'),
    # r2/a.png, r2/pony_pdf.png, r2/p301top_pdf.png, r2/lrr.png, r2/oly.png, r2/crab.png: Tree Fort's family-area outline round its name; Banana Peel's line from its name's end to the easiest way down; Little Red Run's from its name's end; Pony Trail's and Expressway's lines under their labels either side of Mid Station; Expressway's on west to Upper Olympic; the dashed branch and the solid line into Lower Olympic's symbol; the blue line from Expressway into Crabapple's
    ((2418, 1474), "the outline of the Children's Learning Centre"),
    ((2546, 1461), "a fragment of line hidden under the Children's Learning Centre label"),
    # q_mcc.png, q_camel.png, q_gs.png, q_gs2.png, q_jgg_pdf.png, q_glades.png: McConkey's printed across its line, Low Roll's line either side of its name, Die Hard's into its symbol, the line between Harmony Horseshoes' end and Camel Humps' symbol (Camel Humps'), Harmony Piste's line on past its name and down to G.S., Cougar's past its name, Rabbit Tracks' under its name, Harmony Ridge's below its symbol, The Glades' either side of its name
    ((2518, 481), 'a blue link from below the Symphony Express to Burnt Stew Trail, with no name'),
    # q_roundhouse.png, q_rh_51.png, q_pale.png: Little Whistler's line beside its name; T-Bar Run's line after its name; Pony Trail's from the Roundhouse into its name's end; Closed Captions printed on its line; Franz's Meadows' line along its name; Old Man's line through its symbol; Pika's Traverse to the Roundhouse
    ((3168, 737), 'the outline of the snowmaking reservoir'),
    # q_peak.png, regions 2880_0, 3360_0, 3360_360: the Couloir's line below its symbols, Pika's Traverse up to Little Whistler, the lines in Whistler Bowl beside its name, Doom & Gloom's two lines either side of its name, Monday's and Cockalorum's lines into their symbols; the closed-area labels' leaders
    ((3318, 167), 'a leader from the Permanently Closed Area label to its area'),
    ((3398, 166), 'a leader from the Permanently Closed Area label to its area'),
    ((3642, 261), 'a leader from the Permanently Closed Area label to its area'),
    ((3679, 276), 'a leader from the Permanently Closed Area label to its area'),
    # r3/pig.png (the audit), gisfit.py: the green line from the Emerald Express base west to Ego Bowl, under Ego Bowl
    # - Upper's label, drawn on from Upper Whiskey Jack's: the resort's Pig Alley (its ArcGIS run lines: Whiskey Jack -
    # Upper ends at the chair's base, where Pig Alley starts, on to Ego Bowl), a name this map doesn't print
    ((2785, 790), 'a link from the Emerald Express base to Ego Bowl, not named on this map (the resort calls it Pig Alley)'),
]
CUTS = [
    # r2/oe.png: Over Easy's green line from Easy Out, under its name and on down to Sunnyside Up: cut where Big Easy's
    # blue line joins it (the resort's ArcGIS run lines end Over Easy there and go on as Big Easy - Lower)
    ((1431, 993), (1515, 1028)),
    # r2/gl2.png: Come-a-long's dashed line from its name's end meets Greenline's (from the GREENLINE label), which
    # zigzags on down to its second label (GREEN LINE): cut where they meet
    ((962, 1133), (1081, 1163)),
    # r2/jp2.png: one blue line along Strawline's label, down past its symbol to Jackpot's symbol and under Jackpot's
    # name: cut at Jackpot's symbol
    ((1152, 1189), (1157, 1329)),
    # r2/emer.png: one green line into Burnt Stew Trail's symbol, under its name, on to Sidewinder's symbol and under
    # its name: cut where Marmot, Blue Road and Chunky's Choice end on it, where the resort's ArcGIS run lines start
    # Sidewinder (Marmot's end is Sidewinder's start there; Burnt Stew Trail ends higher, at Harmony Ridge)
    ((2152, 817), (2201, 872)),
    # r2/creek.png, r2/gg.png, r2/dmdl.png: one black line from Upper Dave Murray Downhill's name down to the
    # symbol of Dave Murray Downhill - Lower: cut where it crosses Expressway, at Mid Station's level (the resort
    # reports the upper part with Big Red's runs and the lower with Creekside's)
    ((3300, 1498), (3097, 1440)),
    # r2/p301.png, r2/mid_pdf.png: the easiest-way-down line from the top of the Garbanzo Express runs under Pony
    # Trail's second and third labels down to Mid Station, where it turns west as Expressway: cut at Mid Station
    ((3144, 1194), (3268, 1341)),
    # r2/oly.png: Expressway's dashed line on west to Upper Olympic's, and a dashed branch down toward Lower
    # Olympic's symbol: cut at the fork
    ((2417, 1448), (2486, 1447)),
    # q_rh_51.png: one green line from Pika's Traverse's symbol, past the Roundhouse, round to Porcupine's symbol:
    # Pika's Traverse ends at the Roundhouse
    ((2846, 586), (2887, 617)),
    # q_8.png: the green line beside Ego Bowl - Upper runs on past its symbol down beside Ego Bowl - Lower: cut
    # halfway between the two labels
    ((2642, 804), (2533, 863)),
    # q_coyote.png, q_jgg_wide.png: one blue line printed under Coyote, then under the Bobcat and Chipmunk Park pill,
    # then under Green Acres: cut where Bobcat's line joins it and at Green Acres' symbol
    ((2399, 854), (2441, 843)),
    ((2562, 780), (2590, 755)),
    # r3/pig.png: Upper Whiskey Jack's green line from the Roundhouse to the Emerald Express base turns west there to
    # Ego Bowl: cut at the turn
    ((2843, 766), (2829, 809)),
]
TRACED = [
]
