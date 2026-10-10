"""Naming decisions for this panel, settled on crops, keyed by points in map px (work/aspen-mountain/main/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    # (work/aspen-mountain/main/crops/: the main map draws a run on as one path where the next starts; each stretch
    # named by the name printed on it, cut at the junction between two names)
    # from Ajax Express's foot up DIPSY DOODLE to the top, east along BUCKHORN and MIDWAY ROAD to Tourtelotte Park, down
    # RUTHIE'S RUN beside the lift to its foot, round the top of Shadow Mountain (no name printed), west along MAGNIFICO
    # ROAD, east along TOWER TEN ROAD (see CUTS)
    ((999, 1154), 'Dipsy Doodle'), ((926, 1025), 'Buckhorn'), ((1165, 1126), 'Midway Road'),
    ((1365, 1562), "Ruthie's Run"),
    ((1297, 2071), 'Magnifico Road'), ((1385, 2243), 'Tower Ten Road'),
    # from SILVER DIP down past Ajax Express's foot, down SPAR GULCH to KLEENEX CORNER, down UPPER LITTLE NELL and
    # LITTLE NELL to the base; and the branch to the Little Nell lift's foot
    ((964, 1279), 'Silver Dip'), ((1113, 1600), 'Spar Gulch'), ((1099, 2092), 'Kleenex Corner'),
    ((1111, 2184), 'Upper Little Nell'), ((1057, 2473), 'Little Nell'), ((1073, 2497), 'Little Nell'),
    # from Roch Run's foot along SUMMER ROAD to Aztec's top and back round the slow zone (the road's line), down LOWER
    # ROCH RUN to Spring Pitch's foot (the road runs on along it: trails:apply joins Summer Road's two stretches along
    # it), on along SUMMER ROAD and W 5TH AVE, then down to the base (no name printed)
    ((1413, 1645), 'Summer Road'), ((1454, 1718), 'Summer Road'), ((1385, 1903), 'Lower Roch Run'),
    ((1657, 2237), 'Summer Road'),
    ((1506, 2374), 'W 5th Ave'),
    # 1 & 2 LEAF is two runs, two lines (the summit inset prints the name on both): the second from the top of the
    # gondola past the pill down to Silver Dip, SILVER DIP below
    ((835, 1140), '1 & 2 Leaf'), ((908, 1235), 'Silver Dip'),
    # COPPER from the top down to Copper Connector's junction, COPPER BOWL from there to Spar Gulch
    ((914, 1703), 'Copper Bowl'), ((741, 1217), 'Copper'),
    ((1299, 1466), 'Upper Roch Run'), ((1330, 1650), 'Roch Run'),
    ((1531, 2158), 'Strawpile'), ((1467, 2308), 'Beattie Way'), ((1500, 2327), 'Strawpile'),
    # GENTELMEN'S RIDGE and GENT'S RIDGE are printed on one line (resort.py RENAME): Gent's Ridge, up to North Star's
    ((722, 1630), "Gent's Ridge"), ((680, 1204), 'North Star'),
    ((1315, 2373), 'Normandy'), ((1266, 2158), 'Magnifico'),
    # Aztec down to the Ruthie's lift's foot, Spring Pitch from there
    ((1553, 1796), 'Aztec'), ((1471, 1960), 'Spring Pitch'),
    # Walsh's down beside the Hero's lift to Lud's Lane, Lower Walsh's below it
    ((565, 1083), "Walsh's"), ((446, 1223), "Lower Walsh's"),
    # the black line under the BLAZING STAR pill (the build gave it Pussyfoot's name, printed beside it)
    ((912, 1101), 'Blazing Star'),
    # the blue line from Tower Ten Road down to the LOWER CORKSCREW pill, and on under it
    ((1429, 2332), 'Lower Corkscrew'), ((1415, 2358), 'Lower Corkscrew'),
    # the two lines from Midway Road down through Tourtelotte Park, either side of its name (the summit's inset prints
    # the name along the western one, which runs on down to the Ajax Express's foot)
    ((1217, 1253), 'Tourtelotte Park'), ((1092, 1227), 'Tourtelotte Park'),
]
UNNAMED = [
    ((1312, 1966), "from the Ruthie's lift's foot round the top of the Shadow Mountain lift to Magnifico Road: no name "
                   "printed"),
    ((1360, 2472), "from W 5th Ave down to the base: no name printed"),
    ((1210, 1287), "from Tourtelotte Park down across Red's Run to FIS Trail: no name printed"),
    ((1364, 2273), "the blue line from the Shadow Mountain lift's top down to Tower 7 Road: no name printed"),
]
CUTS = [
    ((999, 1154), (860, 1024)), ((926, 1025), (1019, 1075)), ((1165, 1126), (1247, 1246)), ((1365, 1562), (1484, 1875)),
    ((1312, 1966), (1459, 2003)), ((1297, 2071), (1137, 2148)),
    ((964, 1279), (1045, 1334)), ((1113, 1600), (1049, 2093)), ((1099, 2092), (1148, 2097)),
    ((1111, 2184), (1080, 2285)),
    ((1413, 1645), (1537, 1708)), ((1454, 1718), (1353, 1754)), ((1385, 1903), (1498, 2047)),
    ((1657, 2237), (1584, 2360)),
    ((1506, 2374), (1429, 2394)),
    ((835, 1140), (892, 1217)),
    ((914, 1703), (820, 1505)),
    ((1299, 1466), (1306, 1548)),
    ((1531, 2158), (1512, 2225)),
    ((722, 1630), (658, 1413)),
    ((1315, 2373), (1294, 2222)),
    ((1553, 1796), (1513, 1879)),
    ((565, 1083), (494, 1167)),
]
# Summer Road's two stretches (its two SUMMER ROAD labels) are joined by the blue line LOWER ROCH RUN is printed on
# (the road runs on along it; left to trails:apply, they would be joined down the black Aztec and Spring Pitch): that
# line, traced again for Summer Road (a shared stretch)
TRACED = [('Summer Road', [(1353, 1754), (1333, 1782), (1322, 1818), (1327, 1843), (1352, 1852), (1375, 1866),
                           (1384, 1884), (1385, 1910), (1388, 1934), (1396, 1954), (1409, 1970), (1425, 1985),
                           (1480, 2029), (1498, 2047)])]
TRIMS = []
