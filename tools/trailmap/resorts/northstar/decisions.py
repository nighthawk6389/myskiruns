"""Naming decisions for Northstar's map, settled on crops, keyed by points in map px (work/northstar/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on along another trail's line: cut it nearest
         the second and keep the part the first point is on
"""
CHECKED = [
    ((1252, 748), 'Axe Handle'),  # the stretch below Axe Handle's own line's join, labelled AXE HANDLE
    ((2198, 1090), 'Prosser'),  # Lookout Mountain's summit line, down to where Stampede leaves it
    ((1769, 304), 'Iron Horse'),  # the line from the summit into Iron Horse's, above its diamond and name
    ((2520, 1082), 'Iron Horse'),  # Iron Horse's line on past Why Not's to the Backside Express
    ((896, 1580), "Lower Lion's Way"),  # the line over LOWER LION'S WAY, printed on two lines below it
    ((1067, 1941), 'Timberline'),  # Timber Line's line on from its foot to the Timberline lift
    ((927, 1106), 'Sidewinder'),  # the run-out from the foot of the Sidewinder park's pill
    ((1138, 1553), 'Overland Trail'),  # the line under OVERLAND TRAIL (printed on two lines), on to Lion's Way
    ((2302, 923), 'Iron Horse'),  # its line out from under the Promised Land Express's band, to where Why Not leaves
    ((1100, 1042), 'Christmas Tree'),  # its run-out from CHRISTMAS to the Lumberjack circle
    ((1088, 1142), 'Christmas Tree'),  # and its line on from CHRISTMAS down to the Arrow Express's foot
]
UNNAMED = [
    # leader lines (from a label to its dot) drawn in the line colours
    ((768, 1618), 'leader: Ski & Snowboard School'), ((630, 1557), 'leader: the Lodge at Big Springs'),
    ((562, 1417), 'leader: the cross-country centre'), ((998, 1597), 'leader: The Ritz-Carlton'),
    ((534, 805), 'leader: the Teams Foundation Competition Arena'),
    # letters' halos and icons the extraction's filters missed
    ((1350, 1542), 'halo of a letter of LOOKOUT BYPASS'), ((2680, 993), 'halo of a letter of DOWN UNDER'),
    ((2706, 1043), 'halo of a letter of DOWN UNDER'), ((912, 508), 'halo of a letter of DUTCHMAN'),
    ((1288, 483), 'halo of a letter of CROSSCUT'), ((2578, 920), 'halo of a letter of LOWER BURNOUT'),
    ((1104, 948), 'halo of a letter of LUMBERJACK'), ((1354, 244), 'the M of the Mt. Pluto lettering'),
    ((228, 1259), 'the cross-country badge'), ((612, 507), 'the Terrain Parks badge'),
    # lines with no name printed on them
    ((353, 1677), 'a link from the Village Express\'s top past Kids Adventure Zone 4 to The Woods: no name printed'),
    ((1346, 437), 'a blue link from The Flume past Kids Adventure Zone 1 to Crosscut\'s line: no name printed'),
    ((1161, 1414), 'a traverse from the Gulch\'s circle under Lower Pioneer to Home Run\'s top and Lower Pioneer\'s '
                   'sign: no name printed'),
    ((1119, 854), 'a link from the line below The Chute to Lumberjack: no name printed'),
    ((1029, 1855), 'a link from The Glades\' sign round to Timber Line\'s foot: no name printed'),
    ((1295, 1010), 'Northern Lights\' outline doubling Christmas Tree\'s line under CHRISTMAS'),
    ((1425, 745), 'a link from West Ridge\'s foot past Upper Jibboom\'s square to Goldmine\'s: no name printed'),
    ((1032, 968), 'the line on below Skid Trail from The Chute\'s foot, with a square of its own and no name printed '
                  '(perhaps the report\'s Lower Chute)'),
    ((1754, 1072), 'a link from Schwarzstrasse\'s square west under the Lookout Link to The Face\'s: no name printed '
                   '(Schwarzstrasse goes on south)'),
]
CUTS = [
    # the summit of Mt. Pluto: Upper Grouse Alley up to it, The Plunge down from it, Spring Board up to West Ridge
    # from The Plunge's foot (one outline: a V at each)
    ((1665, 193), (1691, 179)), ((1467, 561), (1445, 578)),
    ((1721, 180), (1693, 176)),  # Polaris up to the summit, Burnout down from it
    ((1675, 450), (1698, 436)),  # Axe Handle up to West Ridge, Stump Alley down from it
    # Cascades up to Luggi's foot, the stretch labelled Axe Handle up to where Axe Handle's own line joins, Lower
    # Grouse Alley up to Upper Grouse Alley's foot, The Flume across to East Ridge
    ((1250, 753), (1243, 782)), ((1315, 658), (1347, 642)), ((1469, 445), (1492, 425)),
    # East Ridge to the summit, West Ridge down to Luggi's and Upper Jibboom's tops, Lookout Road down to Zephyr
    # Lodge, Drifter on to the Backside's foot
    ((1671, 182), (1692, 175)), ((1588, 639), (1580, 668)), ((1622, 811), (1625, 845)),
    ((2380, 1076), (2395, 1108)),  # The Islands down to where it joins Drifter
    # Lookout Mountain: Stampede's lower half up to the Martis Camp Express's top, Boca up to the summit, the
    # summit's line down to where Stampede leaves it, Prosser down to Martis Camp
    ((2114, 1765), (2118, 1725)), ((2091, 1055), (2114, 1036)), ((2245, 1147), (2264, 1170)),
    ((2106, 1702), (2090, 1725)),  # Gooseneck down to the lift's top, Stampede's upper half up from it
    ((1703, 1295), (1683, 1318)),  # Schwarzstrasse down to where Martis leaves it, Washoe on from there
    # Home Run up to its top, Boondocks up to Lookout Bypass, Lookout Bypass up to Zephyr Lodge
    ((1248, 1384), (1272, 1366)), ((1432, 1278), (1459, 1265)),
    ((1326, 1283), (1352, 1268)),  # Lower Pioneer up to its sign, Upper Pioneer on up to Zephyr Lodge
    # Skid Trail to Lumberjack's top, Lumberjack to Lower Main Street's top, Lower Main Street to the line from
    # Easy Street at Big Springs, Village Run on down to the village
    ((1177, 770), (1174, 800)), ((924, 1249), (910, 1276)), ((706, 1524), (682, 1542)),
    ((1379, 844), (1405, 832)),  # Goldmine to where Upper Jibboom crosses it, Upper Jibboom up to West Ridge
    # Gateway up to Timber Line's foot; Timber Line up past its sign to the Lion's Way junction, where the outline's
    # centre line turns back down to Home Run's crossing and runs down Home Run's lower line (TRIMS)
    ((1100, 1926), (1076, 1909)), ((1010, 1590), (1008, 1563)),
    ((1002, 1842), (993, 1815)),  # the line from Timber Line's sign past The Glades', on round to Timber Line's foot
    ((1034, 1557), (1006, 1566)),  # Upper Lion's Way down to the Lion's Way junction, Overland Trail across to it
    ((2433, 1032), (2420, 1004)),  # Why Not from where it leaves Iron Horse's line (its diamond just below)
    # Northern Lights' outline drawn on down Christmas Tree's line, under CHRISTMAS, to the Lumberjack circle: cut at
    # Northern Lights' square, where it joins, and at the label's start (the rest is Christmas Tree's run-out)
    ((1360, 980), (1298, 1005)), ((1295, 1010), (1176, 1044)),
]
TRACED = []
TRIMS = [
    ((964, 1673), (990, 1657)),  # Home Run's lower line from its crossing, without the doubled stretch above it
    # runs whose outline goes on along another run's line to their common foot: cut where they join it
    ((1484, 628), (1350, 730)),  # Stump Alley, onto Luggi's line
    ((2047, 887), (2522, 1162)),  # Castle Peak, onto Drifter's (under DRIFTER)
]
