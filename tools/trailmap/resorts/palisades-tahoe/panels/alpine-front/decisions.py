"""Naming decisions for the alpine-front panel, settled on crops, keyed by points in map px
(work/palisades-tahoe/alpine-front/map.png), so they survive a re-extraction: pdf_resort.py finds the piece through
each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # pt/boom.png, pt/boom2.png: Werner's Schuss's line goes on below its name, across Wolverine's (which bends into Boomerang's branch) and down the loop's other branch to East Runout's symbol, one stroke
    ((2280, 886), 'Werner’s Schuss'),
    # pt/und_af/*.png, pt/af1-af3.png (PDF strokes in drawing order, seq.py): To Lakeview's arrowed route from the Mid-Unload station along its name and past its symbol up to the Lakeview chair; Subway and Meadow Beginner Areas' lines along their lifts; Return Road's line past its symbol; Skateboard Alley's, Yellow Trail's, Banana Chute's, Charity's, East Runout's and Sunspot's lines below their names (each drawn right after its run's own stroke); Alpine Bowl's, Nick's Run's, D8's, Pete's Peril's and Reily's Run's lines through their symbols; Outer Limits' line below its name to the Lakeview chair's top; Wolverine's from its name down to where it crosses Werner's Schuss's line; Boomerang's from there into its name
    ((1240, 801), 'To Lakeview'),
    ((842, 685), 'To Lakeview'),
    ((1111, 1713), 'Subway Beginner Area'),
    ((1112, 663), 'Return Road'),
    ((1346, 1026), 'Skateboard Alley'),
    ((1584, 1072), 'Yellow Trail (Alpine)'),
    ((2065, 1062), 'Banana Chute'),
    ((2148, 964), 'Charity'),
    ((1964, 1286), 'East Runout'),
    ((2489, 385), 'Alpine Bowl'),
    ((2552, 421), 'Sunspot'),
    ((2532, 1092), 'Nick’s Run'),
    ((653, 493), 'Outer Limits'),
    ((2748, 468), 'D8'),
    ((2244, 595), 'Pete’s Peril'),
    ((976, 591), 'Reily’s Run'),
    ((1382, 1463), 'Meadow Beginner Area'),
    ((2324, 721), 'Wolverine'),
    ((2193, 854), 'Boomerang'),
]
UNNAMED = [
]
CUTS = [
]
TRACED = [
]
