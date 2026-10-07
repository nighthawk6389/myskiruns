import json
BASE='/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/okemo/'
idx=json.load(open(BASE+'tiles/index.json'))
mine=['t003','t103','t203','t303','t403']
tl={}
for t in idx['tiles']:
    if t['tile'] in mine:
        for i in t['ids']: tl.setdefault(i,[]).append(t['tile'])
L={p['id']:p for p in json.load(open('/home/user/myskiruns/src/data/resorts/okemo/linePolylines.json'))['polylines']}
A='okemo-mountain'
lines=[
(2,'TREE DANCER','high','glade line inside the blue-violet TREE DANCER band, above the label (label inline; continues as 3)'),
(3,'TREE DANCER','high','glade line after the TREE DANCER square+tree icon, inside its band, down to the Green Link / Mountain Road hub (~2810,1100)'),
(12,'WHISTLER','high','below the icons of the lower WHISTLER label, inside that glade band'),
(13,'WHISTLER','high','lower Whistler glade band above the lower WHISTLER label; continues 27 after it crosses the Sweet Solitude line'),
(14,'EVERGLADE','high','glade line after the EVERGLADE label (inline, continues 15)'),
(15,'EVERGLADE','high','right-hand fork of the glade band that starts at the upper WHISTLER label; runs to the EVERGLADE label, which is inline between 15 and 14'),
(16,'WHISPERING PINES','high','glade line after the WHISPERING PINES label, inside its band, ends at Easy Rider'),
(17,'WHISPERING PINES','high','glade line inside the WHISPERING PINES band from its top (~1948,484) to the label'),
(18,'UPPER ARROW','high','after the UPPER ARROW label end, down to Lower Mountain Road (Lower Arrow 204 continues below). No glade icon/band printed, although the PDF puts 18/19 in its "Tree Trails" layer'),
(19,'UPPER ARROW','high','from the junction at the end of Upper Timberline (~2095,985) to the square of UPPER ARROW'),
(20,'THE SHADOWS','high','glade line inside the dark-grey THE SHADOWS band, below the label'),
(21,'THE SHADOWS','high','glade line inside the dark-grey THE SHADOWS band, above the label'),
(26,'WHISTLER','high','head of the glade band just above-left of the upper WHISTLER label (inline); after the label the band forks into 27 (Whistler) and 15 (Everglade)'),
(27,'WHISTLER','high','left fork after the upper WHISTLER label icons; crosses the Sweet Solitude line and continues as 13 to the lower WHISTLER label'),
(99,'SEL\'S CHOICE','high','after the SEL\'S CHOICE label end'),
(100,'SEL\'S CHOICE','high','leads into the diamond of SEL\'S CHOICE'),
(106,'LOWER TIMBERLINE','high','after the LOWER TIMBERLINE label to the Evergreen Summit Express bottom terminal'),
(107,'LOWER TIMBERLINE','high','from the junction at the end of Upper Timberline (~2100,985) to the square of LOWER TIMBERLINE'),
(108,'UPPER TIMBERLINE','high','after the UPPER TIMBERLINE label end, to the junction where Upper Arrow (19) and Lower Timberline (107) start'),
(110,'CUTTER\'S FOLLY','high','after the CUTTER\'S FOLLY label end, to the Express Lane / Upper-Lower Sapphire junction (~2200,928)'),
(111,'CUTTER\'S FOLLY','high','leads into the square of CUTTER\'S FOLLY from beside the Evergreen Summit Express'),
(112,'LOWER SAPPHIRE','high','continuation of 113 below the Ridge Runner crossing, into the slow zone at Lower Mountain Road'),
(113,'LOWER SAPPHIRE','high','after the LOWER SAPPHIRE label end, down to Ridge Runner'),
(114,'LOWER SAPPHIRE','high','from the Express Lane / Cutter\'s Folly / Upper Sapphire junction (~2210,930) to the square of LOWER SAPPHIRE'),
(115,'UPPER SAPPHIRE','high','after the UPPER SAPPHIRE label end, to the junction at ~(2208,910)'),
(116,'UPPER SAPPHIRE','high','from just below the green spur 239 (~1975,630) to the square of UPPER SAPPHIRE'),
(117,'TOMAHAWK','high','blue trail: after the blue TOMAHAWK label, ends at Express Lane (~2256,887); the orange TOMAHAWK terrain-park line (255/254) is its fall-line continuation below Express Lane'),
(118,'TOMAHAWK','high','blue trail: leads into the square of the blue TOMAHAWK label; passes beside the FISHER CAT SLIDE kids-zone label (not a trail)'),
(119,'EXPRESS LANE','high','short stub from the EXPRESS LANE label end to the Solitude summit / lift top'),
(120,'EXPRESS LANE','high','below the square of EXPRESS LANE (label inline), to the junction with Cutter\'s Folly / Sapphire (~2206,928)'),
(121,'HEAVEN\'S GATE','high','after the HEAVEN\'S GATE label end, down to Green Link'),
(122,'HEAVEN\'S GATE','high','from the Express Lane label end at the summit to the square of HEAVEN\'S GATE'),
(123,'SCREAMIN\' DEMON','high','after the SCREAMIN\' DEMON label end'),
(124,'SCREAMIN\' DEMON','high','starts on Lower Mountain Road just below the ROAD end of its label, leads into the square of SCREAMIN\' DEMON'),
(125,'THE PLUNGE','high','after THE PLUNGE label end'),
(126,'THE PLUNGE','high','leads into the diamond of THE PLUNGE'),
(128,'BOOMERANG','high','starts at the Lower Mountain Road lift crossing (~2624,1194), runs beside the Solitude Express Quad into the square of the BOOMERANG label just east of my tiles (~2811,1494)'),
(129,'EXHIBITION','high','after the EXHIBITION label end, down toward Green Link'),
(130,'EXHIBITION','high','beside the Solitude Express Quad from the summit into the diamond of EXHIBITION'),
(134,'COLEMAN BROOK','high','after the COLEMAN BROOK label end, down to the hub near JACKSON GORE JUNCTION (~2817,1079)'),
(135,'COLEMAN BROOK','high','from the Solitude summit into the circle of COLEMAN BROOK'),
(136,'SWEET SOLITUDE','high','after the SWEET SOLITUDE label end to the summit first-aid cross'),
(137,'SWEET SOLITUDE','high','from the tip of the light-green band (~1931,560) into the circle of SWEET SOLITUDE; the unnamed spur 239 leaves it at ~(2045,609)'),
(138,'EASY RIDER','high','after the EASY RIDER label end to the junction with Upper Mountain Road (~2520,740)'),
(139,'EASY RIDER','high','from the tip of the light-green band (~1924,545) into the circle of EASY RIDER'),
(140,'LOWER MOUNTAIN ROAD','medium','no label on it: green road from the hub where the second MOUNTAIN ROAD label ends (~2820,1100) west-southwest to the Solitude Express Quad, where it lines up with 234 (LOWER MOUNTAIN ROAD, label inline) across the lift; Boomerang (128) starts in that gap. Could instead be the tail of MOUNTAIN ROAD'),
(142,'MOUNTAIN ROAD','high','from the Upper Mountain Road / Easy Rider junction (~2520,740) into the circle of the MOUNTAIN ROAD label (inline; the road continues east of my tiles)'),
(143,'UPPER MOUNTAIN ROAD','high','after the UPPER MOUNTAIN ROAD label end, along the ridge and down to the junction with Easy Rider (~2520,740)'),
(147,'ROUNDHOUSE RUN','high','from the Solitude summit into the circle of ROUNDHOUSE RUN'),
(150,'OPEN SLOPE','high','continues from the end of the OPEN SLOPE label (label just west of my tiles at ~1759,1827) up-right past the SUGAR HOUSE box to near Lower Mountain Road (~2211,1669)'),
(156,'KETTLE BROOK','high','after the KETTLE BROOK label end, up to the Homeward Bound / Gordon\'s Garden junction (~2065,1808)'),
(158,'LEDGEWOOD','high','from under the KETTLE BROOK text into the circle of LEDGEWOOD'),
(159,'LEDGEWOOD','high','after the LEDGEWOOD label end, up to Homeward Bound (~2208,1760); Snow Track (160) branches off it'),
(160,'SNOW TRACK','high','branches off Ledgewood (159) into the circle of SNOW TRACK; no drawn line after the label'),
(180,'VILLAGE RUN','high','after the VILLAGE RUN label end'),
(181,'VILLAGE RUN','high','from the corner of Lower Mountain Road at the foot of the SWITCHBACK label (~2320,1435) into the circle of VILLAGE RUN'),
(203,'LOWER MOUNTAIN ROAD','high','from the foot of Lower Arrow (~2177,1606) into the end of the second LOWER MOUNTAIN ROAD label (label just west of my tiles at ~1907,1714)'),
(204,'LOWER ARROW','high','from Lower Mountain Road (below Upper Arrow 18) down to the top of the vertical LOWER ARROW label'),
(205,'LOWER ARROW','high','below the circle of LOWER ARROW, down to Lower Mountain Road'),
(225,'HOMEWARD BOUND','high','from the Gordon\'s Garden / Kettle Brook junction (~2066,1802) into the circle of HOMEWARD BOUND'),
(226,'HOMEWARD BOUND','high','after the HOMEWARD BOUND label end, up to the top of the lift above it'),
(227,'RIDGE RUNNER','high','after the RIDGE RUNNER label end, down to Green Link'),
(228,'RIDGE RUNNER','high','from the Upper Arrow square (~2112,1134) east to the RIDGE RUNNER label; broken where it crosses Lower Timberline and the Evergreen Summit Express'),
(229,'GREEN LINK','high','one stroke from the circle of GREEN LINK west-southwest (Ridge Runner, Heaven\'s Gate and Exhibition end on it), hairpin at ~(2352,1240), back east to join Lower Mountain Road under its label at ~(2515,1214); the LOWER MOUNTAIN ROAD label is on the separate line 231-234, not on this return leg'),
(230,'GREEN LINK','high','after the GREEN LINK label end, east to the hub (~2810,1100)'),
(231,'LOWER MOUNTAIN ROAD','high','from the circle of LOWER MOUNTAIN ROAD (label inline between 234 and 231) west, hairpin near Broken Arrow, back east to Lower Arrow (~2201,1408)'),
(232,'LOWER MOUNTAIN ROAD','medium','no label on it: the road between 231 and 203 (both carry a LOWER MOUNTAIN ROAD label), broken only where Lower Arrow meets it at each end; the SWITCHBACK label ends at its corner (~2312,1435), where Village Run (181) starts'),
(234,'LOWER MOUNTAIN ROAD','high','after the ROAD end of the LOWER MOUNTAIN ROAD label, up-right to the Solitude Express Quad'),
(237,'DOUBLE DIPPER','high','after the DOUBLE DIPPER label, down into the slow zone at Lower Mountain Road'),
(239,'UNKNOWN','medium','short unnamed green spur leaving Sweet Solitude (137) at ~(2045,609) west to the heads of Upper Sapphire (116) and Tomahawk (118); no label on or near it (checked on crops)'),
(246,'PROGRESSION PARK','high','orange terrain-park stub after the PROGRESSION PARK label'),
(247,'PROGRESSION PARK','high','orange terrain-park stub before the pill of PROGRESSION PARK'),
(248,'THE ZONE','high','orange terrain-park stub after THE ZONE label'),
(249,'THE ZONE','high','orange terrain-park stub before the pill of THE ZONE'),
(250,'HALFPIPE','high','orange terrain-park stub after the HALFPIPE label'),
(251,'HALFPIPE','high','orange terrain-park stub before the pill of HALFPIPE'),
(252,'GORDON\'S GARDEN','high','orange terrain-park line from the end of the GORDON\'S GARDEN label (just west of my tiles, ~1874,1886) to the Homeward Bound / Kettle Brook junction (~2060,1808)'),
(254,'TOMAHAWK','high','ORANGE terrain-park line after the orange TOMAHAWK label (pill), not the blue trail; same printed name as the blue TOMAHAWK trail (118/117), whose line it continues below Express Lane'),
(255,'TOMAHAWK','high','ORANGE terrain-park line before the pill of the orange TOMAHAWK label, not the blue trail; starts just below Express Lane in line with blue TOMAHAWK 117'),
]
out_lines=[]
ids=set()
for i,name,conf,note in lines:
    assert i not in ids; ids.add(i)
    cls=L[i]['cls']
    out_lines.append({'id':i,'mapName':name,'color':cls,'confidence':conf,'tiles':tl[i],'note':note})
