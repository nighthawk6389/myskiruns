import json, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/sugarbush/r1')
from labels_draft import L as LABELS
TD = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/sugarbush/tiles'
idx = json.load(open(f'{TD}/index.json'))
mine = ['t001', 't101', 't201', 't301']
tiles_of = {}
for t in idx['tiles']:
    if t['tile'] in mine:
        for i in t['ids']:
            tiles_of.setdefault(i, []).append(t['tile'])

lines = [
 (0, 'VALLEY HOUSE TRAVERSE', 'blue', 'high', "label (blue square) printed along it on a light-blue band at ~(680,1380), just left of t001/t101; runs from beside the Super Bravo top / info icon (802,1314) SW to the Valley House Quad top"),
 (1, "STEIN'S RUN", 'black', 'high', "label with snowflake + two diamonds on it at (835,1724); runs from Heaven's Gate Traverse near the Valley House top (637,1483), between Stein's Woods and Egan's Woods, to the Super Bravo / Valley House base"),
 (3, 'SPRING FLING', 'blue', 'high', "label (snowflake, blue square) on it at ~(490,1875), left of my tiles; straight line down to the Valley House Lodge base area"),
 (4, 'SPILLSVILLE', 'black', 'high', "leaves the Jester line at (843,1055), crosses Organgrinder, SPILLSVILLE label (one diamond) right after the crossing; ends just left of the Heaven's Gate lift (1156,1238) by the top of Paradise Extension"),
 (5, "SIGI'S RIPCORD", 'black', 'high', "label with two diamonds on it; ends at (1201,1228) where Paradise (8) also ends and LWR RIPCORD (16) begins"),
 (6, "RACER'S EDGE", 'blue', 'high', "label (snowflake, blue square, race icon) on it at ~(630,2190), left of t301; ends at the Valley House Lodge base area"),
 (7, 'PARADISE EXTENSION', 'black', 'high', "two-line label with one diamond along it; from just left of the Heaven's Gate lift (1178,1252) down to Downspout (1130,1394)"),
 (8, 'PARADISE', 'black', 'high', "label with two diamonds on it; Lower Paradise (17) forks off at (1228,1120); the last ~85px continue unlabeled to the lift line (1204,1203) where Sigi's Ripcord also ends and 16 / 7 begin"),
 (9, 'ORGANGRINDER', 'black', 'high', "label (snowflake, one diamond) on it; summit down to the Downspout crossing (1006,1286), continues as LOWER ORGANGRINDER (18)"),
 (10, "MURPHY'S GLADE", 'blue', 'medium', "two parallel lines at the MURPHY'S GLADE label: 11 (east) and this one (west) merge at (822,1487); below the merge this line carries the end of the label ('...S GLADE') down to the Super Bravo lift (930,1629). Its upper ~130px (737,1372)-(822,1487) is an unlabeled parallel branch off the Valley House Traverse, taken as part of the glade"),
 (11, "MURPHY'S GLADE", 'blue', 'high', "the label starts on this line (snowflake, blue square at (803,1438)); from below the Valley House Traverse, merges into 10 at (822,1487)"),
 (13, 'THE MALL', 'black', 'high', "label with one diamond on it at ~(700,1680), left of t101/t201; runs beside the Valley House Quad lift down to its base (1038,2159)"),
 (14, 'LOWER TWIST', 'black', 'high', "label with one diamond on it at ~(700,1850), left of t201; ends at the Valley House Quad base (892,1975)"),
 (16, 'LWR RIPCORD', 'black', 'high', "printed 'LWR RIPCORD'; begins where Sigi's Ripcord (5) and Paradise (8) end (1201,1235) and runs down the right side of the Heaven's Gate lift to its base (1361,1531); Lower Paradise (17) joins at the snowflake (1283,1365) right above the label's diamond"),
 (17, 'LOWER PARADISE', 'black', 'high', "forks off Paradise at (1228,1120) with one diamond; label along it; joins LWR RIPCORD (16) at (1283,1362)"),
 (18, 'LOWER ORGANGRINDER', 'black', 'high', "continues Organgrinder (9) below the Downspout crossing; label (snowflake, one diamond) on it; ends at the Super Bravo base (1100,1916)"),
 (19, 'LOWER MOONSHINE', 'blue', 'high', "continues from the MOONSHINE label end (528,1818); LOWER MOONSHINE label (blue square) on it at (758,1963)-(902,2115); ends at the Valley House base"),
 (20, 'LOWER JESTER', 'blue', 'high', "starts at Allyn's Lodge (864,1293) where 26 arrives; Downspout (31) leaves at (940,1293); loops down through both LOWER JESTER labels (1002,1592) and (1335,1797); Header (29) leaves at (1286,1890); ends in the Super Bravo base slow zone (1153,1967)"),
 (21, 'LOWER DOWNSPOUT', 'blue', 'high', "continues Downspout (31) from the Heaven's Gate lift base; label (snowflake, blue square) along it; ends joining Lower Jester (20) at (1382,1782)"),
 (22, 'LOWER DOMINO', 'blue', 'high', "starts just below Heaven's Gate Traverse (1248,1593), continuing Domino (33); label with blue square along it"),
 (23, 'LOWER BIRDLAND', 'black', 'high', "black line beside the Super Bravo lift below Birdland (36); label with one diamond along it; ends at the Super Bravo base"),
 (25, 'JESTER', 'blue', 'high', "JESTER label (snowflake, blue square) on it at the summit; runs down the west ridge (Spillsville 4 leaves at (843,1055)); at (800,1234) piece 26 forks off to Allyn's Lodge. The last ~60px (800,1234)-(807,1293) continue to the Valley House Traverse start, and the small two-line ALLYN'S TRAVERSE label (~765,1265) is printed right beside that tail: the tail may be Allyn's Traverse (it is one PDF stroke with Jester, so not split here)"),
 (26, 'JESTER', 'blue', 'medium', "unlabeled connector from the Jester fork (800,1234) past the Allyn's Lodge icons to (864,1293), where Lower Jester (20) starts; taken as the end of Jester at the lodge (it could equally be the head of Lower Jester)"),
 (27, "HEAVEN'S GATE TRAVERSE", 'blue', 'high', "second (east) HEAVEN'S GATE TRAVERSE label on it; from Lower Organgrinder (1067,1583) east to the arrowhead at the Heaven's Gate lift base (1358,1572)"),
 (28, "HEAVEN'S GATE TRAVERSE", 'blue', 'high', "first (west) label (blue square) on it at (594-833,1456-1526); from the Valley House Quad top (586,1459) east across Murphy's Glade, Birdland, the Super Bravo lift and Lower Jester to Lower Organgrinder (1064,1579), continuing as 27"),
 (29, 'HEADER', 'blue', 'high', "from Lower Jester (1286,1890) to Castlerock Runout (1379,1933); label with blue square along it"),
 (30, 'GONDOLIER', 'green', 'high', "label (snowflake, green circle) along it; from the Super Bravo base slow zone down to Lincoln Peak Village"),
 (31, 'DOWNSPOUT', 'blue', 'high', "leaves Lower Jester at (940,1293) by Allyn's Lodge; label (snowflake, blue square) along it; ends at the Heaven's Gate lift base (1353,1546), continuing as LOWER DOWNSPOUT (21)"),
 (32, 'DOMINO CHUTE', 'blue', 'high', "short line under the two-line label (snowflake, blue square), from below Allyn's Lodge back into Lower Jester (992,1396)"),
 (33, 'DOMINO', 'black', 'high', "starts beside Lower Organgrinder (1043,1430); label with one diamond on it (the diamond just below the LEW'S LINE tree icon); ends at Heaven's Gate Traverse (1233,1580), continuing as LOWER DOMINO (22)"),
 (34, 'COFFEE RUN', 'green', 'high', "label (snowflake, green circle) along it; from the Super Bravo base slow zone down to Lincoln Peak Village"),
 (35, "CAT'S MEOW", 'blue', 'high', "label (blue square) on it at ~(765,2311), mostly left of t301; ends at the Valley House Lodge base area"),
 (36, 'BIRDLAND', 'blue', 'high', "blue line on the right of the Super Bravo lift from its top (848,1334); label (snowflake, blue square) along it; ends at (950,1616) where Lower Birdland (23) starts"),
 (42, 'SUGARBEAR RD', 'green', 'high', "label (snowflake, green circle) along it; label straddles the right edge of t301"),
 (43, 'SUGARBEAR FOREST', 'green', 'high', "short line from Sugarbear Rd down to the SUGARBEAR FOREST green circle (1520,2237)"),
 (45, 'SLEEPER RD', 'blue', 'high', "leaves Sleeper (47) at (1413,2004) heading east; label with blue square on it"),
 (47, 'SLEEPER', 'blue', 'high', "carries both SLEEPER labels (upper ~(1670,1770), lower (1505,1940)); below the Sleeper Rd junction (1411,2004) it continues unlabeled down to the Lincoln Peak Village base (1275,2256)"),
 (52, 'OUT ROAD', 'green', 'high', "the piece traces the blue edge of a two-tone green/blue road stroke; OUT ROAD label with green circle on it"),
 (55, 'LWR HOT SHOT', 'blue', 'high', "printed 'LWR HOT SHOT'; label (snowflake, blue square) along it, beside the Gate House Express"),
 (56, 'IN ROAD', 'green', 'high', "label (green circle) on it; text continues right of t301"),
 (58, 'FIRST TIME', 'green', 'high', "green line just below the Welcome Mat carpet; label (snowflake, green circle) along it"),
 (59, 'EASY RIDER', 'green', 'high', "long green line beside the Schoolhouse Lift; the EASY RIDER label (snowflake, green circle at ~(1613,2242)) sits on it just right of t301"),
 (100, 'LOWER LIFT LINE', 'black', 'high', "continues 102 below the Cotillion crossing (1653,1358) down the right side of the Castlerock Double; LOWER LIFT LINE label (one diamond at its lower end) along it; mostly right of t101/t201"),
 (101, 'LOWER CASTLEROCK RUN', 'black', 'high', "starts at the foot of Castlerock Run where Troll Road leaves (1520,1189); label with one diamond (at the label's lower end) along it; ends at the Castlerock Double base (1533,1620)"),
 (104, 'CASTLEROCK RUNOUT', 'blue', 'high', "from the Castlerock Double base (arrowhead at (1507,1747)) down to Lincoln Peak Village; CASTLEROCK RUNOUT label (blue square) along its lower half"),
 (105, 'CASTLEROCK RUN', 'black', 'high', "label with one diamond on it; from the Castlerock summit down to the Troll Road junction (1528,1180); only its foot is inside t001"),
 (106, 'UNKNOWN', 'blue', 'high', "unnamed connector: ~70px spur with an arrowhead from Lower Downspout (21) at (1434,1721) to the Castlerock Double bottom terminal; nothing printed on it (checked at 3x)"),
 (107, 'CASTLEROCK CONNECTION', 'blue', 'high', "from the Castlerock Double base (1521,1719) east to the arrowhead (1821,1660); label with blue square along it; mostly right of my tiles"),
 (108, 'BAILOUT', 'blue', 'high', "starts beside Lower Castlerock Run (1437,1299); label with blue square on a light-blue band; crosses under the Heaven's Gate lift to (1263,1475) just above Downspout"),
 (109, 'TROLL ROAD', 'blue', 'high', "from the Castlerock Run / Lower Castlerock Run junction (1537,1195): both TROLL ROAD labels (blue square) lie on its switchbacks under the Castlerock Double; ends at Castlerock Connection (1650,1608); only its start is inside t001"),
]
ids_mine = sorted(tiles_of)
assert sorted(i for i, *_ in lines) == ids_mine, (sorted(i for i, *_ in lines), ids_mine)
out_lines = [{'id': i, 'mapName': n, 'color': c, 'confidence': conf, 'tiles': tiles_of[i], 'note': note}
             for i, n, c, conf, note in lines]
out_labels = [{'mapName': n, 'symbol': s, 'glade': g, 'area': 'lincoln-peak', 'labelSrc': [int(x), int(y)], 'note': note}
              for n, s, g, (x, y), note in LABELS]
res = {'lines': out_lines, 'labels': out_labels}
json.dump(res, open(f'{TD}/result_1.json', 'w'), indent=1)
from collections import Counter
print(len(out_lines), 'lines', Counter(l['confidence'] for l in out_lines), '|', len(out_labels), 'labels',
      Counter(l['symbol'] for l in out_labels), 'glades', sum(l['glade'] for l in out_labels))
