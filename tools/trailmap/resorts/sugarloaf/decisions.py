"""Sugarloaf's naming decisions, settled on zoomed crops (grid_crop.py over work/sugarloaf/map.png with the pieces
tagged id:name). Every decision is a POINT in map px (work/sugarloaf/map.png, 3825x2388), so it survives a
re-extraction: pdf_resort.py finds the piece through it. `pdf_resort.py sugarloaf add` records new ones.

CHECKED  [((x, y), NAME)]   the piece through the point is that trail (overrides the auto-match)
UNNAMED  [((x, y), why)]    the piece is not a trail
CUTS     [((x, y) on the piece, (x, y) to cut at)]  one drawn line carries two trails; the second part becomes a
                            new piece (appended, so the other ids stay put)
TRACED   [(NAME, [(x, y), ...])]  a stretch with no drawn line of its own (the Snowfields inset is a raster)
"""
CHECKED = [
    # p_sb.png (2270,690 z2.4): circle 31 sits on the black line above the SHEER BOOM label (the label names the stretch below it)
    ((2371, 804), 'UPPER SHEER BOOM'),
    # sl_west.png (0,250 z0.75): the orange dashed line (the legend's GOLDEN ROAD) along the top of Brackett Basin, circle 55 beside it
    ((1302, 416), 'GOLDEN ROAD'),
    # p_b4 (3550,1740 z2.2): L. West Mountain's green line past lift L's bottom terminal
    ((3667, 1850), 'L. WEST MOUNTAIN'),
    # p_b5 (700,1330 z1.6): the blue dashed lines between the log yards and from the lower yard east: the legend's LOGGING ROAD (key 66); 245 had taken L. Stub's Trail from the circle where it ends
    ((1010, 1667), 'LOGGING ROAD'),
    ((824, 1497), 'LOGGING ROAD'),
    # p_b3 (2330,1430 z3): the green line below L. GLANCER's circle, down to the CONDO ACCESS ONLY label
    ((2406, 1489), 'L. GLANCER'),
    # p_b2 (1900,2080 z2): Snowbrook's green line on from its label round to lift G's base and the short curl past it
    ((2035, 2156), 'SNOWBROOK'),
    ((2054, 2273), 'SNOWBROOK'),
    ((2104, 2296), 'SNOWBROOK'),
    # p_w4 (1420,580 z2): the black lines below RIPSAW's double diamond and below HAUL BACK's diamond, down beside lift D
    ((1548, 719), 'RIPSAW'),
    ((1652, 707), 'HAUL BACK'),
    # p_w2: the green line from that junction down to L. BUCKBOARD's circle
    ((1402, 1331), 'L. BUCKBOARD'),
    ((1382, 1414), 'L. BUCKBOARD'),
    # p_w1, p_w2 (1100,1250 z1.5): U. Buckboard's blue line below the Condo X-Cut, down to the junction with Cross Haul
    ((1507, 1203), 'U. BUCKBOARD'),
    # p_w3, p_w2: the green line from U. STUB'S TRAIL's circle down to L. Stub's Trail's circle, where the lower trail starts
    ((1086, 1264), 'U. STUB’S TRAIL'),
    # p_w3: the green line from Stub's Trail down across the Condo X-Cut to CROSS HAUL's circle
    ((1273, 1092), 'CROSS HAUL'),
    ((1272, 1157), 'CROSS HAUL'),
    # p_w3: the green line west of CONDO X-CUT's circle, to Stub's Trail
    ((1233, 1141), 'CONDO X-CUT'),
    # p_w1 (1300,940 z1.8), p_w3 (1100,960 z2): Moose Alley's blue line from beside the U. CRUISER label west to its square
    ((1636, 979), 'MOOSE ALLEY'),
    # p_b1: the dashed green line from the base past lift N round to NATALIE'S BIRCHES' circle
    ((1588, 1634), 'NATALIE’S BIRCHES'),
    ((1581, 1711), 'NATALIE’S BIRCHES'),
    ((1652, 1777), 'NATALIE’S BIRCHES'),
    # p1, p_b1 (1500,1560 z2.2): L. Pole Line's green line below its circle, down to the base
    ((1591, 1493), 'L. POLE LINE'),
    # p_l2: Haywire's blue line past its square at (2194,1343), to the foot of Candy Side
    ((2151, 1362), 'HAYWIRE'),
    # p_l2 (1950,1300 z1.5): the long green line from L. TOTE ROAD's circle west to the base
    ((2070, 1442), 'L. TOTE ROAD'),
    # sl_base1.png (PDF 7x at 712,545 pt): Boardwalk's line crosses the lift line and curves left as this piece, down to the base
    ((1751, 1488), 'BOARDWALK'),
    # p_l1 (1800,1170 z2): the green lines below the circles of L. WINTER'S WAY, BOARDWALK and L. NARROW GAUGE, and the black line below DROP LINE's double diamond and SIDEWINDER's diamond
    ((1845, 1360), 'L. WINTER’S WAY'),
    ((1895, 1360), 'BOARDWALK'),
    ((1968, 1336), 'L. NARROW GAUGE'),
    ((1858, 1239), 'DROP LINE'),
    ((2039, 1280), 'SIDEWINDER'),
    # p_e4: the blue line below U. GLANCER's square, down to Horseshoe
    ((2826, 1124), 'U. GLANCER'),
    # p_e4 (2540,1060 z2): the green line below M. SCOOT's circle
    ((2579, 1197), 'M. SCOOT'),
    # sl_spur.png (PDF 7x at 1040,320 pt): the blue line from Double Bitter east to SPURLINE's square, and the short wavy stub from the square under the label
    ((2674, 876), 'SPURLINE'),
    ((2772, 878), 'SPURLINE'),
    # p_e1: below KING'S LANDING's square
    ((2524, 935), 'KING’S LANDING'),
    # p_e1 (2500,830 z2.2), sl_spur.png: the blue line below Double Bitter's black line, through the square, on to L. Double Bitter's piece
    ((2618, 907), 'L. DOUBLE BITTER'),
    ((2577, 955), 'L. DOUBLE BITTER'),
    # p_e2 (2830,780 z2.2): the blue line from the lift top down to the GOOD CHANCE X-CUT label, where U. Glancer's piece carries on below it
    ((2965, 972), 'U. GLANCER'),
    # p_e3 (2940,820 z1.8), sl_bucksaw.png: the green line from Windrow Ext. past the Bucksaw lift top (under the slow-zone band) round to the smiley and on into HORSESHOE's label: the horseshoe
    ((3118, 951), 'HORSESHOE'),
    # sl_bucksaw.png (PDF 7x at 1128,325 pt): U. Scoot's blue line runs up past circle 35 across both green lines; 97 had taken WINDROW EXT. from the circle
    ((2923, 866), 'U. SCOOT'),
    ((2893, 887), 'U. SCOOT'),
    # p_m6: the blue line below L. COMP HILL's square down to the green traverse
    ((2221, 990), 'L. COMP HILL'),
    # p_m6: the blue line from the Spillway west of circle 47
    ((2227, 818), 'TOTE ROAD X-CUT'),
    # sl_f.png (PDF 7x at 800,340 pt): Lower Spillway's line resumes past lift F's bottom terminal, in line with its upper part, down to the lodge
    ((2079, 1009), 'LOWER SPILLWAY'),
    # p_m6 (2060,780 z2.5): the blue line through circle 46 below Upper Spillway's black line: the short link from Sluice to its top, and on below its square
    ((2162, 806), 'LOWER SPILLWAY'),
    ((2138, 902), 'LOWER SPILLWAY'),
    # sl_jill.png (PDF 7x at 684,290 pt): the blue line below JILL POKE's square, down to the S/M pill where U. Cruiser's line starts
    ((1745, 838), 'JILL POKE'),
    # p_m5 (1700,600 z2.3): the dashed black line below MISERY WHIP's double diamond
    ((1872, 691), 'MISERY WHIP'),
    # sl_gl.png (PDF 8x at 822,238 pt): the black line below U. GONDOLA LINE's double diamond, down to the Mid Station X-Cut
    ((2146, 629), 'U. GONDOLA LINE'),
    # p_m1 (1940,560 z2.4): the dashed blue line through circle 29, east to the lift and west to Ramdown's line
    ((1977, 638), 'MID STATION X-CUT'),
    ((2095, 637), 'MID STATION X-CUT'),
    ((2125, 639), 'MID STATION X-CUT'),
    ((2161, 648), 'MID STATION X-CUT'),
    ((2202, 651), 'MID STATION X-CUT'),
    # sl_boom.png (PDF 8x at 755,225 pt), ends_0.png: the blue line below RAMDOWN's square, down to Lombard X-Cut's
    # square (the Mid Station X-Cut joins it from the right); the short black line below U. BOOMAUGER's diamond, down to
    # the square on the X-Cut where the L. BOOMAUGER label starts
    ((1905, 698), 'RAMDOWN'),
    ((1990, 624), 'U. BOOMAUGER'),
    # sl_oww.png (PDF 8x at 796,188 pt): the blue line that comes out from under the U. BOOMAUGER label below Old Winter's Way's square and runs down to L. Bubblecuffer
    ((2072, 612), 'OLD WINTER’S WAY'),
    # p_s11 (2680,560 z2.2): the blue line west of BRIDLE CHAIN's square, across U. Binder
    ((2688, 610), 'BRIDLE CHAIN'),
    # sl_cinder.png: the blue arc from the end of Binder Ext. to BUCKSKIN's square
    ((2560, 427), 'BUCKSKIN'),
    # sl_cinder.png, p_s10: the long blue line that carries on from Tote Road Ext. down to Pick Pole (Tote Road shares Pick Pole's line from there to its square: TRACED)
    ((2587, 545), 'TOTE ROAD'),
    # sl_cinder.png (PDF at 9x, 970,150 pt): Cinder Hoe's line ends on a wavy blue line that runs right from the end of Tote Road Ext. and down into the trees, where it stops
    ((2501, 426), 'CINDER HOE'),
    ((2550, 458), 'CINDER HOE'),
    # p_s8: the blue lines above the TOTE ROAD EXT. and CINDER HOE squares
    ((2325, 304), 'TOTE ROAD EXT.'),
    ((2360, 308), 'CINDER HOE'),
    # p_s8 (2300,250 z2.2): the green line from the lift top to U. TIMBERLINE's circle and label
    ((2420, 285), 'U. TIMBERLINE'),
    # p_s5, p_s7: the black line from U. Double Bitter down-left across Pick Pole into U. SKIDDER
    ((2525, 579), 'U. SKIDDER'),
    # p_s6 (2560,480 z2.2): the black line from Gin Pole down across Pick Pole into HAYBURNER
    ((2574, 603), 'HAYBURNER'),
    # p_s5, p_s6: the blue arc from circle 21 east to the square where PINCH (circle 24) starts
    ((2510, 552), 'GIN POLE'),
    ((2552, 577), 'GIN POLE'),
    # p_s5, p_s7 (2380,500 z3.5): the blue line from Sluice Headwall east across the lift to the square and circle 23, and on east past circle 24
    ((2397, 578), 'PICK POLE'),
    ((2461, 599), 'PICK POLE'),
    ((2724, 662), 'PICK POLE'),
    # p_s3, p_s7: the black line from Narrow Gauge Ext. (under the end of the TOTE ROAD EXT. label) down to U. NARROW GAUGE's piece
    ((2458, 506), 'U. NARROW GAUGE'),
    # p_s3 (2280,400 z3): the black line with a diamond just left of circle 18
    ((2328, 476), 'SLUICE CHUTE'),
    # p_s2 (1880,400 z3): the black line from the lift top east to the SPILLWAY X-CUT diamond, where Pure Heat and Jagger end
    ((2009, 432), 'SPILLWAY X-CUT'),
    # p1 (1480,1060 z2): the green line from the traverse down past the circle at (1670,1183) and across the lift into L. WHIFFLETREE's label, and on below its circle
    ((1679, 1160), 'L. WHIFFLETREE'),
    ((1553, 1437), 'L. WHIFFLETREE'),
]
UNNAMED = [
    # p_w2: two short green links from L. Buckboard across to The Yard; no name printed
    ((1429, 1381), 'short green link from Lower Buckboard to The Yard; no name printed'),
    ((1438, 1526), 'short green link from Lower Buckboard to The Yard; no name printed'),
    # p_l2, p_l3: a green run-out from the foot of Candy Side and Haywire (a green circle on it) down to lift B's base; no name printed
    ((2046, 1398), "green run-out from the foot of Candy Side and Haywire to lift B's base; no name printed"),
    ((1912, 1512), "green run-out from the foot of Candy Side and Haywire to lift B's base; no name printed"),
    # p_m7 (1990,960 z2.2): a green traverse from the top of L. Sheer Boom to where M. Narrow Gauge ends and L. Narrow Gauge starts; no name printed
    ((2195, 1015), 'green traverse from the top of Lower Sheer Boom to the foot of Middle Narrow Gauge; no name printed'),
    # sl_rookie.png (PDF 5x at 660,350 pt): the green traverse from the Whiffletree lift line east to the phone at the foot of Lombard X-Cut; no name printed (circles 42 and 43 are in the trees above and below it)
    ((1856, 1053), 'green traverse from the Whiffletree lift line to the phone at the foot of Lombard X-Cut; no name printed'),
    # sl_jill.png: a short blue link from the lift line to the square on Whiffletree's line
    ((1786, 838), 'short blue link from the Whiffletree lift line to the square on Upper Whiffletree; no name printed'),
    # sl_gl.png: a blue line from the Mid Station X-Cut at the Wild Things triangle, across the top of the GONDOLA LINE label, down to Sluice; no name printed on it
    ((2098, 694), 'blue link from the Mid Station X-Cut across the top of the GONDOLA LINE label down to Sluice; no name printed'),
    ((2119, 779), 'blue link from the Mid Station X-Cut across the top of the GONDOLA LINE label down to Sluice; no name printed'),
]
CUTS = []
TRACED = [
    # sl_inset_w.png, sl_inset_e.png (3180,130 and 3480,130 z2.2): the Snowfields inset, a raster: each run from its
    # rough points snapped onto the black line (snap_trace.py --rgb 20,20,25 --tol 45 --r 6), through its label.
    # High Rigger runs from the summit along the ridge round the shoulder to the dashes above Hard Tack's symbol
    # (as the main map splits them at circles 1 and 2)
    ('HIGH RIGGER', [(3498, 155), (3480, 166), (3464, 176), (3448, 185), (3433, 194), (3419, 203), (3403, 213),
        (3386, 222), (3372, 231), (3360, 237), (3344, 246), (3329, 255), (3315, 263), (3301, 271), (3287, 280),
        (3272, 289), (3258, 299), (3243, 314), (3232, 331), (3227, 342)]),
    ('HARD TACK', [(3225, 346), (3220, 360), (3218, 377), (3220, 394), (3222, 413), (3227, 428), (3233, 443),
        (3241, 459), (3249, 472), (3253, 487), (3257, 504), (3260, 522), (3269, 540), (3280, 554), (3287, 560)]),
    ('PURE HEAT', [(3323, 272), (3318, 288), (3320, 302), (3320, 317), (3317, 336), (3314, 352), (3311, 368),
        (3301, 389), (3296, 408), (3296, 425), (3288, 444), (3278, 459), (3268, 473), (3264, 480)]),
    ('JAGGER', [(3395, 258), (3393, 273), (3387, 293), (3379, 308), (3371, 322), (3364, 337), (3358, 356),
        (3355, 375), (3354, 393), (3353, 412), (3354, 436), (3359, 453), (3369, 470), (3376, 489), (3375, 507),
        (3379, 526), (3386, 543)]),
    ('IGNITOR', [(3525, 184), (3522, 198), (3519, 213), (3515, 230), (3512, 248), (3512, 266), (3508, 286),
        (3503, 303), (3498, 320), (3495, 339), (3497, 358), (3498, 376), (3499, 392), (3495, 413), (3493, 429),
        (3491, 446), (3490, 464), (3490, 485), (3493, 503), (3496, 511)]),
    ('POWDER KEG', [(3593, 203), (3579, 210), (3575, 227), (3577, 244), (3581, 265), (3578, 282), (3567, 295),
        (3554, 307), (3551, 325), (3554, 343), (3560, 360), (3569, 374), (3578, 389), (3587, 407), (3589, 423),
        (3587, 439), (3585, 457), (3584, 477), (3582, 490)]),
    ('WHITE NITRO EXT.', [(3661, 186), (3646, 192), (3630, 198), (3617, 211), (3612, 232), (3610, 253), (3612, 272),
        (3619, 290), (3625, 308), (3631, 323), (3638, 341), (3643, 354), (3648, 368), (3654, 385), (3659, 400),
        (3663, 421), (3666, 441)]),
    ('BUBBLECUFFER EXT.', [(3694, 217), (3695, 231), (3696, 249), (3698, 269), (3702, 287), (3706, 306), (3711, 321),
        (3718, 337), (3725, 350), (3731, 364), (3736, 383), (3739, 402), (3740, 413)]),
    ('GONDOLA LINE EXT.', [(3671, 171), (3683, 180), (3696, 190), (3707, 203), (3717, 219), (3728, 233), (3736, 246),
        (3744, 261), (3753, 276), (3762, 291), (3770, 306), (3777, 320), (3783, 334), (3789, 348)]),
    ('SPILLWAY X-CUT', [(3794, 382), (3783, 391), (3770, 402), (3758, 413), (3744, 423), (3732, 433), (3718, 442),
        (3703, 450), (3689, 457), (3677, 462), (3658, 468), (3645, 472), (3626, 478), (3610, 484), (3594, 489),
        (3577, 495), (3555, 503), (3539, 507), (3523, 512), (3507, 517), (3489, 525), (3473, 533), (3453, 534),
        (3438, 543), (3419, 547), (3402, 547), (3384, 544), (3366, 548), (3348, 552), (3332, 560), (3312, 560),
        (3291, 562)]),
    # p_s10, p_s11: Tote Road runs on Pick Pole's line from where its own line meets it to where it leaves for its
    # square (the piece is Pick Pole's)
    ('TOTE ROAD', [(2702, 645), (2711, 655), (2739, 669), (2751, 673), (2760, 681)]),
]
