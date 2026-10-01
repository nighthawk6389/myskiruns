"""Vail's naming decisions, settled on zoomed review tiles and crops in October 2026 (the crop and tile names in
the comments are that session's scratch files; they were not kept). Every decision is a POINT on the map (panel
px), never a piece id: piece ids change whenever raster_lines.py is re-tuned, and common.resolve() finds the
current piece through the point. add.py records new decisions here.

CHECKED  {panel: [((x, y), NAME)]}  the piece through the point is that trail (overrides build.py's auto-match)
UNNAMED  {panel: [((x, y), why)]}   the piece is not a trail: icons, creek edges, the bus route, connectors the
                                    map prints no name for
CUTS     {panel: [((x, y) on the piece, (x, y) to cut at)]}  one drawn line carries two trails; the second part
                                    becomes a new piece (appended, so later ids stay put)
TRACED   {panel: [(NAME, [(x, y), ...])]}  stretches the detector missed (a name printed in the line, dashes
                                    through slow-zone hatching, a stub between a symbol and its parent line),
                                    snapped to the painted line with tools/trailmap/snap_trace.py; appended to
                                    linePolylines.json as pieces (listed in its _traced)
"""
CHECKED = {'front-side': [
    # r_fs_e0/e1, c_fs_gc1/gc2/gc4.png: Game Creek Bowl: Showboat, The Woods, Baccarat (its square is unlisted: the EXTRA label), Dealer's Choice, Ouzo, Ouzo Glade, Faro, Deuces Wild, Club Walk, Game Trail and Lost Boy resume past their printed names; two green lines leave the EAGLE'S NEST RIDGE label for Eagle's Nest (the lower one through an unnamed circle, #2) and merge; Bwana's blue line crosses under the Pride lift
    ((4376, 431), 'SHOWBOAT'),
    ((4552, 389), 'THE WOODS'),
    ((4764, 316), 'BACCARAT'),
    ((4544, 449), 'BACCARAT'),
    ((4620, 507), "DEALER'S CHOICE"),
    ((4596, 588), 'LOST BOY'),
    ((4357, 541), 'GAME TRAIL'),
    ((3989, 460), 'CLUB WALK'),
    ((4185, 391), 'OUZO'),
    ((4246, 329), 'FARO'),
    ((4312, 344), 'DEUCES WILD'),
    ((4034, 422), 'OUZO GLADE'),
    ((3970, 271), "EAGLE'S NEST RIDGE"),
    ((3710, 392), "EAGLE'S NEST RIDGE"),
    ((3909, 1428), 'BWANA'),
    ((4863, 1880), 'CASCADE WAY'),
    # r_fs_d0/d1, c_fs_gp2/gpb.png: Golden Peak: GS Alley, Fall Line, Golden Peak Race, Pony Express, Ruder's Run and Gopher Hill each resume past their printed names; Golden Peak Race runs on under the Riva Bahn label to the base; Ruder's Run's line above its square starts under lift 6; Riva Catwalk's blue line comes down from Riva Ridge's end through its square and on past Windisch Way to the base
    ((1113, 1705), 'GS ALLEY'),
    ((1163, 1788), 'FALL LINE'),
    ((1526, 1920), 'GOLDEN PEAK RACE'),
    ((2037, 2123), 'GOLDEN PEAK RACE'),
    ((1854, 1751), 'PONY EXPRESS'),
    ((1428, 1680), "RUDER'S RUN"),
    ((1922, 1919), "RUDER'S RUN"),
    ((2153, 2115), 'GOPHER HILL'),
    ((2350, 2120), 'RIVA CATWALK'),
    ((2179, 1754), 'RIVA CATWALK'),
    # r_fs_c4/c5/c6, c_fs_gs/vv/hf/38/ms/vc/vb/vu.png: Giant Steps, Lindsey's and Head First: each line runs to the top of its printed name, the symbol sits at the bottom of the name and the line resumes below (Head First's line starts below Giant Steps' label; its symbol #156 has no line below); the run beside Gondola One prints 38 above its diamond (#144) and starts where Mill Creek Road ends; Mudslide and Frontside Chutes have no lines; Gitalong Road switchbacks down past Bear Tree to its circles, loops west and back east to the Lionshead Catwalk junction, forks down to its lower circle and on to Vail Village Catwalk; Windisch Way runs west from that fork under the gondola; Bear Tree's blue line crosses the catwalks; Vail Village Catwalk comes from Bwana Loop's west end round its U-turn into Lionshead Catwalk and down from the junction to its lower circle; Bwana Loop comes down into Lionshead Catwalk; Born Free runs on under the lifts to the Lionshead base
    ((2705, 1591), 'GIANT STEPS'),
    ((2788, 1609), "LINDSEY'S"),
    ((2724, 1870), "LINDSEY'S"),
    ((2640, 1803), 'HEAD FIRST'),
    ((2641, 1866), 'HEAD FIRST'),
    ((2514, 2026), '38'),
    ((2506, 1902), '38'),
    ((2414, 1838), 'MILL CREEK ROAD'),
    ((2674, 1840), 'GITALONG ROAD'),
    ((2719, 1911), 'GITALONG ROAD'),
    ((3102, 1644), 'GITALONG ROAD'),
    ((3161, 1720), 'GITALONG ROAD'),
    ((2965, 2088), 'GITALONG ROAD'),
    ((2621, 1928), 'WINDISCH WAY'),
    ((2330, 2016), 'WINDISCH WAY'),
    ((3044, 1721), 'BEAR TREE'),
    ((3037, 1787), 'BEAR TREE'),
    ((3040, 2014), 'BEAR TREE'),
    ((2991, 1971), 'LIONSHEAD CATWALK'),
    ((3200, 2022), 'LIONSHEAD CATWALK'),
    ((3270, 2075), 'VAIL VILLAGE CATWALK'),
    ((3450, 2035), 'BWANA LOOP'),
    ((3480, 2078), 'LIONSHEAD CATWALK'),
    ((3317, 1906), 'VAIL VILLAGE CATWALK'),
    ((3996, 2024), 'BORN FREE'),
    ((4060, 2053), 'BORN FREE'),
    # r_fs_c0/c6, c_fs_ch/148/cr.png: Cheetah's line from Simba through its square and round its loop; Simba's line turns black through a diamond printed right under its SIMBA label (#141) and blue again to its lower square; Safari's line turns black above its SAFARI label and diamond (#153); the catwalk from Simba's line to lift 20's top turns back west as Post Road; the blue lines along Gore Creek are the creek's edge
    ((4347, 1336), 'POST ROAD'),
    ((4316, 1654), 'CHEETAH'),
    ((4383, 1718), 'SIMBA'),
    ((4226, 1954), 'SIMBA'),
    ((4222, 1757), 'SAFARI'),
    ((4263, 1888), 'SAFARI'),
    # r_fs_b6, c_fs_bf/bl/lh/121.png: Minnie's resumes below its label; Born Free's blue line turns green (no symbol) to its BORN FREE label and circle, crosses Bwana Loop, turns blue to its square and green again past its lower circle; Post Road's catwalk east from its circle; The Preserve's blue line crosses Bwana Loop and goes on as a black line through an unnamed diamond (#151); Bwana Loop runs east from its circle and loops back; Bwana's blue line crosses the Pride lift and Pride's line (which goes on through an unnamed square, #121) and comes down to its BWANA label and diamond; Safari resumes below its label
    ((3503, 1531), "MINNIE'S"),
    ((3561, 1568), 'BORN FREE'),
    ((3383, 1607), 'POST ROAD'),
    ((3600, 1604), 'POST ROAD'),
    ((4002, 1526), 'POST ROAD'),
    ((3710, 1745), 'THE PRESERVE'),
    ((3804, 1958), 'THE PRESERVE'),
    ((3840, 1846), 'BWANA LOOP'),
    ((3527, 1905), 'BORN FREE'),
    ((3856, 1684), 'BWANA'),
    ((3957, 1377), 'PRIDE'),
    ((4007, 1467), 'PRIDE'),
    ((4082, 1535), 'PRIDE'),
    ((4161, 1601), 'SAFARI'),
    # r_fs_b5, c_fs_net/cf/jn/pj/ck/en.png: Mid-Vail network: Upper Lion's Way runs from lift 1's top to its label; Pika's catwalk runs from lift 28's top past its label and circle down to Mid-Vail, ending where Upper Lion's Way's label ends; the lower catwalk from there through the slow zone has COLD FEET printed just above it (no symbol); the branch from Pika's line to Practice Parkway's lower circle; Cub's Way reaches lift 2's base, Lower Lion's Way leaves it for its circle; Avanti, Lodgepole Gulch, Columbine, Lodgepole and Berries resume past their labels; Cookshack's name is printed beside the diamond-topped line next to it (the diamond at the text's top has no line of its own); the short blue runs from Eagle's Nest Ridge to Pika's catwalk through unnamed squares (#58-60) and a short solid green link print no names
    ((2672, 1108), 'PIKA'),
    ((2870, 1048), 'PIKA'),
    ((2769, 1206), 'COLD FEET'),
    ((3057, 1095), 'PRACTICE PARKWAY'),
    ((3339, 1173), 'PRACTICE PARKWAY'),
    ((2780, 1463), "CUB'S WAY"),
    ((2890, 1473), "LOWER LION'S WAY"),
    ((3159, 1553), "LOWER LION'S WAY"),
    ((2748, 1237), 'AVANTI'),
    ((2693, 1297), 'AVANTI'),
    ((2734, 1431), 'LODGEPOLE GULCH'),
    ((2945, 1356), 'COLUMBINE'),
    ((2951, 1257), 'LODGEPOLE'),
    ((2916, 1221), 'BERRIES'),
    ((2806, 1138), 'COOKSHACK'),
    # r_fs_b4, c_fs_tt/ph.png: Trans Montane east of its circle; Riva Ridge crosses Trans Montane as a blue line (unnamed square) to Tourist Trap's pitch, then resumes below its RIVA RIDGE label with a blue square (#115); Skid Road's blue line runs east from its square to the Riva Ridge slope (Compromise's square is on the lower branch); Northface Catwalk's blue part to the Riva slope; Gitalong Road runs from its circle east under lift 1; Upper Lion's Way from lift 1's top; the line from Cady's Cafe's diamond goes on below a double diamond (no name printed by it); The Pump House's double diamond has no line
    ((1799, 1188), 'TRANS MONTANE'),
    ((1974, 1212), 'RIVA RIDGE'),
    ((2052, 1283), 'TOURIST TRAP'),
    ((2073, 1620), 'RIVA RIDGE'),
    ((1791, 1325), 'SKID ROAD'),
    ((1959, 1329), 'SKID ROAD'),
    ((1879, 1461), 'NORTHFACE CATWALK'),
    ((2159, 1185), 'GITALONG ROAD'),
    ((2481, 1241), 'GITALONG ROAD'),
    ((2373, 1112), "UPPER LION'S WAY"),
    ((2187, 1328), "CADY'S CAFE"),
    # r_fs_b3, c_fs_tm/kk/gp/67/bw.png: Pronto's top above its label; Prima's double-black line crosses Trans Montane and ends above the blue PRIMA square, whose line goes on down; Northstar's black line ends at a blue square (no name) and goes on blue to lift 11's base; Trans Montane runs west and loops back east as Northface Catwalk; Klickity Klack and Log Chute resume past their labels; Skid Road runs west from its circle to lift 10's base (Brisk Walk runs east from its own circle); the catwalk from lift 6's mid-station west to lift 10's base prints no name
    ((1373, 1103), 'PRONTO'),
    ((1363, 1303), 'PRIMA'),
    ((1353, 1234), 'TRANS MONTANE'),
    ((1096, 1312), 'NORTHFACE CATWALK'),
    ((1464, 1381), 'NORTHFACE CATWALK'),
    ((1008, 1301), 'KLICKITY KLACK'),
    ((947, 1454), 'LOG CHUTE'),
    ((818, 1303), 'CHOKER CUT OFF'),
    ((1042, 1472), 'SKID ROAD'),
    ((1118, 1505), 'BRISK WALK'),
    ((1590, 1540), 'BRISK WALK'),
    ((1126, 1120), 'NORTHSTAR'),
    # r_fs_b0/b1, c_fs_pp/pp2.png: Eagle's Nest beginner area: Practice Parkway's line through its upper circle up to lift 19 and down past its lower circle; Coyote Crossing's line through its circle west to the Pika junction; Cub's Way from lift 26 down to the westbound arrows; Pride, Bwana and Simba resume past their labels
    ((3323, 940), 'PIKA'),
    ((3447, 1026), 'PRACTICE PARKWAY'),
    ((3570, 991), 'PRACTICE PARKWAY'),
    ((3285, 1086), 'PRACTICE PARKWAY'),
    ((3554, 1261), 'PRACTICE PARKWAY'),
    ((3543, 1054), 'COYOTE CROSSING'),
    ((3373, 1117), 'COYOTE CROSSING'),
    ((3250, 1118), 'COYOTE CROSSING'),
    ((3635, 1147), "CUB'S WAY"),
    ((3487, 1320), "CUB'S WAY"),
    ((3261, 1356), "CUB'S WAY"),
    ((3900, 1292), 'PRIDE'),
    ((3990, 1266), 'BWANA'),
    ((4263, 1316), 'SIMBA'),
    # r_fs_3, c_fs_ww/en/mv/wr.png: Windows Road's second lane to Hunky Dory; Hunky Dory's top above its label; two green lines leave Wildwood's top for Eagle's Nest Ridge (the circle on the upper one prints no name and joins the ridge line); The Meadows runs past its label to the unnamed circle and on to lift 3's base; Overeasy and Avanti resume past their labels; Kangaroo Cornice has no line
    ((2483, 675), 'WINDOWS ROAD'),
    ((2660, 646), 'HUNKY DORY'),
    ((2794, 729), "EAGLE'S NEST RIDGE"),
    ((2848, 738), "EAGLE'S NEST RIDGE"),
    ((3063, 814), "EAGLE'S NEST RIDGE"),
    ((2511, 856), 'THE MEADOWS'),
    ((2398, 849), 'THE MEADOWS'),
    ((2212, 915), 'THE MEADOWS'),
    ((2629, 1031), 'OVEREASY'),
    ((2840, 1023), 'AVANTI'),
    # r_fs_2, c_fs_zot/sk/82/265.png: two blue lines from Mountaintop's top meet at Ramshorn's square (one crosses under the lift), and a branch splits off and rejoins below; Powerline Glade's line above its diamond; Zot, Whistle Pig, Slifer Express, Cappuccino, Christmas and Swingsville resume past their labels; Whistle Pig crosses under the lift; Riva Ridge's line above its label
    ((1862, 617), 'RAMSHORN'),
    ((1988, 661), 'RAMSHORN'),
    ((1967, 606), 'RAMSHORN'),
    ((2214, 793), 'RAMSHORN'),
    ((1957, 630), 'POWERLINE GLADE'),
    ((2029, 848), 'WHISTLE PIG'),
    ((2150, 907), 'WHISTLE PIG'),
    ((2014, 804), 'ZOT'),
    ((2054, 907), 'SLIFER EXPRESS'),
    ((2010, 934), 'CAPPUCCINO'),
    ((2046, 1023), 'CHRISTMAS'),
    ((1972, 965), 'SWINGSVILLE'),
    ((1657, 900), 'RIVA RIDGE'),
    # r_fs_0/1, c_fs_330/162/wj/fst/rim/106/hb.png: names resume past their labels (Tin Pants, Boomer, Flap Jack between its two circles, Blue Ox, Highline, Roger's Run); Highline starts at lift 10's top and crosses it; Whiskey Jack above its square and across lift 14; Timberline Catwalk on along the ridge to lift 11; Northwoods, Northstar, Prima Cornice and Prima print their names uphill of the symbol, their tops run on above the text; Gandy Dancer crosses the lift; Hairbag Alley's diamond is mid-line; First Step has no line
    ((296, 637), 'SILK ROAD'),
    ((662, 666), 'SOURDOUGH'),
    ((703, 827), 'TIN PANTS'),
    ((748, 804), 'BOOMER'),
    ((912, 879), 'FLAP JACK'),
    ((437, 1207), 'BLUE OX'),
    ((616, 1297), 'HIGHLINE'),
    ((816, 1082), "ROGER'S RUN"),
    ((369, 850), 'HIGHLINE'),
    ((858, 680), 'WHISKEY JACK'),
    ((899, 851), 'WHISKEY JACK'),
    ((1614, 565), 'TIMBERLINE CATWALK'),
    ((1194, 795), 'SNAG PARK'),
    ((1254, 759), 'SNAG PARK'),
    ((1419, 684), 'NORTHWOODS'),
    ((1471, 752), 'NORTHSTAR'),
    ((1392, 864), 'GANDY DANCER'),
    ((1504, 917), 'PRIMA CORNICE'),
    ((1609, 861), 'PRIMA'),
    ((972, 1092), 'HAIRBAG ALLEY'),
    ((1044, 972), 'HAIRBAG ALLEY'),
], 'back-bowls': [
    # r2_bb_0..7, c_bb_sd/su/sr2/tc/oe/bs1/bs3/top2/72/24/29/35.png: Sun Down Bowl's runs funnel into Sun Down Catwalk; Forever crosses the lift into it; Sun Up Catwalk and WFO run on to lift 5; Sleepytime Road east past its symbol; Tea Cup Glades' arrow to lift 36; Orient Express resumes below its label; Silk Road west from lift 21's top to Two Elk and along the bottom to lift 21's base; in the Blue Sky strip China Spur crosses its bridge down to Pete's Express, Cloud 9 runs from Pete's base to Skyline/Tea Cup, Kelly's Toll Road comes up to Skyline's base
    ((679, 1217), 'SUN DOWN CATWALK'),
    ((792, 1437), 'SUN DOWN CATWALK'),
    ((703, 1137), 'FOREVER'),
    ((1085, 1502), 'SUN UP CATWALK'),
    ((1210, 1516), 'WFO'),
    ((1325, 1282), 'CHICKEN YARD'),
    ((1857, 1221), 'SLEEPYTIME ROAD'),
    ((2203, 1299), 'SLEEPYTIME ROAD'),
    ((2754, 1268), 'SLEEPYTIME ROAD'),
    ((2302, 1506), 'TEA CUP GLADES'),
    ((3816, 1257), 'ORIENT EXPRESS'),
    ((3406, 1540), 'SILK ROAD'),
    ((3756, 1456), 'SILK ROAD'),
    ((3765, 1465), 'SILK ROAD'),
    ((3184, 1429), 'SILK ROAD'),
    ((2748, 467), 'SILK ROAD'),
    ((3014, 449), 'SILK ROAD'),
    ((3771, 1557), 'CHINA SPUR'),
    ((3709, 1678), 'CHINA SPUR'),
    ((3357, 1670), 'CLOUD 9'),
    ((2399, 1935), "KELLY'S TOLL ROAD"),
    # r_bb_1 (3800-4990 x 450-1150), f_bb_98.png: lines from Silk Road / lift 22 into Bolshoi Ballroom and the Mongolia bowls; runs resume below their labels
    ((4081, 566), 'BOLSHOI BALLROOM'),
    ((3918, 680), 'BOLSHOI BALLROOM'),
    ((4125, 1069), 'BOLSHOI BALLROOM'),
    ((4259, 575), 'INNER MONGOLIA BOWL'),
    ((4347, 612), 'INNER MONGOLIA BOWL'),
    ((4620, 641), 'OUTER MONGOLIA BOWL'),
    ((4015, 1016), 'GORKY PARK'),
    ((3961, 1130), "RASPUTIN'S REVENGE"),
    ((4287, 516), 'SILK ROAD'),
    # r_bb_3, f_bb_pf.png, f_bb_sg.png, f_bb_top.png, f_bb_34.png: Gillett's Dream and Poppyfields West merge into Poppyfields above its label; Poppyfields East and Gillett's Dream resume past their labels up to Silk Road / the top of Orient Express; Shangri-La crosses the lift down to Poppyfields
    ((2997, 701), "GILLETT'S DREAM"),
    ((2941, 765), 'POPPYFIELDS'),
    ((3486, 555), 'POPPYFIELDS EAST'),
    ((3250, 465), "GILLETT'S DREAM"),
    ((3115, 908), 'SHANGRI-LA'),
    ((3561, 608), 'SHANGRI-LA'),
    ((3578, 459), 'SILK ROAD'),
    ((3214, 421), 'SILK ROAD'),
    ((3880, 938), 'RED SQUARE'),
    # r_bb_2: each run's line resumes below its printed name; the Yonder runs' approach from the top of Sun Up Express (f_bb_l9.png)
    ((2786, 758), "DRAGON'S TEETH"),
    ((2736, 806), 'JADE GLADE'),
    ((2727, 1000), 'GENGHIS KHAN'),
    ((2709, 1068), 'SWEET N SOUR'),
    ((2384, 1090), "EMPEROR'S CHOICE"),
    ((2333, 1092), 'RED ZINGER'),
    ((2039, 724), 'OVER YONDER'),
    ((2059, 846), 'SLEEPYTIME ROAD'),
    ((1922, 594), 'YONDER GULLY'),
    ((1933, 654), 'YONDER'),
    # r_bb_0: Ptarmigan Ridge runs from Wildwood along the ridge, its label, symbol, then down the west side; Seldom
    # and Never leave it; each run's line resumes below its printed name. f_bb_ss2.png: Morning Side Ridge joins
    # Straight Shot beside Sun Down Express
    ((463, 548), 'PTARMIGAN RIDGE'),
    ((103, 964), 'PTARMIGAN RIDGE'),
    ((609, 812), 'MORNING SIDE RIDGE'),
    ((749, 847), 'WINDOWS'),
    ((917, 616), 'WINDOWS'),
    ((507, 954), 'SELDOM'),
    ((518, 1144), 'NEVER'),
    # r_bb_1: the line from the top of High Noon down Sun Up Bowl's ridge feeds Milt's Face, Campbell's, Cow's Face
    # and Chicken Yard and ends at Apres Vous; f_bb_1052.png: the line from the top of High Noon crosses the lift into
    # Forever's approach
    ((1486, 733), "MILT'S FACE"),
    ((1535, 841), "CAMPBELL'S"),
    ((1531, 1013), "COW'S FACE"),
    ((1443, 1146), 'APRES VOUS'),
    ((1216, 730), 'APRES VOUS'),
    ((1572, 762), 'THE SLOT'),
    ((1064, 573), 'WOW'),
    ((1046, 791), 'FOREVER'),
    ((1962, 549), 'SLEEPYTIME ROAD'),
    ((662, 909), 'STRAIGHT SHOT'),
    ((1179, 627), 'FOREVER'),
], 'blue-sky': [
    # c_bs_ul/c9/mid/mid2/ml/cs/sk/top/ur/b1/b2/br/pf/21.png, g_bs_*.png: Blue Sky: each run's line resumes past its printed name (Resolution, Hornsilver, Skree Field, Steep & Deep, Lover's Leap, Iron Mask, Little Ollie, Heavy Metal, Champagne Glade, In The Wuides, The Divide, Encore, Grand Review); The Star's line starts beside Grand Review's and runs on past the slow zone; Cloud 9 comes from lift 37's top to its square and down (and round its dashed loop) to Big Rock Park's square; Big Rock Park's line runs from its square to lift 39's base, where Cloud 9 resumes (its second square) on to Tea Cup & Skyline; China Spur runs from its square to the bridge; Silk Road comes from the bridge past its square to lift 21's base and over the creek; Sleepytime Road comes from under the Tea Cup lift past Marmot Valley's top (diamond #22) and its square to lift 21's base; Marmot Valley from #22 to its label and on to lift 36; Kelly's Toll Road from lift 38's base to Skyline's base; Poppyfields from the panel's edge to lift 21's base
    ((2502, 791), 'SKREE FIELD'),
    ((2847, 848), "LOVER'S LEAP"),
    ((3107, 736), 'CHAMPAGNE GLADE'),
    ((3146, 985), 'IN THE WUIDES'),
    ((3454, 1361), "CJ'S GLADE"),
    ((3502, 2426), 'THE DIVIDE'),
    ((3621, 2352), 'ENCORE'),
    ((2876, 1055), 'IRON MASK'),
    ((2152, 1480), 'IRON MASK'),
    ((2172, 1766), 'LITTLE OLLIE'),
    ((2296, 1974), 'HEAVY METAL'),
    ((1486, 1065), 'RESOLUTION'),
    ((1460, 1139), 'HORNSILVER'),
    ((938, 1010), 'GRAND REVIEW'),
    ((1469, 1746), 'GRAND REVIEW'),
    ((1157, 1264), 'THE STAR'),
    ((1453, 1439), 'THE STAR'),
    ((1609, 1609), 'THE STAR'),
    ((1844, 1761), 'THE STAR'),
    ((2509, 734), 'CLOUD 9'),
    ((1769, 1067), 'CLOUD 9'),
    ((1408, 1071), 'CLOUD 9'),
    ((1805, 1233), 'BIG ROCK PARK'),
    ((2054, 1642), 'BIG ROCK PARK'),
    ((2118, 2127), 'BIG ROCK PARK'),
    ((2546, 2599), 'CLOUD 9'),
    ((3315, 2759), 'CLOUD 9'),
    ((1150, 2125), 'CHINA SPUR'),
    ((971, 2240), 'CHINA SPUR'),
    ((1185, 2465), 'SILK ROAD'),
    ((2745, 2763), 'SILK ROAD'),
    ((2756, 2747), 'SILK ROAD'),
    ((2224, 2847), 'SILK ROAD'),
    ((2921, 2869), 'SLEEPYTIME ROAD'),
    ((2690, 2868), 'SLEEPYTIME ROAD'),
    ((2857, 3223), 'SLEEPYTIME ROAD'),
    ((2205, 3031), 'SLEEPYTIME ROAD'),
    ((3036, 2987), 'MARMOT VALLEY'),
    ((3196, 3039), 'MARMOT VALLEY'),
    ((3758, 3055), 'MARMOT VALLEY'),
    ((3793, 3014), 'MARMOT VALLEY'),
    ((4117, 1673), "KELLY'S TOLL ROAD"),
    ((4002, 2587), "KELLY'S TOLL ROAD"),
    ((120, 3219), 'POPPYFIELDS'),
    ((758, 3164), 'POPPYFIELDS'),
    ((1677, 3160), 'POPPYFIELDS'),
    ((2078, 3054), 'POPPYFIELDS'),
]}
UNNAMED = {'front-side': [
    ((3140, 130), 'sky at the top edge, not a line'),
    ((4391, 204), 'black line through an unnamed diamond (#8) beside the Game Creek lift, no name printed'),
    ((4405, 320), 'black line through an unnamed diamond (#8) beside the Game Creek lift, no name printed'),
    ((4600, 562), "short blue run through an unnamed square (#15) to lift 7's base"),
    ((4511, 584), "short blue run through an unnamed square (#15) to lift 7's base"),
    ((3587, 613), "Eagle's Nest services icon, not a line"),
    ((4968, 1801), "Gore Creek's edge, not a trail"),
    ((1731, 2354), "Gore Creek's edge, not a trail"),
    ((1979, 2424), "Gore Creek's edge, not a trail"),
    ((3085, 2323), "Gore Creek's edge, not a trail"),
    ((2421, 2439), "Gore Creek's edge, not a trail"),
    ((2549, 2447), "Gore Creek's edge, not a trail"),
    ((4070, 2213), "Gore Creek's edge, not a trail"),
    ((2789, 2431), 'in-town bus route, not a trail'),
    ((2959, 2438), 'in-town bus route, not a trail'),
    ((3048, 2423), 'in-town bus route, not a trail'),
    ((2252, 90), 'sky at the top edge, not a line'),
    ((1747, 91), 'sky at the top edge, not a line'),
    ((1855, 96), 'sky at the top edge, not a line'),
    ((2024, 104), 'sky at the top edge, not a line'),
    ((2245, 105), 'sky at the top edge, not a line'),
    ((2422, 124), 'sky at the top edge, not a line'),
    ((2449, 109), 'sky at the top edge, not a line'),
    ((2550, 121), 'sky at the top edge, not a line'),
    ((2574, 114), 'sky at the top edge, not a line'),
    ((2595, 121), 'sky at the top edge, not a line'),
    ((2667, 118), 'sky at the top edge, not a line'),
    ((2697, 119), 'sky at the top edge, not a line'),
    ((2728, 119), 'sky at the top edge, not a line'),
    ((2784, 132), 'sky at the top edge, not a line'),
    ((2756, 131), 'sky at the top edge, not a line'),
    ((2813, 131), 'sky at the top edge, not a line'),
    ((2912, 123), 'sky at the top edge, not a line'),
    ((2873, 130), 'sky at the top edge, not a line'),
    ((2926, 134), 'sky at the top edge, not a line'),
    ((2954, 152), 'sky at the top edge, not a line'),
    ((3100, 133), 'sky at the top edge, not a line'),
    ((3100, 154), 'sky at the top edge, not a line'),
    ((3478, 2366), 'in-town bus route, not a trail'),
    ((3241, 2390), 'in-town bus route, not a trail'),
    ((3200, 2265), "Gore Creek's edge, not a trail"),
    ((3277, 2271), "Gore Creek's edge, not a trail"),
    ((3475, 2324), "Gore Creek's edge, not a trail"),
    ((4807, 1978), "Gore Creek's edge, not a trail"),
    ((4642, 2059), "Gore Creek's edge, not a trail"),
    ((4451, 2096), "Gore Creek's edge, not a trail"),
    ((3790, 1742), "short green line from beside The Preserve's square down to Bwana Loop, no name"),
    ((4108, 1273), 'short black line through an unnamed diamond (#109) between Simba and Safari'),
    ((4111, 1354), 'short black line through an unnamed diamond (#109) between Simba and Safari'),
    ((3035, 1057), "short solid green link from Pika's catwalk to the Practice Parkway branch, no name"),
    ((2946, 909), "short blue run through an unnamed square (#58) from Eagle's Nest Ridge to Pika's catwalk"),
    ((2947, 1011), "short blue run through an unnamed square (#58) from Eagle's Nest Ridge to Pika's catwalk"),
    ((3103, 923), "short blue run through an unnamed square (#59) from Eagle's Nest Ridge to Pika's catwalk"),
    ((3052, 987), "short blue run through an unnamed square (#59) from Eagle's Nest Ridge to Pika's catwalk"),
    ((3170, 923), "short blue run through an unnamed square (#60) from Eagle's Nest Ridge to Pika's catwalk"),
    ((3124, 1056), "short blue run through an unnamed square (#60) from Eagle's Nest Ridge to Pika's catwalk"),
    ((2598, 1225), 'kids-zone icon, not a line'),
    ((2555, 1426), 'kids-zone icon, not a line'),
    ((2987, 1455), 'kids-zone icon, not a line'),
    ((3159, 1302), 'kids-zone icon, not a line'),
    ((1148, 1637), "catwalk from lift 6's mid-station unloading west to lift 10's base, no name printed"),
    ((1564, 1632), 'kids-zone icon, not a line'),
    ((3841, 948), 'kids-zone icon, not a line'),
    ((4039, 1183), 'kids-zone icon, not a line'),
    ((2553, 1066), 'Vail Sports icon, not a line'),
    ((3065, 857), 'kids-zone icon, not a line'),
    ((3225, 869), 'kids-zone icon, not a line'),
    ((3223, 988), 'kids-zone icon, not a line'),
    ((2082, 668), 'kids-zone icon, not a line'),
    ((568, 743), 'kids-zone icon, not a line'),
    ((1629, 570), "blue line from lift 11's top west along the ridge, no name printed"),
], 'back-bowls': [
    ((688, 489), 'dashed black ridge road west to Wildwood, no name printed'),
    ((1002, 471), 'dashed black ridge road west to Wildwood, no name printed'),
    ((3926, 1801), "Blue Sky strip: dashed road from Pete's Express to Belle's Camp, no name printed here"),
    ((4461, 1958), "Blue Sky strip: dashed road on past Belle's Camp, no name printed here"),
    ((1986, 585), 'shared approach to Yonder and Yonder Gully from the top of Sun Up Express'),
    ((1790, 965), 'connector from Sleepytime Road to the bottom of Sun Up Express (lift 9)'),
    ((2058, 546), 'shared approach to Yonder and Yonder Gully from the top of Sun Up Express'),
    ((606, 527), 'short line at the top of Sun Down Express, no name'),
], 'blue-sky': [
    ((120, 3219), "Poppyfields' line where it comes out from under the legend at the panel's corner (its stretch right of the legend carries the name; joining the two would draw across the legend)"),
    ((2982, 764), "shared approach from lift 38's top (In The Wuides, Lover's Leap, Iron Mask and the runs below branch off it)"),
    ((3062, 1034), "shared approach to CJ's Glade, The Divide and Encore"),
    ((3239, 1187), "shared approach to CJ's Glade, The Divide and Encore"),
    ((1922, 1929), "short blue line from under Pete's Express to the slow zone, no name printed"),
    ((1656, 1425), "dashed road from Big Rock Park's fork to China Spur's square, no name printed"),
    ((1523, 1966), "dashed road from Big Rock Park's fork to China Spur's square, no name printed"),
    ((1807, 2063), "road from China Spur's square to lift 39's base, printed 'to Tea Cup & Skyline Express' (a direction, not a name)"),
    ((1468, 2003), "road from China Spur's square to lift 39's base, printed 'to Tea Cup & Skyline Express' (a direction, not a name)"),
    ((1492, 2047), "road from China Spur's square to lift 39's base, printed 'to Tea Cup & Skyline Express' (a direction, not a name)"),
    ((1496, 2029), "road from China Spur's square to lift 39's base, printed 'to Tea Cup & Skyline Express' (a direction, not a name)"),
    ((3369, 3256), "black line from the panel's bottom edge into Marmot Valley's label, no name printed on this panel"),
    ((3217, 3300), "black line from the panel's bottom edge into Marmot Valley's label, no name printed on this panel"),
]}

