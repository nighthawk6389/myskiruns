import json
TD = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/sugarbush/tiles'
OUT = TD + '/result_4.json'
MINE = ['t005', 't105', 't205', 't305', 't106', 't206']
idx = json.load(open(TD + '/index.json'))
tiles_of = {}
for t in idx['tiles']:
    if t['tile'] in MINE:
        for i in t['ids']:
            tiles_of.setdefault(i, []).append(t['tile'])

H, M = 'high', 'medium'
lines = [
 (60, 'WAY BACK', 'blue', H, "Blue line from the Way Back square/snowflake (3388,1213) SW, passes under the top of the NORTH RIDGE lift label, crosses LWR ELBOW's label/line (X crossing near 3330,1298, no junction) and ends in the Glen House plaza (3310,1342). One continuous stroke; the lower stretch carries no other name."),
 (68, 'LOWER F.I.S.', 'black', H, "Only its bottom run-out is in my tiles (t305: along the light-blue band west of Riemergasse/Snowflake, ending at 3579,2170). Followed it on the source: one continuous black line from (3027,1229) carrying two 'LOWER F.I.S.' labels, each with one diamond (~3035,1265 and ~3035,1825), down the Mt Ellen west boundary and around to the base; no other label or junction."),
 (69, 'LWR ELBOW', 'blue', H, "Blue line inline under the 'LWR ELBOW' text (square + snowflake at 3250,1240) ending at the North Ridge lift label box (3365,1324). WAY BACK (60) crosses it near the 'BOW' letters."),
 (72, 'EXTERMINATOR', 'black', H, "Thin black line under the 'EXTERMINATOR' text from the double diamond (~3322,1047) down to the LWR EXTERMINATOR single diamond (3442,1190) where 111 starts."),
 (74, 'BRAVO', 'black', H, "Lift-line trail on the right of the NORTH RIDGE EXPRESS QUAD; 'BRAVO' text inline with one diamond at (3291,1047). Lower end runs under the lift's red label box."),
 (75, 'WHICH WAY', 'blue', H, "Starts left of the North Ridge lift (3376,1377), crosses under it, inline through 'WHICH WAY' (square 3461,1454 + snowflake) and ends at the MAINSTREAM circle / slow zone (3541,1715)."),
 (76, 'WALT\'S TRAIL', 'green', H, "Starts at the Inverness summit (3920,1454), curves SW with no junction or other label to the inline 'WALT'S TRAIL' text (circle at its lower end 3652,1748), then continues down along the west side of Semi Tough Woods to the base near the KBRA T-bar bottom (3809,2031). The upper stretch is unlabeled but one continuous green line."),
 (77, 'TUMBLER', 'black', H, "From the Glen House plaza (3259,1421) down through the TUMBLER diamond (3262,1544) and inline 'TUMBLER' text, past Tumbler Woods, to the bottom of the Green Mountain Express (3458,1789)."),
 (78, 'SUGAR RUN', 'green', H, "Straight green line along the second orange terrain-park pill; 'SUGAR RUN' and its circle (3579,2047) are printed on the pill. Extends slightly past the pill's lower end (3742,2193)."),
 (79, 'STRAIGHT SHOT', 'green', H, "Straight green line just left of the Green Mountain Express lift, under the chair icon, inline through snowflake + circle (3612,1954) and 'STRAIGHT SHOT' text, ending near the base (3730,2114)."),
 (80, 'SNOWFLAKE', 'green', H, "Inline 'SNOWFLAKE' text with circle at its start (3577,2206); runs along the boundary to the base (3721,2293)."),
 (81, 'SEMI TOUGH', 'blue', H, "From beside the ski-school icon (3911,1545) down through the inline 'SEMI TOUGH' text (square at its lower end 3825,1728) to the KBRA T-bar bottom (3811,1998)."),
 (82, 'RIEMERGASSE', 'green', M, "Straight green line drawn on the orange terrain-park pill of the SUNSHINE QUAD (left of the red lift line, under the lift's red label and chair icon). No text is inline on it; the only trail label aligned with it is 'RIEMERGASSE' (snowflake, no difficulty symbol) printed parallel ~15 px to its SW, between GRADUATION's end and SNOWFLAKE's start. No other line fits that label."),
 (83, 'NORTHWAY', 'green', H, "Starts at the edge of the slow zone east of the North Ridge lift base (3452,1348), runs east along the light-blue band through the inline 'NORTHWAY' text (circle 3653,1377) to the Inverness summit (3898,1434)."),
 (84, 'NORTHRIDGE EXPRESSWAY', 'green', H, "From the Inverness summit (3902,1444) west along the inline 'NORTHRIDGE EXPRESSWAY' text (circle + snowflake at its west end 3633,1524) to the junction with Lwr Northstar (3586,1581)."),
 (85, 'SPLIT: NORTHSTAR / LWR NORTHSTAR', 'green', H, "NORTHSTAR from its start in the plaza west of the North Ridge lift (3366,1338), under the lift, through snowflake + circle (3523,1385) and the 'NORTHSTAR' text, down to the LWR NORTHSTAR circle at (3581,1520). The last ~45 px, (3581,1520)-(3578,1564), run through that circle and under the 'LWR' text = LWR NORTHSTAR (continues as 87). Split spec: 85@3581,1520=NORTHSTAR/LWR NORTHSTAR."),
 (86, 'MAINSTREAM', 'green', H, "Branches off Lwr Northstar (3573,1599); inline 'MAINSTREAM' text reading upward with its circle at the lower end (3544,1716), ends in the slow zone (3546,1733)."),
 (87, 'LWR NORTHSTAR', 'green', H, "From the Northridge Expressway junction (3578,1564) down through the rest of the inline 'LWR NORTHSTAR' text to the slow zone (3568,1740)."),
 (88, 'LOWER CRACKERJACK', 'green', H, "Continuation of 94 under the rest of the inline 'LOWER CRACKERJACK' text to the base (3746,2156)."),
 (89, 'JOE\'S CRUISER', 'blue', H, "Starts under the North Ridge lift (3395,1375), inline through square + snowflake (3485,1416) and 'JOE'S CRUISER' text, continues down to the slow zone (3568,1709)."),
 (90, 'INVERNESS', 'blue', H, "Straight blue line just east of the INVERNESS QUAD, inline 'INVERNESS' text with square + snowflake at its lower end (3958,1619); from the Inverness summit (3989,1478) to the base (3858,2049)."),
 (91, 'HAMMERHEAD', 'black', H, "From the Glen House plaza (3313,1412) through the HAMMERHEAD diamond (3344,1444) and inline text down to the lower slow zone (3493,1704); runs parallel to ENCORE (93) on its left."),
 (92, 'GRADUATION', 'green', H, "Starts under the 'WOODS' of the GRADUATION WOODS label (3445,2012), inline along the thin 'GRADUATION' text, circle printed just after the name (3540,2131), ends where RIEMERGASSE's label begins (3555,2128)."),
 (93, 'ENCORE', 'black', H, "From the plaza (3337,1392) through the ENCORE diamond (3388,1420) and inline text, down parallel to HAMMERHEAD on its right to (3496,1691)."),
 (94, 'SPLIT: CRACKERJACK / LOWER CRACKERJACK', 'green', H, "CRACKERJACK from the slow zone (3498,1832) through the circle (3487,1855) and inline 'CRACKERJACK' text down to the LOWER CRACKERJACK snowflake + circle (snowflake 3592,1988, circle 3606,2005). The last ~50 px from there to (3643,2041) run under 'LOWER CRA...' = LOWER CRACKERJACK (continues as 88). Split spec: 94@3598,1996=CRACKERJACK/LOWER CRACKERJACK."),
 (95, 'THE CLIFFS', 'black', H, "Straight black line just left (west) of the Green Mountain Express lift, inline 'THE CLIFFS' text with snowflake + one diamond (3304,1469) at its top, from the plaza (3281,1431) to (3472,1748)."),
 (96, 'BRAMBLES', 'blue', H, "From the Inverness summit (4007,1466) through the square (4045,1499) and inline 'BRAMBLES' text, down west of Brambles Woods to (3910,1943)."),
 (110, 'EASY DOES IT', 'green', H, "Short green line beside the EASY UP carpet; tiny inline 'EASY DOES IT' text with a snowflake at the bottom and a small circle at its top end (3771,2149)."),
 (111, 'LWR EXTERMINATOR', 'black', H, "From the LWR EXTERMINATOR single diamond (3442,1190) inline along 'LWR EXTERMINATOR' text to the Northway line (3524,1347)."),
]
out_lines = []
for pid, name, col, conf, note in lines:
    out_lines.append({'id': pid, 'mapName': name, 'color': col, 'confidence': conf,
                      'tiles': tiles_of.get(pid, []), 'note': note})
