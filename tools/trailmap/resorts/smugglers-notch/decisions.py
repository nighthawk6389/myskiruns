"""Smugglers' Notch's naming decisions, settled on zoomed crops (grid_crop.py over work/smugglers-notch/map.png with
the pieces tagged id:name). Every decision is a POINT in map px (work/smugglers-notch/map.png, 4238x2865), so it
survives a re-extraction: pdf_resort.py finds the piece through it. `pdf_resort.py smugglers-notch add` records new
ones.

CHECKED  [((x, y), NAME)]   the piece through the point is that trail (overrides the auto-match)
UNNAMED  [((x, y), why)]    the piece is not a trail
CUTS     [((x, y) on the piece, (x, y) to cut at)]  one drawn line carries two trails; the second part becomes a
                            new piece (appended, so the other ids stay put)
TRACED   [(NAME, [(x, y), ...])]  a stretch with no drawn line of its own
"""
CHECKED = [
    # sp_pw (2480,880 z1.8): a parallel lane that leaves Lower Rumrunner's line and rejoins it
    ((2622, 1039), 'Lower Rumrunner'),
    # sp_st1 (2850,550 z1.0): Bootlegger's black line goes on below the black traverse
    ((3030, 784), 'Bootlegger'),
    # sp_lp (3150,780 z2): Hangman's line goes on across the lift and Lower Pipeline to Black Snake
    ((3304, 881), 'Hangman’s'),
    # sm_jr.png (PDF 7x at 1185,415 pt): Jolly Rodger's leader ends on a short dash of its line; the line goes on
    # from Black Bear across the lifts and Pipeline Escape
    ((3031, 1115), 'Jolly Rodger'),
    ((3186, 1110), 'Jolly Rodger'),
    # sp_st2 (2800,950 z1.05): the blue line below the foot of Black Bear's black line, down to the top of the
    # Birch Run park line its label's leader names
    ((2904, 1283), 'Birch Run'),
    # sp_kr (2450,1100 z1.15): the orange park line (two strokes) beside the KNIGHT'S REVENGE GLADED PARK box
    ((2459, 1193), 'Knight’s Revenge Gladed Park'),
    ((2530, 1447), 'Knight’s Revenge Gladed Park'),
    # sp_morse (250,1100 z1.0): the orange park line beside the LOG JAM TERRAIN PARK box
    ((464, 1801), 'Log Jam Terrain Park'),
    # sp_mc: McPherson's line below its label and on below the lift to Lower Chilcoot
    ((2085, 1149), 'McPherson’s'),
    ((2103, 1231), 'McPherson’s'),
    # sp_mc (1830,780 z1.3): Dan's Ford's line from Goat Path across Mulcahy's Link, and on below the lift to
    # Lower Chilcoot
    ((1936, 837), 'Dan’s Ford'),
    ((1874, 1003), 'Dan’s Ford'),
    # sp_wf: the short blue line from the mid-station junction to the top of Father Bob's line (its leader names
    # the line below)
    ((1578, 684), 'Father Bob’s'),
    # sm_top.png (PDF 5x at 740,90 pt): THE BLACK HOLE's leader ends 5 pt from its line (three diamonds); the same
    # line with three diamonds goes on below the traverse
    ((2079, 606), 'The Black Hole'),
    ((2090, 835), 'The Black Hole'),
    # sp_wf (1280,600 z1.5): the blue line from Upper Chilcoot down to the tops of Ruthie's (blue) and Gary B's
    # (black): Ruthie's top
    ((1373, 776), 'Ruthie’s'),
    # sp_ml: the green line past the right end of the HOWIE'S WANDERER box (text Howie's, glyphs Wanderer) down to
    # the base
    ((1210, 2004), 'Howie’s Wanderer'),
    # sp_vil (950,2050 z0.85): Meadowlark's line goes on across lift C
    ((1252, 2342), 'Meadowlark'),
    # sp_ml: the green line along the lift below the foot of Upper Morse Liftline's black line, down to where
    # LOWER MORSE LIFTLINE's labelled line goes on
    ((930, 1838), 'Lower Morse Liftline'),
    # sp_ms: the green line round the west side of the Morse summit lift and across it, down into Garden Path's
    # labelled line; sp_ml: Garden Path crosses the lift and curves back to the liftline
    ((781, 1337), 'Garden Path'),
    ((906, 1373), 'Garden Path'),
    ((1005, 1687), 'Garden Path'),
    # sp_ml (850,1550 z1.3): Snow Snake's line goes on across the lift line to the Morse lift
    ((1020, 1849), 'Snow Snake'),
    # sm_morsetop.png: the blue line from the Morse summit along the ridge to that junction, where Snow Snake
    # drops away below: Snow Snake's top (the resort's only other blue run on Morse, Evaporator, is far below)
    ((944, 1292), 'Snow Snake'),
    # sp_ms (700,1230 z1.6), sm_morsetop.png (PDF 7x at 330,500 pt): from the Morse summit the green line runs
    # east to the junction where the boundary line turns green and is labelled MIDWAY
    ((978, 1337), 'Midway'),
]
UNNAMED = [
    # sm_top.png: the black line with a double diamond from the Madonna summit down to Catwalk, left of Upper
    # Liftline, has no name: the resort's trail list has no other expert run (Freefall, Robin's Run, Upper
    # Liftline and The Black Hole are each on their own line)
    ((1980, 346), "expert line (double diamond) from the Madonna summit to Catwalk with no name printed; the "
                  "resort's trail list has no other expert run"),
    # unnamed links and traverses: no name printed on them
    ((742, 1935), "short green link from Dixie's Knoll down to Bud's Way; no name printed"),
    ((2366, 460), 'short blue link from Upper Drifter down to Lower Catwalk (sm_drift.png); no name printed'),
    ((1777, 558), "short black dash between Doc Dempsey's Glades and Upper F.I.S.; no name printed"),
    ((2049, 694), 'black traverse below Freefall across The Black Hole to Upper Liftline (sm_top.png); no name '
                  'printed'),
    ((2151, 927), "short blue line in the trees above Three Mtn. Glades' circle (sm_51.png); no name printed"),
    ((2709, 1513), 'blue run-out between Lower Rumrunner and the Birch Run park (sp_kr); no name printed'),
    ((2958, 1227), 'blue traverse across the foot of Black Bear to Lower Exhibition (sp_st2); no name printed'),
    ((2872, 1243), 'blue traverse across the foot of Black Bear from Treasure Run (sp_st2); no name printed'),
    ((3440, 630), "blue access at the Sterling summit to the tops of Hangman's Drop and Upper Pipeline (sp_ss); no "
                  "name printed"),
    ((3057, 1674), 'the ski-back route to parking lot 1 (its sign: Ski Back to Parking Lot #1); not a trail'),
    ((3106, 1621), 'the ski-back route to parking lot 1 (its sign: Ski Back to Parking Lot #1); not a trail'),
    ((3288, 927), 'short blue stub from Lower Pipeline toward Black Snake (sp_lp); no name printed'),
    ((3079, 748), "black traverse from Smugglers' Alley across Bootlegger toward Thomke's (sp_st1); no name printed"),
]
CUTS = [
    # sm_drift.png (PDF 5x at 900,150 pt): one line carries UPPER DRIFTER (labelled along the summit ridge) and LOWER
    # DRIFTER (labelled just below Lower Catwalk's junction): cut at that junction
    ((2438, 324), (2459, 621)),
]
TRACED = []
