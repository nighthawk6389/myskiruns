"""Naming decisions for this panel, settled on crops, keyed by points in map px (work/snowmass/<panel>/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # Elk Camp: one line runs from the top of Elk Camp past TURKEY TROT, then turns down past FUNNEL (see CUTS)
    ((1442, 697), 'Turkey Trot'),
    ((1182, 993), 'Funnel'),
    # the line from Funnel's foot on down past FUNNEL (its lower name) to the base; above the turn it runs back up to
    # the Elk Camp lifts, no name printed (UNNAMED)
    ((1594, 1305), 'Funnel'),
    # a second line beside SLIDER's, from the same place to the same place
    ((1434, 983), 'Slider'),
    # the short branches beside BULL RUN's and SANDY PARK's lines, where each splits around a stand of trees
    ((846, 721), 'Bull Run'),
    ((1108, 676), 'Sandy Park'),
    # the green line from the base past ASSAY HILL turns at the bottom and runs on past BRIDGES (see CUTS)
    ((1534, 1286), 'Assay Hill'),
    ((1697, 1342), 'Bridges'),
    # Hanging Valley on the whole mountain, as the inset names its lines (the main map prints few of its names): the
    # cased line from Cookies' top to the junction below POSSIBLE and BABY RUTH is Hanging Valley Glades (its name is
    # printed beside the junction), on down to the foot Weird Woods (see CUTS); the line through BABY RUTH's EX from
    # The Edge's top to that junction is Baby Ruth
    ((1663, 551), 'Hanging Valley Glades'),
    ((1543, 616), 'Weird Woods'),
    ((1434, 664), 'Weird Woods'),
    ((1651, 510), 'Baby Ruth'),
    # the cased traverse along the boundary from High Alpine (the upper of its two lines, and the lower one as far as
    # the Roberto's and Valley Valley junction) is the inset's High Pass (Lower BD); from there on down past LOWER
    # LADDER, Lower Ladder (the inset's Upper Ladder too: the main map doesn't print it) (see CUTS)
    ((1721, 377), 'High Pass (Lower BD)'),
    ((1513, 414), 'High Pass (Lower BD)'),
    ((1244, 558), 'Lower Ladder'),
    # the Cirque: EAST WALL is printed on the cased line from the corner of the top traverse down to the Cirque
    # Headwall junction (see CUTS)
    ((2110, 396), 'East Wall'),
    # Big Burn: one black line runs down GLISSADE to its foot, then back up the gully past GARRETT GULCH to the top
    # (see CUTS; West Face and Free Fall join it on the way, WEST GARRETT is printed beside it with its EX: the
    # extreme terrain beside the gully, a marker); its foot to Trestle is the gully's too
    ((2290, 690), 'Glissade'),
    ((2465, 479), 'Garrett Gulch'),
    ((2340, 760), 'Garrett Gulch'),
    # Sheer Bliss splits at the top: SHEER BLISS is printed on the upper branch; the lower (past West Face's top)
    # rejoins it below
    ((2404, 443), 'Sheer Bliss'),
    # from the Cirque's lift top down into Whispering Jesse, at its name's top
    ((2492, 422), 'Whispering Jesse'),
    # the line down WINESKIN runs on to the Big Burn lift's foot, then on down MONKSHOOD (see CUTS)
    ((2540, 600), 'Wineskin'),
    ((2352, 835), 'Monkshood'),
    # from the Big Burn lift's foot past TRESTLE to the Sheer Bliss lift's foot, then down past GREEN CABIN (see CUTS)
    ((2287, 778), 'Trestle'),
    # from Sam's Knob along BANZAI RIDGE, down beside CONEY GLADE to the Coney lift's top, then down past BLUE GROUSE
    # (see CUTS)
    ((2760, 646), 'Banzai Ridge'),
    ((2637, 739), 'Coney Glade'),
    ((2516, 897), 'Blue Grouse'),
    # HAL'S HOLLOW is printed across its line, which runs from the Coney lift's top down to the base
    ((2700, 852), "Hal's Hollow"),
    ((2597, 1002), "Hal's Hollow"),
    # COYOTE HOLLOW is printed on the top of a line that runs on down beside the Big Burn lift, TIMBERLINE beside its
    # foot (the only line by that name): cut where Whispering Jesse leaves it (see CUTS)
    ((2533, 386), 'Coyote Hollow'),
    ((2500, 590), 'Timberline'),
    # Green Cabin from the High Alpine lift's foot (Green Cabin (Upper) ends there) to the Sheer Bliss lift's foot,
    # where GREEN CABIN is printed again on the lower part (see CUTS)
    ((2106, 711), 'Green Cabin (Lower)'),
    # the Cirque: HANG ON HALVIN'S is printed beside the cased line leaving Buckskin's past its EX
    ((2153, 632), "Hang On Halvin's"),
    # Sam's Knob: FAST DRAW is printed below the black line from the ridge down to Ute Chute's (no other line by it)
    ((2826, 649), 'Fast Draw'),
    # WILDCAT is printed on the line from the top of Sam's Knob that turns back up to the Campground's (see CUTS); on
    # down to the junction above Sam's Knob's foot, then on down to Slot's
    ((3048, 621), 'Wildcat'),
    ((3113, 705), 'Wildcat'),
    ((3200, 856), 'Wildcat'),
    ((3214, 660), 'Campground'),
    # DAWDLER is printed at the foot of its green line
    ((2933, 962), 'Dawdler'),
]
UNNAMED = [
    ((1500, 1042), 'from Funnel back up to the Elk Camp lifts: no name printed'),
    ((1880, 992), "a connector from Green Cabin's foot: no name printed"),
    ((1282, 790), "the run-out from Hanging Valley's foot to the Meadows: no name printed"),
    ((1385, 584), "a cased line between Wall Two's and Cassidy's with no name printed (the inset's differ here)"),
    ((1229, 714), "the exit from Hanging Valley's foot: no name printed"),
    ((1339, 693), "the traverse along Hanging Valley's foot: no name printed"),
    ((2560, 350), 'the traverse along the top of Big Burn between the lifts: no name printed'),
    ((2700, 934), "the green connector from Hal's Hollow to Scooper: no name printed"),
    ((2379, 921), 'from Monkshood across the lifts at the Hot Dogger: no name printed'),
    ((2460, 974), 'on from the Hot Dogger to Velvet Falls: no name printed'),
    ((2006, 657), "from under the Alpin Room's callout to the High Alpine lift's foot: no name printed"),
    ((2115, 624), "the cased exit from the foot of the Cirque's runs (two double diamonds): no name printed"),
    ((3083, 844), "from the Wildcat and Howler junction to Sam's Knob's foot: no name printed"),
    ((3184, 793), "from the Campground lift's top across to the Wildcat and Howler junction: no name printed"),
    ((3065, 769), 'a cut-across from Wildcat to Slot: no name printed'),
    ((2836, 815), "from Moonshine's and Ute Chute's foot across to Sam's Knob's: no name printed"),
    ((2201, 1110), 'a green run-out at the base, below Cabin: no name printed'),
    ((2327, 1074), 'a green run-out at the base, below Cabin: no name printed'),
    ((2300, 333), "the cased traverse along the top of the Cirque's runs, from Big Burn's top: no name printed"),
    ((2186, 467), "the Cirque's run-out below its headwalls (two double diamonds): no name printed"),
]
CUTS = [
    ((1442, 697), (1010, 838)),  # Turkey Trot / Funnel, where the line turns down
    ((1594, 1305), (1313, 1114)),  # Funnel / the connector back up, at the turn
    ((1534, 1286), (1312, 1446)),  # Assay Hill / Bridges, at the turn
    ((2290, 690), (2336, 746)),  # Glissade / Garrett Gulch, at Glissade's foot
    ((2540, 600), (2397, 782)),  # Wineskin / Monkshood, at the Big Burn lift's foot
    ((2287, 778), (2112, 807)),  # Trestle / Green Cabin, at the Sheer Bliss lift's foot
    ((2760, 646), (2662, 686)),  # Banzai Ridge / Coney Glade, where the line turns down
    ((2637, 739), (2617, 803)),  # Coney Glade / Blue Grouse, at Lunchline
    ((2533, 386), (2567, 442)),  # Coyote Hollow / Timberline, where Whispering Jesse leaves
    ((2106, 711), (2029, 669)),  # the connector / Green Cabin, at the High Alpine lift's foot
    ((3048, 621), (3023, 573)),  # Wildcat / Campground, at the turn
    ((3113, 705), (3135, 813)),  # Wildcat / the traverse to Sam's Knob's foot, at the junction
    ((1663, 551), (1619, 567)),  # Hanging Valley Glades / Weird Woods, at the junction
    ((1513, 414), (1392, 452)),  # High Pass (Lower BD) / Lower Ladder, at the Roberto's junction
    ((2110, 396), (2047, 348)),  # the top traverse / East Wall, at the corner
    ((2110, 396), (2171, 428)),  # East Wall / the run-out, at the Cirque Headwall junction
]
# ROCK BAND CHUTE's line is drawn from the top down along Grinder's (beside GRINDER) to where it leaves it: its own
# stretch is from there on
TRIMS = [((1938, 489), (1888, 465))]
TRACED = []