missing = sorted(set(tiles_of) - {l['id'] for l in out_lines})
extra = sorted({l['id'] for l in out_lines} - set(tiles_of))
print('ids in my tiles not reported:', missing, ' reported but not in my tiles:', extra)

GP = 'glade icon = tree pair (no trunk), same as most Mt Ellen glades'
labels = [
 ('BRAVO', 'diamond', False, [3302, 1090], 'one diamond at the top (3291,1047); inline on piece 74'),
 ('EXTERMINATOR', 'double-diamond', False, [3370, 1110], 'two diamonds (~3322,1047), checked at 10x; thin text inline on piece 72'),
 ('LWR EXTERMINATOR', 'diamond', False, [3484, 1265], 'one diamond (3442,1190), checked at 8x; inline on piece 111'),
 ('WAY BACK', 'square', False, [3400, 1228], 'snowflake + square (3388,1213); two-line label; line = piece 60'),
 ('LWR ELBOW', 'square', False, [3305, 1282], 'snowflake + square (3250,1240, just left of t005); inline on piece 69'),
 ('BRAVO WOODS', 'none-visible', True, [3283, 1153], 'glade, no line; label straddles the left edge of t005, icon at (3262,1070); ' + GP),
 ('BRAVINATOR WOODS', 'none-visible', True, [3365, 1150], 'glade, no line; icon at (3338,1102); ' + GP),
 ('EXTERMINATOR WOODS', 'none-visible', True, [3465, 1170], 'glade, no line; icon at (3383,1077); ' + GP),
 ('WAY BACK WOODS', 'none-visible', True, [3450, 1300], 'glade, no line; icon at (3422,1263); ' + GP),
 ('NORTHWAY', 'circle', False, [3717, 1387], 'circle (3653,1377); inline on piece 83'),
 ('NORTHSTAR', 'circle', False, [3570, 1433], 'snowflake + circle (3523,1385); inline on piece 85'),
 ("JOE'S CRUISER", 'square', False, [3519, 1497], 'snowflake + square (3485,1416); inline on piece 89'),
 ('WHICH WAY', 'square', False, [3485, 1513], 'snowflake + square (3461,1454); inline on piece 75'),
 ('ENCORE', 'diamond', False, [3406, 1466], 'one diamond (3388,1420), checked at 6x; inline on piece 93'),
 ('HAMMERHEAD', 'diamond', False, [3382, 1510], 'one diamond (3344,1444), checked at 6x; inline on piece 91'),
 ('THE CLIFFS', 'diamond', False, [3337, 1523], 'snowflake + one diamond (3304,1469), checked at 6x; inline on piece 95'),
 ('TUMBLER', 'diamond', False, [3289, 1591], 'one diamond (3262,1544, just left of t105), checked at 6x; inline on piece 77'),
 ('TUMBLER WOODS', 'none-visible', True, [3281, 1640], 'glade, no line; label straddles the left edge of t105/t205, icon at (3222,1552) outside my tiles; ' + GP),
 ('LWR NORTHSTAR', 'circle', False, [3595, 1610], 'circle (3581,1521) at its top; inline on the tail of 85 + piece 87'),
 ('MAINSTREAM', 'circle', False, [3559, 1652], 'circle + snowflake at the LOWER end of the upward-reading text (3544,1716); inline on piece 86'),
 ('NORTHRIDGE EXPRESSWAY', 'circle', False, [3765, 1482], 'snowflake + circle at its west end (3633,1524); inline on piece 84'),
 ("WALT'S WOODS", 'none-visible', True, [3685, 1618], 'glade, no line; icon at (3633,1670); ' + GP),
 ("WALT'S TRAIL", 'circle', False, [3690, 1680], 'circle at the lower end of the upward-reading text (3652,1748); inline on piece 76'),
 ('SEMI TOUGH WOODS', 'none-visible', True, [3762, 1700], 'glade, no line; icon at (3704,1797); ' + GP),
 ('SEMI TOUGH', 'square', False, [3840, 1655], 'square at the lower end of the upward-reading text (3825,1728); inline on piece 81'),
 ('INVERNESS', 'square', False, [3973, 1560], 'the trail label (not the INVERNESS area/elevation label); snowflake + square at its lower end (3958,1619); inline on piece 90'),
 ('BRAMBLES', 'square', False, [4053, 1550], 'square at its top (4045,1499); inline on piece 96'),
 ('BRAMBLES WOODS', 'none-visible', True, [4105, 1675], 'glade, no line; icon at (4046,1765); ' + GP),
 ('CRACKERJACK', 'circle', False, [3529, 1921], 'snowflake + circle (3487,1855); inline on piece 94 (upper part)'),
 ('STRAIGHT SHOT', 'circle', False, [3668, 2027], 'snowflake + circle (3612,1954); inline on piece 79'),
 ('LOWER CRACKERJACK', 'circle', False, [3678, 2080], 'snowflake + circle (3606,2005); inline on the tail of 94 + piece 88'),
 ('SUGAR RUN', 'circle', False, [3628, 2090], 'circle (3579,2047); name and circle printed ON an orange terrain-park pill; line = piece 78'),
 ('GRADUATION WOODS', 'none-visible', True, [3470, 2035], 'glade, no line; icon at (3437,1984); GRADUATION (92) starts under this label; ' + GP),
 ('GRADUATION', 'circle', False, [3478, 2085], 'circle printed just AFTER the name (3540,2131), on the text baseline; inline on piece 92'),
 ('RIEMERGASSE', 'none-visible', False, [3605, 2155], 'only a snowflake before the name (3548,2098); the nearby circle (3540,2131) belongs to GRADUATION. Label printed parallel to the SUNSHINE QUAD orange terrain-park pill, whose green line is piece 82; parks on this map may print no difficulty symbol'),
 ("ELLEN'S WOODS", 'none-visible', True, [3368, 2092], 'glade, no line; icon at (3284,2092) is a SINGLE upright tree with a trunk, unlike the tree-pair icon on every other glade in my tiles (and on Moose Run Woods); may or may not mean a different glade rating - no legend in the image'),
 ('SNOWFLAKE', 'circle', False, [3630, 2248], 'circle (3577,2206); inline on piece 80'),
 ('EASY DOES IT', 'circle', False, [3753, 2187], 'tiny label beside the EASY UP carpet; snowflake at the bottom, small circle at the top end (3771,2149); inline on piece 110'),
]
out_labels = [{'mapName': n, 'symbol': s, 'glade': g, 'area': 'mt-ellen', 'labelSrc': c, 'note': note}
              for n, s, g, c, note in labels]
json.dump({'lines': out_lines, 'labels': out_labels}, open(OUT, 'w'), indent=1, ensure_ascii=False)
print('wrote', OUT, len(out_lines), 'lines', len(out_labels), 'labels')
