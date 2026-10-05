"""Sunday River's naming decisions, settled on zoomed crops (grid_crop.py over work/sunday-river/map.png with the
pieces tagged id:name). Every decision is a POINT in map px (work/sunday-river/map.png, 4800x2700), so it survives a
re-extraction: pdf_resort.py finds the piece through it. `pdf_resort.py sunday-river add` records new ones.

CHECKED  [((x, y), NAME)]   the piece through the point is that trail (overrides the auto-match)
UNNAMED  [((x, y), why)]    the piece is not a trail
CUTS     [((x, y) on the piece, (x, y) to cut at)]  one drawn line carries two trails; the second part becomes a
                            new piece (appended, so the other ids stay put)
TRACED   [(NAME, [(x, y), ...])]  a stretch with no drawn line of its own
"""
CHECKED = [
    # pieces/und_2: the green line in the Merrill Hill inset printed with SECOND THOUGHTS
    ((4093, 1634), 'SECOND THOUGHTS'),
    # close_t2.png, sr_bim.png: the black line from T2 across Locke Line to Upper Sunday Punch, with the JIM'S WHIM label and diamond just below it
    ((896, 771), 'JIM’S WHIM'),
    # pieces/und2_0: the short green stub where the horizontal DOUBLE REFRACTION label starts
    ((2438, 1445), 'DOUBLE REFRACTION'),
    # close/inset_jordan.png: the North Peak inset prints ROUNDABOUT along the green curve from the Jordan Bowl summit; the main map draws the same curve with no name
    ((2698, 505), 'ROUNDABOUT'),
    # pieces/und_0: the blue line from Second Mile down past the UPPER 3D label to Ridge Run (two pieces, cut where it passes the North Woods glades)
    ((2062, 1023), 'UPPER 3D'),
    ((2040, 1137), 'UPPER 3D'),
    # pieces/und_0: the green line from the top of lift 11 round the left of Green Cheese down to Moonstruck's label: Moonstruck's top
    ((72, 1224), 'MOONSTRUCK'),
]
UNNAMED = [
    # audit_close/r00_2000_1380.jpg, close/merrill_plain.png: Prism's lower stub beside its label at the foot of Merrill Hill; the main map leaves Prism's middle to the Merrill Hill inset (it would be bridged straight across the trees to Prism's upper part)
    ((2071, 1540), "Prism's lower end beside its label; the main map draws Prism's middle only in the Merrill Hill inset, so this stub is left out rather than bridged across the trees"),
    # close/inset_risky.png: the North Peak inset's Risky Business and Vortex lines, labelled without the Upper / Lower the main map prints on their two sections
    ((3580, 502), "North Peak inset: Risky Business's line (named Upper and Lower Risky Business on the main map)"),
    ((3739, 649), "North Peak inset: Vortex's line (named Upper and Lower Vortex on the main map)"),
    # pieces/und_0, und2: unnamed links and inset repeats
    ((1836, 1305), 'short blue link from Northway down to the South Ridge base; no name printed'),
    ((3411, 969), 'short green link from Lollapalooza down to the Jordan hotel; no name printed'),
    ((1747, 1344), 'short green stub in the South Ridge slow zone; no name printed'),
    ((3569, 693), 'North Peak inset, at its left edge: the end of Three Mile Trail at the lodge (named on the main map; no name visible in the inset)'),
    ((1852, 1978), 'base-area inset: repeats a main-map beginner run; no name printed in the inset'),
    ((2297, 2049), 'base-area inset: repeats a main-map beginner run; no name printed in the inset'),
    ((2185, 1981), 'base-area inset: repeats a main-map beginner run; no name printed in the inset'),
    ((2099, 1981), 'base-area inset: repeats a main-map beginner run; no name printed in the inset'),
    ((2028, 1939), 'base-area inset: an orange freestyle line with no name printed in the inset'),
]
CUTS = [
    # pieces/multi_0, along.py: one drawn line carries the upper and the lower run, cut where another line crosses
    # it between their labels (Risky Business: Three Mile Trail; T72: Ridge Run; Vortex: Lights Out; Air Glow:
    # Super Nova's junction), or midway between the labels where nothing crosses (Caramba)
    ((1674, 1035), (1746, 859)),
    ((2047, 1272), (2082, 1230)),
    ((2707, 531), (2874, 733)),
    ((1932, 681), (2009, 764)),
    ((2047, 540), (2260, 689)),
    # the North Peak inset's Caramba and Air Glow lines, the same way
    ((4438, 439), (4376, 584)),
    ((3907, 461), (3900, 551)),
    # multi_0 #65: one green line is Three Mile Trail from Barker's summit to the North Peak lodge, where Lights Out
    # joins, then Second Mile
    ((1316, 704), (1975, 884)),
    # pieces/multi2_0 #126: in the North Peak inset one green line is Sirius from Spruce Peak to where Borealis joins,
    # Aludra on to where Lights Out and Kansas join, then Cyclone (the main map draws the three as separate pieces
    # meeting at those junctions)
    ((3690, 480), (3759, 516)),
    ((3823, 533), (3876, 564)),
]
TRACED = []