CUTS = {'front-side': [
    ((2790, 1459), (2856, 1444)),  # c_fs_net/jn.png: Cub's Way reaches lift 2's base; Lower Lion's Way leaves that line here for its circle
    ((3300, 2068), (3338, 2047)),  # c_fs_vc.png: Lionshead Catwalk (shared with Vail Village Catwalk from its U-turn) turns down to Vail Village Catwalk's lower circle here
    ((3450, 2035), (3413, 2046)),  # c_fs_vc.png: Bwana Loop comes down into Lionshead Catwalk here
], 'back-bowls': [
    ((2995, 698), (2966, 722)),  # f_bb_pf.png: Gillett's Dream joins Poppyfields West's line, which goes on as Poppyfields
], 'blue-sky': [
    ((3062, 1034), (3003, 907)),  # c_bs_top.png: the line from lift 38's top comes out from under the lift here and splits: Iron Mask west, the shared approach to CJ's Glade / The Divide / Encore east
]}

TRACED = {'front-side': [
    # symbol_audit.py --mode ends, audit e1: stubs past a symbol or a name that no piece covered
    ('S. RIM', [(1596, 656), (1605, 643), (1625, 630), (1645, 616), (1654, 608), (1665, 596), (1663, 585)]),  # along its name, which runs uphill from its diamond, to the hook above
    ('SOURDOUGH', [(854, 763), (861, 767), (869, 776), (871, 783), (868, 790), (859, 810), (859, 821), (861, 831), (871, 839), (886, 842)]),  # past its name, under the LIFT label, to its end
    ('BRISK WALK', [(2096, 1719), (2108, 1713), (2121, 1710), (2138, 1707), (2148, 1703)]),  # from its circle to Mill Creek Road
    ('CASCADE WAY', [(4450, 1849), (4464, 1855), (4481, 1864), (4493, 1866), (4513, 1868)]),  # from its start arrow beside Simba to its square
    ('RIVA GLADE', [(1694, 915), (1705, 922), (1717, 931), (1722, 933)]),  # the stub above its diamond
    ("CADY'S CAFE", [(2236, 1103), (2237, 1115), (2238, 1130), (2239, 1138)]),  # from Gitalong Road down to its diamond
    ('S. LOOK MA', [(2327, 935), (2370, 900), (2414, 866), (2420, 862)]),  # audit lm: along its name, which runs uphill from its diamond, to the stub above it
    ('RIVA RIDGE', [(2068, 1400), (2055, 1450), (2040, 1500), (2035, 1517)]),  # audit z3: along its printed name below Tourist Trap's stub, to its square
    # symbol_audit.py --mode off, gg_sheet.png: from each symbol along its printed name to where its line resumes,
    # and the stubs above symbols (Cookshack's #80 has no line; Sleepytime Road's #49 is fixed in back-bowls)
    ('GAME TRAIL', [(3802, 518), (3892, 516)]),
    ('WINDOWS ROAD', [(2024, 606), (2164, 634)]),
    ('WINDOWS ROAD', [(2478, 649), (2540, 641), (2602, 636), (2622, 635)]),
    ('RIVA GLADE', [(1722, 933), (1799, 1018)]),
    ('LEDGES', [(3292, 902), (3293, 925), (3294, 950), (3292, 966), (3292, 974), (3244, 1082)]),
    ('PICKEROON', [(2937, 1056), (2930, 1081), (2894, 1182)]),
    ('BORN FREE', [(3560, 1022), (3565, 1045), (3572, 1072), (3600, 1170)]),
    ('BRISK WALK', [(997, 1510), (1028, 1511)]),
    ('OLD 9 LINE', [(3360, 1374), (3367, 1403), (3389, 1506)]),
    ('BRISK WALK', [(2096, 1719), (2080, 1736)]),
    ('POST ROAD', [(3155, 1633), (3187, 1627)]),
    ('CASCADE WAY', [(4513, 1868), (4529, 1875)]),
    ('HEAD FIRST', [(2617, 1957), (2582, 2054)]),
    ('WILDCARD', [(4498, 191), (4499, 201), (4496, 210)]),  # audit z9: the stub from Lost Boy's line to its diamond
    ("EAGLE'S NEST RIDGE", [(4237, 171), (4222, 174), (4210, 176), (4180, 182), (4150, 190), (4120, 197), (4095, 205), (4072, 213)]),  # audit z9: from Wildwood past its circle, along its printed name to where its line resumes
    ('VAIL VILLAGE CATWALK', [(3072, 1950), (3068, 1961), (3072, 1971), (3079, 1981), (3086, 1989), (3093, 1995), (3109, 1997), (3121, 2003), (3140, 2009), (3157, 2014), (3176, 2019), (3194, 2022), (3212, 2024), (3234, 2027), (3253, 2030), (3272, 2033), (3292, 2036), (3311, 2039), (3324, 2039), (3338, 2047)]),  # c_fs_vc.png, audit z7: round its U-turn and along the stretch it shares with Lionshead Catwalk to where it turns back west
    ('HEAD FIRST', [(2637, 1882), (2632, 1904), (2627, 1922), (2622, 1940), (2617, 1957)]),  # audit z6: below Gitalong Road and Windisch Way, down to its name
    ("CUB'S WAY", [(3656, 955), (3639, 970), (3640, 988), (3663, 997), (3675, 999), (3696, 1001), (3712, 1003), (3730, 1004)]),  # audit z2: the dashed loop from lift 26's top round to its circle
    ('THE SKIPPER', [(2348, 680), (2344, 694), (2342, 705)]),  # audit z1: the stub above its name
    ('TOURIST TRAP', [(2072, 1371), (2069, 1384), (2067, 1394)]),  # audit z3: the stub below its diamond, above Riva Ridge's name
    ('LEDGES', [(3243, 1170), (3237, 1187), (3229, 1206), (3222, 1225), (3219, 1241), (3223, 1262), (3229, 1282), (3235, 1301), (3240, 1319), (3246, 1337)]),  # g_fs_86.png, s_led.png: the dashed green middle through its circle
    ('COMPROMISE', [(1940, 1333), (1974, 1358), (2020, 1396)]),  # c_fs_cp.png: the dashed branch from Skid Road through its square
    ("BEN'S FACE", [(2407, 1130), (2416, 1158), (2422, 1222)]),  # c_fs_bf2.png: short line above its square, resumes below its name
    ('CHAOS CANYON', [(2560, 1197), (2500, 1207), (2468, 1220)]),  # c_fs_bf2.png: resumes below its name
    ('SPRUCE FACE', [(2370, 1119), (2353, 1150)]),  # c_fs_bf2.png: short line above its square
], 'back-bowls': [
    # g_bb_st1/st2.png, s_bb_*.png: the Blue Sky roads along this panel's bottom edge, where the dashes run through
    # slow-zone hatching: Cloud 9 on past the bridge to Tea Cup & Skyline, Sleepytime Road down to lift 21, Kelly's Toll Road up to Skyline
    ('CLOUD 9', [(3180, 1653), (3150, 1649), (3118, 1641), (3084, 1631), (3058, 1613), (3033, 1593), (3015, 1577), (3012, 1564), (2978, 1564), (2941, 1563), (2908, 1562), (2871, 1565), (2833, 1574), (2801, 1582), (2764, 1590), (2730, 1601), (2689, 1615), (2660, 1609)]),
    ('SLEEPYTIME ROAD', [(2919, 1247), (2928, 1259), (2937, 1275), (2948, 1307), (2961, 1337), (2974, 1366), (2985, 1381), (2995, 1390), (3011, 1402), (3027, 1417)]),
    ("KELLY'S TOLL ROAD", [(2493, 1921), (2520, 1906), (2548, 1884), (2570, 1863), (2588, 1828), (2604, 1795), (2623, 1770), (2634, 1751), (2636, 1718), (2633, 1699), (2641, 1667), (2645, 1657)]),
    ('SILK ROAD', [(3693, 536), (3712, 544), (3729, 550), (3740, 555), (3758, 562), (3775, 569), (3786, 574)]),  # audit bb r03: from its square to the Mongolia lift's base
    # symbol_audit.py --mode off, gg_sheet.png: from each symbol along its printed name to where its line resumes,
    # and the stubs from the parent line to the symbol
    ('STRAIGHT SHOT', [(664, 592), (652, 841)]),
    ('HEADWALL', [(1628, 558), (1653, 719)]),
    ('SILK ROAD', [(3693, 536), (3668, 525)]),
    ("WIDGE'S", [(236, 656), (262, 688), (377, 762)]),
    ("RICKY'S RIDGE", [(352, 601), (375, 629), (468, 720)]),
    ('MORNING SIDE RIDGE', [(487, 565), (499, 601), (573, 756)]),
    ('MORNING THUNDER', [(2057, 997), (2197, 1089)]),
    ('O.S.', [(296, 1137), (380, 1148)]),
    ('SLEEPYTIME ROAD', [(2275, 1317), (2293, 1316), (2309, 1310), (2323, 1300), (2330, 1278), (2329, 1264), (2325, 1246), (2325, 1227), (2333, 1213), (2345, 1206), (2350, 1203)]),  # through its square
    ('MARMOT VALLEY', [(2444, 1241), (2503, 1382)]),
    ('POPPYFIELDS WEST', [(2698, 514), (2712, 522), (2729, 531), (2746, 541), (2830, 588), (2912, 634)]),  # audit bb r02, g_bb_pw.png: its line from below Wapiti, then its name, to its square
], 'blue-sky': [
    ('HORNSILVER', [(647, 671), (662, 676), (680, 681), (700, 688), (719, 694), (729, 698), (765, 712), (799, 725)]),  # audit bs r00: from beside Grand Review under Pete's Express to its diamond
    ('CHAMPAGNE GLADE', [(3245, 788), (3643, 961)]),  # audit bs r02: along its printed name to its diamond
    ('IN THE WUIDES', [(3322, 1138), (3700, 1387)]),  # g_bs_all.png: along its printed name to its square
    ('CHINA SPUR', [(1346, 2022), (1331, 2030), (1315, 2033), (1297, 2038), (1280, 2045), (1264, 2052), (1247, 2060), (1234, 2066), (1221, 2073), (1208, 2079), (1188, 2090), (1173, 2099), (1160, 2107), (1144, 2120), (1126, 2132), (1108, 2138)]),  # s_cs.png: the dashes from its square under 'to CHINA BOWL'
    ('MARMOT VALLEY', [(3385, 3203), (3476, 3229)]),  # through the arrowhead to its diamond
    ('CLOUD 9', [(2204, 777), (2183, 787), (2158, 797), (2136, 802), (2109, 806), (2087, 809), (2060, 810), (2037, 814), (2010, 817), (1988, 822), (1972, 826), (1950, 833), (1921, 845), (1894, 857), (1869, 871), (1851, 883), (1825, 900), (1805, 908)]),  # g_bs_c9.png: the road from lift 37's top on to its square
    ('CLOUD 9', [(2809, 2702), (2845, 2698), (2879, 2698), (2910, 2691), (2941, 2690)]),  # c_bs_b1.png: past the junction with Silk Road
    ('GRAND REVIEW', [(1020, 1100), (1036, 1128), (1047, 1158), (1050, 1192), (1047, 1210), (1044, 1245), (1053, 1276), (1062, 1299)]),  # g_bs_gr.png: beside the lift label
    ('THE STAR', [(1063, 1176), (1079, 1205), (1089, 1219), (1109, 1240)]),  # g_bs_gr.png: its line starts beside Grand Review's
    ('RESOLUTION', [(1301, 743), (1350, 740), (1400, 737), (1449, 735), (1482, 733), (1499, 736), (1515, 745), (1526, 760)]),  # g_bs_res.png: resumes past its label
    ('STEEP & DEEP', [(2747, 722), (2768, 674)]),  # g_bs_sd.png: the stub past its label
    ('KELLY\'S TOLL ROAD', [(3941, 2599), (3919, 2621), (3887, 2640), (3855, 2658), (3829, 2672), (3800, 2690), (3770, 2709), (3739, 2720), (3704, 2726), (3689, 2731)]),  # g_bs_kt.png: on to Skyline's base
    ('SLEEPYTIME ROAD', [(2839, 3264), (2840, 3248), (2840, 3228)]),  # g_bs_sr.png: from under the Tea Cup lift
    ('SLEEPYTIME ROAD', [(2868, 3147), (2887, 3112), (2903, 3085), (2920, 3061), (2943, 3028), (2953, 3011), (2981, 2991), (3005, 2975), (3012, 2971)]),
    ('SLEEPYTIME ROAD', [(2647, 2877), (2665, 2876), (2684, 2867), (2700, 2860), (2716, 2855), (2740, 2852)]),  # g_bs_21.png
    ('SLEEPYTIME ROAD', [(2630, 2883), (2608, 2897), (2579, 2914), (2550, 2934), (2525, 2954), (2502, 2975), (2483, 2996), (2468, 3013), (2446, 3041), (2424, 3061), (2410, 3072)]),
    ('SLEEPYTIME ROAD', [(2400, 3090), (2387, 3100), (2375, 3112), (2359, 3126)]),
    ('SLEEPYTIME ROAD', [(2149, 3106), (2162, 3089), (2173, 3074), (2189, 3048), (2196, 3035), (2215, 3010)]),
    ('MARMOT VALLEY', [(3266, 3094), (3293, 3113), (3318, 3140), (3340, 3163), (3369, 3182), (3385, 3203)]),  # c_bs_b2.png: down to the arrow at its label
]}
