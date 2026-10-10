"""Naming decisions for Alta's map, settled on crops, keyed by points in map px (work/alta/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # the High Traverse: black dashes from the Collins top south along the ridge, past the Rustlers' tops, to
    # Greeley Bowl (one dashed path per stretch)
    ((2706, 610), 'High Traverse'), ((2703, 644), 'High Traverse'), ((2656, 816), 'High Traverse'),
    ((2764, 1190), 'High Traverse'), ((2759, 1356), 'High Traverse'), ((2738, 1506), 'High Traverse'),
    ((2980, 520), 'Ballroom'),  # the blue dashes east from the Collins top, the BALLROOM square on them
    ((3351, 1373), "Johnson's Warm-up"),  # its line from Angle Station's top, under its name
    ((2885, 987), 'Race Course'),  # its line on below its name to the High Traverse's foot
    ((2369, 420), 'Sugar Bowl'),  # its line from the Sugarloaf top into its name
    ((2229, 882), 'Running Dog Nose'),  # its line out of its name
    ((3231, 551), 'Shoulder Traverse'),  # the dashes under its name, on from the Ballroom traverse
    ((2838, 1898), 'Rustler Four'),  # its line beside its name
    ((3114, 1601), 'Race Course Saddle'),  # the blue line from Race Course Saddle's top past West Rustler to Meadow
    ((1654, 1638), 'Race Hill'),  # its line from the Sunnyside top's side to its square
    ((2428, 408), "Devil's Elbow"),  # its dotted way from the Sugarloaf top round to its square
    ((1498, 1310), "Rock N' Roll"),  # its dotted way on from its foot on Big Dipper's to Over the River's
]
UNNAMED = [
    ((3418, 2143), 'a dash of a lift icon\'s line at the Wildcat base'),
    ((480, 545), 'the line from the Supreme top to Catherine\'s Area\'s runs: no name printed'),
    ((2014, 1989), 'a dotted link between Crooked Mile\'s and Home Run\'s ways down: no name printed'),
    ((1698, 1279), 'a dotted link from Devil\'s Elbow\'s way to Big Dipper\'s, by SUPREME ACCESS: no name printed'),
]
CUTS = []
TRACED = [
    # HIGH MAIN STREET, printed on two lines in a gap of its line: the line on from its diamond, under the name, to
    # the short stroke past STREET
    ('High Main Street', [(2830, 578), (2880, 603), (2930, 632), (2975, 664)]),
]
TRIMS = []
