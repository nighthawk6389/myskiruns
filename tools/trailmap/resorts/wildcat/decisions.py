"""Wildcat Mountain's naming decisions, settled on zoomed crops (grid_crop.py over work/wildcat/map.png with the
pieces tagged id:name). Every decision is a POINT in map px (work/wildcat/map.png), so it survives a
re-extraction: pdf_resort.py finds the piece through it. `pdf_resort.py wildcat add` records new ones.

CHECKED  [((x, y), NAME)]   the piece through the point is that trail (overrides the auto-match)
UNNAMED  [((x, y), why)]    the piece is not a trail
CUTS     [((x, y) on the piece, (x, y) to cut at)]  one drawn line carries two trails; the second part becomes a
                            new piece (appended, so the other ids stay put)
TRACED   [(NAME, [(x, y), ...])]  a stretch with no drawn line of its own
"""
CHECKED = [
    # close/mid.png: below Cat Track, Lift Lion's black line runs on as Black Cat (its diamond and name are printed beside it)
    ((1707, 1790), 'BLACK CAT'),
    # close/loop42.png: the inner green line of the loop at the top of Tomcat, from Upper Polecat past the start of Cat Track down to Tomcat (no name of its own; both ends lead into Tomcat)
    ((1132, 1405), 'TOMCAT'),
    # close/base.png: the blue line the ANNIE'S ALLEY square's arrow points to, from Cougar's foot across under the lift to the Bobcat lift
    ((1905, 2868), 'ANNIE’S ALLEY'),
    # close/base.png: the black line beside the Tomcat lift that the SPHYNX diamond's arrow points to, from Panther's foot down to the base, and the short black branch joining it from Alley Cat's foot (no other name on it)
    ((1782, 3000), 'SPHYNX'),
    ((1811, 2849), 'SPHYNX'),
    # pieces/sheet_5: the black line through the diamond printed with the two-line WILDCAT PITCH name, from Lower Cat Track down to Lower Wildcat
    ((2652, 2115), 'WILDCAT PITCH'),
    # pieces/sheet_5: the black line the LEO'S LEAP arrow points to, from Annie's Alley down to the base
    ((2169, 3037), 'LEO’S LEAP'),
    # pieces/sheet_3: the black line beside the lift through the FELINE diamond and down its name, from Tomcat to Middle Lynx
    ((1181, 1755), 'FELINE'),
    # pieces/sheet_3: the blue line through the OCELOT WAY square, from Lower Polecat down to the base road
    ((1392, 3106), 'OCELOT WAY'),
    # pieces/sheet_7: the green line from the MIDDLE POLECAT circle down to the Tomcat Schuss / Cat Walk junction, where Lower Polecat starts
    ((228, 2254), 'MIDDLE POLECAT'),
    # pieces/sheet_3: the black line the HAIRBALL arrow points to, through its diamond, down to Midway
    ((1429, 1952), 'HAIRBALL'),
    # pieces/sheet_6: the green line through the SNOWCAT SLOPE circle and along its name
    ((2610, 2911), 'SNOWCAT SLOPE'),
    # pieces/sheet_6: the green line through the SNOWCAT TRAIL circle and up its name
    ((2761, 2812), 'SNOWCAT TRAIL'),
    # pieces/sheet_4: the black line through the MIDDLE CATAPULT diamond and down its name, from Cat Track
    ((1904, 1697), 'MIDDLE CATAPULT'),
    # pieces/sheet_2: the blue line printed along HAINESVILLE PASS, from Midway's crossing up to Al's Folly's foot
    ((1570, 2165), 'HAINESVILLE PASS'),
    # pieces/sheet_1: the blue line through the LOWER CATAPULT square and down its name to the Bobcat lift
    ((2060, 2083), 'LOWER CATAPULT'),
    # close_uw.png, close_uw2.png: Upper Wildcat's black line leaves Upper Catapult's bend through its diamond and name, splits around a tree island and runs down to Cat Track (both branches, one name: no other name is printed on them)
    ((2281, 1008), 'UPPER WILDCAT'),
    ((2210, 1352), 'UPPER WILDCAT'),
    # tiles_review/crop_900_600: the black line from the top of Upper Catapult across into Lift Lion above its diamond (no name of its own; Lift Lion's second entrance)
    ((1678, 766), 'LIFT LION'),
    # tiles_review/crop_900_600: the short black line from Upper Polecat past the LYNX LAIR diamond down to Upper Lynx
    ((1299, 806), 'LYNX LAIR'),
]
UNNAMED = [
    # close/mid.png: the short blue link from the foot of Middle Catapult down to Cat Walk; no name printed
    ((1929, 1912), 'short link from the foot of Middle Catapult to Cat Walk; no name printed'),
    # close/east.png: the short blue link between Cheetah and Lower Wildcat; no name printed
    ((2521, 2203), 'short link between Cheetah and Lower Wildcat; no name printed'),
    ((2354, 1957), "hidden under Wild Kitten's green line (Middle Wildcat's foot to Bobcat's top): the drawn line there is Wild Kitten's"),
]
CUTS = [
    # pieces/sheet_0 #2, close/mid.png: one drawn line carries Upper, Middle and Lower Lynx: cut where Cat Track
    # crosses it and where Cat Walk crosses it (the sections the names are printed on)
    ((1545, 1300), (1442, 1502)),
    ((1271, 1900), (1162, 2179)),
    # close/mid.png: Top Cat runs on as Starr Line below Cat Track (Starr Line's diamond and name), Lift Lion as
    # Black Cat (its diamond and name)
    ((1608, 1300), (1633, 1531)),
    ((1644, 1300), (1686, 1533)),
    # pieces/sheet_6 #41: Tomcat runs from Cat Track's west end down to where Upper Polecat joins it at the Tomcat
    # circle; below the junction the line is Middle Polecat
    ((920, 1700), (770, 1775)),
    # close/east.png, close/hairpin.png: one line is Cat Track, then Middle Wildcat from its square, down a hairpin
    # that ends on Wild Kitten's green line, hidden under that line for 120 px, then Bobcat down to the base
    ((1900, 1512), (2033, 1622)),
    ((2350, 1851), (2415, 1953)),
    ((2262, 2232), (2294, 1967)),
    # close/catenary.png, close/catfoot.png: Midway's line runs on as Catenary from the CATENARY square (its name
    # is printed along the line below it) down to Lower Polecat; Lower Catenary and Lower Lynx branch off it
    ((1492, 2281), (1524, 2440)),
]
TRACED = [
    # close/hairpin.png: the LOWER CAT TRACK label's arrow points at Wild Kitten's green line between Middle
    # Wildcat's hairpin and the top of Lower Wildcat: the run shares that stretch of line
    ('LOWER CAT TRACK', [(2415, 1958), (2485, 1982), (2583, 1990), (2612, 2004)]),
]