missing=set(tl)-ids
extra=ids-set(tl)
print('missing',sorted(missing),'extra',sorted(extra))
labels=[
('UPPER MOUNTAIN ROAD','circle',False,[2084,507],''),
('WHISTLER','square',True,[2055,589],'upper WHISTLER label (square + glade icon) at the head of the glade band'),
('EASY RIDER','circle',False,[2199,605],''),
('WHISPERING PINES','square',True,[2305,605],'square + glade icon'),
('WHISTLER','square',True,[2178,725],'second (lower) WHISTLER label on the same glade, square + glade icon'),
('SWEET SOLITUDE','circle',False,[2272,744],''),
('EVERGLADE','square',True,[2422,762],'square + glade icon'),
('TOMAHAWK','square',False,[2147,768],'blue trail label (square); an orange terrain park with the same name is printed below Express Lane'),
('UPPER SAPPHIRE','square',False,[2109,789],''),
('EXPRESS LANE','square',False,[2303,880],''),
('CUTTER\'S FOLLY','square',False,[2123,889],''),
('MOUNTAIN ROAD','circle',False,[2808,889],'label straddles the east edge of my tiles; a second MOUNTAIN ROAD label is further east at ~(2905,1065)'),
('UPPER TIMBERLINE','square',False,[2046,900],''),
('ROUNDHOUSE RUN','circle',False,[2711,908],'west of the JACKSON GORE JUNCTION sign'),
('RT. 103','square',False,[2160,956],'no drawn line of its own: the label spans the short connector from the Cutter\'s Folly / Express Lane junction (~2200,930) down-left to the end of Upper Timberline (~2100,985)'),
('COLEMAN BROOK','circle',False,[2722,981],'west of the JACKSON GORE JUNCTION sign; the line ends at the hub beside it'),
('TREE DANCER','square',True,[2676,1012],'square + glade icon'),
('TOMAHAWK','none-visible',False,[2348,1022],'ORANGE terrain-park label with orange pill (freestyle), not the blue square TOMAHAWK trail; lines 255/254'),
('EXHIBITION','diamond',False,[2532,1031],'one diamond (checked zoomed)'),
('LOWER SAPPHIRE','square',False,[2267,1040],''),
('HEAVEN\'S GATE','square',False,[2438,1041],''),
('GREEN LINK','circle',False,[2708,1107],''),
('RIDGE RUNNER','circle',False,[2307,1140],''),
('LOWER TIMBERLINE','square',False,[2209,1145],''),
('UPPER ARROW','square',False,[2132,1181],''),
('DOUBLE DIPPER','square',False,[2240,1242],''),
('SEL\'S CHOICE','diamond',False,[2084,1244],'one diamond (checked zoomed)'),
('LOWER MOUNTAIN ROAD','circle',False,[2470,1249],'a second LOWER MOUNTAIN ROAD label is just west of my tiles at ~(1907,1714)'),
('BROKEN ARROW','diamond',True,[2143,1312],'one diamond + glade icon (checked zoomed); dark-grey glade band with NO drawn line'),
('SWITCHBACK','circle',False,[2308,1377],'no drawn line of its own: the vertical label runs from Lower Mountain Road (~2296,1325) down to the road\'s corner at ~(2312,1435), where Village Run starts'),
('THE SHADOWS','diamond',True,[2379,1385],'one diamond + glade icon (checked zoomed)'),
('THE PLUNGE','diamond',False,[2506,1461],'one diamond (checked zoomed)'),
('LOWER ARROW','circle',False,[2202,1483],''),
('BOOMERANG','square',False,[2811,1494],'just east of my tiles; line 128 leads into it'),
('SCREAMIN\' DEMON','square',False,[2672,1506],''),
('THE ZONE','none-visible',False,[2118,1510],'orange terrain park (pill), freestyle'),
('HALFPIPE','none-visible',False,[2108,1546],'orange terrain park (pill), freestyle'),
('PROGRESSION PARK','none-visible',False,[2059,1542],'orange terrain park (pill), freestyle'),
('VILLAGE RUN','circle',False,[2559,1594],''),
('HOMEWARD BOUND','circle',False,[2176,1752],''),
('SNOW TRACK','circle',False,[2278,1856],''),
('LEDGEWOOD','circle',False,[2103,1925],'green trail label; the light-blue LEDGEWOOD box below it is a building, not a trail'),
('KETTLE BROOK','circle',False,[1988,1934],'label straddles the west edge of my tiles; the dark-blue KETTLE BROOK box is a building, not a trail'),
]
out_labels=[{'mapName':n,'symbol':s,'glade':g,'area':A,'labelSrc':p,'note':note} for n,s,g,p,note in labels]
res={'lines':out_lines,'labels':out_labels}
json.dump(res,open(BASE+'tiles/result_2.json','w'),indent=1)
from collections import Counter
print(len(out_lines),'lines',Counter(l['mapName'] for l in out_lines).most_common(5))
print(len(out_labels),'labels',Counter(l['symbol'] for l in out_labels))
print(Counter(l['confidence'] for l in out_lines))
