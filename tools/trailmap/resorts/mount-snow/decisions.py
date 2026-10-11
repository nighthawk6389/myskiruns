"""Naming decisions for Mount Snow, settled on crops, keyed by points in map px (work/mount-snow/map.png), so they
survive a re-extraction: pdf_resort.py finds the piece through each point. `pdf_resort.py mount-snow add` records
new ones. The crops were read on this season's image and, where it is too soft, on the 2023-24 PDF rendered on the
same grid (work/mount-snow/ref2023.png; the Sunbrook inset on a 3.5x render of the 2023-24 inset).

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # the Sunbrook inset: each line by the label printed on it, or the run it continues
    ((299, 161), 'Big Dipper'), ((222, 237), 'Big Dipper'),  # from the summit along the ridge, down the west side
    ((319, 195), 'Moonwalk'), ((319, 177), 'Moonwalk'), ((366, 150), 'Moonwalk'),  # its line, square and start
    ((186, 343), 'Little Dipper'), ((320, 433), 'Little Dipper'),  # both its labels, down to the base
    ((348, 235), 'Thanks Walt'), ((321, 345), 'Thanks Walt'),  # from its square down to the base
    ((367, 282), 'Cloud Nine'), ((340, 396), 'Cloud Nine'),  # beside the Sunbrook lift
    ((405, 190), 'Sunspot'), ((397, 190), 'Sunspot'),
    ((442, 237), 'Shooting Star'), ((326, 285), 'Shooting Star'), ((514, 201), 'Shooting Star'),  # on across Cloud
    ((233, 293), 'One Small Step'),  # Nine to Thanks Walt; its tick from Long John
    ((171, 413), 'Moonbeam'), ((299, 489), 'Moonbeam'),
    ((666, 421), 'Milky Way'), ((582, 518), 'Milky Way'),  # from the Nitro top round to the Sunbrook base
    ((422, 148), 'Skyline'), ((425, 158), 'Skyline'),  # the summit traverse
    ((613, 334), 'Bear Paw'), ((719, 362), 'Bear Paw'), ((758, 371), 'Bear Paw'),
    ((583, 228), 'Long John'),  # its top, from the summit, before its label
    ((498, 395), 'Bear Trap'), ((352, 505), 'Bear Trap'),  # the black line beside its lift
    # the main face
    ((1875, 294), 'Long John'),  # from the summit to its label
    ((1250, 889), 'Somerset Road'), ((1621, 838), 'Somerset Road'), ((1674, 835), 'Somerset Road'),  # its dashes,
    ((1739, 838), 'Somerset Road'), ((1802, 839), 'Somerset Road'), ((1886, 842), 'Somerset Road'),  # broken at
    ((1986, 842), 'Somerset Road'),  # each lift, west to Long John
    ((1322, 623), 'Low Traverse'), ((1425, 804), 'Low Traverse'),  # from Long John into its square; on down past
    ((1321, 907), 'Low Traverse'),  # Somerset Road to the base
    ((1786, 425), 'High Traverse'), ((1842, 442), 'High Traverse'), ((1875, 459), 'High Traverse'),  # from the
    ((2030, 568), 'High Traverse'),  # Grand Summit top to its square, and on to the Canyon top
    ((2100, 638), 'Snowdance Pitch'),  # from the Canyon top to its square
    ((1790, 581), 'Link'), ((1927, 607), 'Link'), ((1985, 596), 'Link'), ((1734, 579), 'Link'),  # its dashes
    ((1494, 646), 'Hop'),  # on below its square across the lift to Low Traverse
    ((1907, 554), 'Ledge'), ((1993, 324), 'Ledge'),  # the black Ledge: from the summit, past its diamond
    ((2057, 313), 'Committed'), ((2078, 304), 'Committed'),  # its top from Skyline
    ((1106, 679), 'Tunnel Vision'), ((1116, 694), 'Tunnel Vision'), ((975, 622), 'Tunnel Vision'),  # its dashed
    ((995, 630), 'Tunnel Vision'), ((947, 594), 'Tunnel Vision'), ((951, 605), 'Tunnel Vision'),  # orange line
    ((961, 616), 'Tunnel Vision'),
    ((1454, 1088), "Charlie's Chase"),  # its line, under Sap Bucket's label (a glade printed beside it)
]
UNNAMED = [
    ((1548, 927), 'a link with no name, from Somerset Road past Pat\'s Pitch'),
    ((1416, 973), 'a link with no name, from Somerset Road beside Drop'),
    ((1043, 1053), 'a link with no name, from Sweet Sixteen to Long John'),
]
CUTS = []
TRACED = []
TRIMS = []
