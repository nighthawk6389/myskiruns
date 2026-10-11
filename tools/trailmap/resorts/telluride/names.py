"""What Telluride's two inset images print, read on zoomed grid crops of each (2x the published PNG:
work/telluride/<panel>/map.png, in its px). The resort's mountain page shows them beside the trail map as the detail
of the hike-to terrain the map marks "See Reverse for Detail": revvy-23.24-1.png (Revelation Bowl, 962x878) and
palmyra-23.24.png (Palmyra Peak and Black Iron Bowl, 962x704), James Niehues's paintings with names, symbols and the
chutes' lines (black strokes). prepare.py routes each line along the painted one and pdf_resort.py builds the trail
list from these.

READING[panel]: (NAME as printed, (x, y) the label's middle, symbol, [line, ...]) per printed name. symbol: the one
printed by the name (circle, square, diamond, double-diamond; the EX is double black, as the app rates it). A line is
points along the run's own drawn line, in order (prepare.py snaps them onto the painted line); a name with no line (an
open face, a bowl, a numbered chute) has none and becomes a marker at its label.
"""

READING = {
    # Revelation Bowl (revvy-23.24-1.png): See Forever from the Revelation lift's top east past the Gold Hill Express
    # top, the two lines down the bowl to the Bear Creek Overlook, and three faces printed with a diamond and no line
    'revelation': [
        ('SEE FOREVER', (960, 600), 'square', [[
            (362, 366), (600, 470), (800, 545), (1000, 610), (1127, 662), (1300, 690), (1450, 692), (1600, 735),
            (1820, 780)]]),
        ('SILVERCLOUD', (640, 780), 'diamond', [[(422, 430), (560, 640), (700, 860), (760, 960), (900, 1190),
                                                 (1037, 1425)]]),
        ('MAJESTIC', (1100, 950), 'diamond', [[(1124, 712), (1110, 900), (1096, 1095), (1080, 1300), (1066, 1516)]]),
        ('GOLDEN CROSS', (862, 750), 'diamond', []),
        ("BEE'S RUN", (362, 837), 'diamond', []),
        ('LIBERTY BELL', (1546, 950), 'diamond', []),
    ],
    # Palmyra Peak and Black Iron Bowl (palmyra-23.24.png): the chutes off the Palmyra ridge, each name printed on
    # its line ("—NAME—EX"), the Gold Hill chutes as numbers with an EX, the bowl's faces, and the Black Iron Bowl
    # chutes down to the Prospect Express top (Genevieve to Confidence also on the main map)
    'black-iron-bowl': [
        ('ROY BOY', (847, 414), 'double-diamond', [[(917, 320), (885, 353), (847, 414), (800, 480), (783, 503)]]),
        ("SENIOR'S", (900, 398), 'double-diamond', [[(974, 248), (944, 339), (900, 398), (840, 460), (794, 512)]]),
        ('TRAM SHOT', (861, 487), 'double-diamond', [[(964, 423), (931, 445), (861, 487), (800, 517)]]),
        ('SUNRISE', (861, 531), 'double-diamond', [[(947, 481), (919, 503), (861, 531), (786, 564)]]),
        ('ELECTRIC SHOCK', (794, 631), 'double-diamond', [[(892, 553), (867, 576), (794, 631), (719, 706)]]),
        ('CAPITOL', (880, 664), 'double-diamond', [[(858, 617), (880, 664), (914, 723), (922, 728)]]),
        ('NICE CHUTE', (847, 933), 'double-diamond', [[(807, 857), (847, 933), (895, 1000), (921, 1040)]]),
        ('MOUNTAIN QUAIL', (1147, 802), 'double-diamond', [[(1205, 681), (1192, 697), (1147, 802), (1097, 931)]]),
        ('DIHEDRAL CHUTE', (1217, 810), 'double-diamond', [[(1330, 702), (1292, 739), (1217, 810), (1101, 931)]]),
        ('LAKEVIEW', (1347, 827), 'double-diamond', [[(1361, 718), (1347, 827), (1351, 902), (1373, 1027)]]),
        ('GENEVIEVE', (1538, 952), 'double-diamond', [[(1626, 883), (1605, 906), (1538, 952), (1467, 1010)]]),
        ('LA ROSA', (1613, 968), 'double-diamond', [[(1667, 897), (1655, 906), (1613, 968), (1582, 1018)]]),
        ('CRYSTAL', (1676, 968), 'double-diamond', [[(1730, 902), (1722, 906), (1676, 968), (1605, 1031)]]),
        ('CONFIDENCE', (1684, 993), 'diamond', [[(1772, 927), (1744, 950), (1684, 993), (1613, 1031)]]),
        ('GOLD HILL 1', (59, 1016), 'double-diamond', []),
        ('GOLD HILL 2', (137, 956), 'double-diamond', []),
        ('GOLD HILL 6', (281, 652), 'double-diamond', []),
        ('GOLD HILL 7', (373, 552), 'double-diamond', []),
        ('GOLD HILL 8', (380, 520), 'double-diamond', []),
        ('GOLD HILL 9', (391, 499), 'double-diamond', []),
        ('GOLD HILL 10', (430, 495), 'double-diamond', []),
        ('PALMYRA BASIN', (597, 686), 'diamond', []),
        ('SWEET MARTHA', (638, 970), 'diamond', []),
        ('THE FANS', (540, 1178), 'diamond', []),
        ('REVIEW', (938, 890), 'double-diamond', []),
        ("JELLO'S BOWL", (1033, 833), 'double-diamond', []),
        ('ZIPPER ROCK', (933, 1150), 'double-diamond', []),
        ('DIHEDRAL FACE', (1276, 852), 'double-diamond', []),
        ('WESTLAKE', (1426, 852), 'double-diamond', []),
    ],
}
