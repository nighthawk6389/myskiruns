"""Naming decisions settled on crops, keyed by points in map px (work/mt-bachelor/map.png), so they survive a
re-extraction: pdf_resort.py finds the piece through each point. `pdf_resort.py mt-bachelor add` records new ones.

The crops: piece sheets (tools/trailmap/piece_sheet.py: each piece alone in magenta with the names around it) and
zoomed grid crops (tools/trailmap/grid_crop.py, with the pieces, names and symbols drawn on). On this map a name is
printed in a gap of its line, its symbol at the start of the name as it reads (so at the top or the bottom), and the
line runs on from both ends of the name: a line that runs into a name, with no junction between, is that trail's.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # the beginner area at Sunrise (und/crop_460_2120.png, und3/zbeg_plain.png): each of the four runs is a loop from
    # the Early Riser lift's top, along its name to its circle, then round to the lift's bottom: Green Flash's line
    # beyond its name and from its circle down the left side; Morning Glory's beyond its name and the stub under its
    # circle; Early Riser's from the lift's top to its name and the S-curve into its circle; Day Break's from the
    # lift's top to its name and the arc into its circle
    ((685, 2181), 'Green Flash'),
    ((495, 2269), 'Green Flash'),
    ((685, 2205), 'Morning Glory'),
    ((519, 2303), 'Morning Glory'),
    ((732, 2190), 'Early Riser'),
    ((545, 2302), 'Early Riser'),
    ((721, 2247), 'Day Break'),
    ((559, 2341), 'Day Break'),
    # Marshmallow (und/crop_1100_1380.png, und/crop_900_1950.png, s_2): its name is printed (in fragments: EXTRA) in a
    # gap of one green line, from the junction under Chicken Foot down past Avalanche to the name, and from its circle
    # on down across the Sunrise Express to Sunrise Lodge
    ((1477, 1693), 'Marshmallow'),
    ((1064, 2065), 'Marshmallow'),
    # West Boundary (und/crop_2500_1850.png): its line from the junction at Red Shuttle's end down to its square, and
    # from its name's end down to the line by the boundary
    ((2622, 1991), 'West Boundary'),
    ((2697, 2290), 'West Boundary'),
    # Fish Hawk Wing and Osprey Way (und2/crop_3650_1450.png): two lines leave the end of Osprey Way's lower (blue)
    # name: one runs into Fish Hawk Wing's square (its name prints down from there; the auto-match gave it to Osprey
    # Way), the other on along the Northwest Express to the base (Osprey Way's); Fish Hawk Wing's line on from its
    # name's end to the lift
    ((4020, 1992), 'Fish Hawk Wing'),
    ((4348, 2195), 'Fish Hawk Wing'),
    ((4322, 2115), 'Osprey Way'),
    # Kangaroo (und/crop_2400_1420.png): its line from the Outback Express's top round to its square
    ((2716, 1511), 'Kangaroo'),
    # Outback Way (und/crop_2400_1420.png): the spur from the line at Pine Marten Lodge to its square, by the STOP sign
    ((2516, 1533), 'Outback Way'),
    # DSQ (und3/crop_1600_2100.png): DSQ is printed twice, high on the line from the Summit Crossover's circle and low
    # by its square; its upper line runs into Corkscrew's at the end of Corkscrew's name, and the line from there down
    # to DSQ's lower name is DSQ's (Corkscrew's name ends at the junction)
    ((1764, 2453), 'DSQ'),
]
UNNAMED = [
    # links with no name printed along them, each between two named lines or from a lift's top terminal
    ((1212, 1484), "a green link from a lift's top down to Roostertail's start (und3/z0.png): no name along it"),
    ((1492, 787), "a link from under Wanoga Way's name down to the Cloudchaser Express's top: no name along it"),
    ((2073, 1620), "a link from a lift's top down to the Summit Crossover's circle (und3/z80.png): no name along it"),
    ((2636, 1919), "a link from Leeway's line down to the junction at Red Shuttle's end: no name along it"),
    ((3208, 1785), "a link from Atkeson's Zoom's name down to Boomerang's and Melbourne's lines: no name along it"),
    ((4136, 1960), "a link from Brookie's Run's line across the Northwest Express to Osprey Way's: no name along it"),
    ((2422, 2406), "a link from Leeway's line across the lifts to Thunderbird's name: no name along it"),
    ((3562, 1939), "a link from the foot of Atkeson's Zoom's black line down to Kangaroo's lower square (und3/atk2p.png; "
                   "the Zoom's lower line goes on to its own square): no name along it"),
    ((1938, 2538), "the way from Sunshine's line into Progression Park (the park is its hatched area): no name"),
    ((2437, 2718), "a link from Leeway's lower name down to the West Village base: no name along it"),
    ((2386, 2720), "the way from Peace Park's foot down to the West Village base: no name along it"),
]
CUTS = [
]
TRACED = [
]
