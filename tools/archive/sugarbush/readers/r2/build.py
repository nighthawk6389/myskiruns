import json
T='/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/sugarbush/tiles'
idx=json.load(open(T+'/index.json'))
mine=['t002','t102','t202','t302']
tiles={}
for t in idx['tiles']:
    if t['tile'] in mine:
        for i in t['ids']:
            tiles.setdefault(i,[]).append(t['tile'])
H='high'
L=[
(21,'LOWER DOWNSPOUT','blue',H,'LOWER DOWNSPOUT printed along it (blue square at its top, ~1404,1569); runs from the 16/31 junction down to the LOWER JESTER junction (piece 20)'),
(37,'SUNRISE','black',H,'from the North Lynx summit, curves down then runs straight along the SUNRISE label (single diamond) to the North Lynx base; no other label on it'),
(38,'MORNING STAR','black',H,'straight line just right of North Lynx Triple, MORNING STAR printed inline (single diamond); summit to base'),
(39,'BIRCH RUN','blue',H,'left of North Lynx Triple, BIRCH RUN printed inline (blue square); ends where CASTLEROCK CONNECTION starts'),
(40,'WATER FALL','black',H,'printed WATER FALL with a word gap (could be spelled WATERFALL); black middle section of the line beside Gate House Express Quad: blue HOT SHOT (57) above, LWR HOT SHOT (55) below; single diamond'),
(41,'VILLAGE RUN','blue',H,'VILLAGE RUN (blue square) with the caption TO CONDOS and an arrow; from the North Lynx base east then down to the condos'),
(42,'SUGARBEAR RD','green',H,'SUGARBEAR RD printed inline (green circle)'),
(43,'SUGARBEAR FOREST','green',H,'short green line from SUGARBEAR RD down past the SUGARBEAR FOREST label (green circle; bold lettering but no glade icon/hatch)'),
(44,'SLOWPOKE','blue',H,'blue line running along an orange terrain-park pill with SLOWPOKE (blue square) printed on it; from the PUSHOVER/LWR PUSHOVER junction down to SUGARBEAR RD'),
(45,'SLEEPER RD','blue',H,'SLEEPER RD printed inline (blue square at its west end); from SLEEPER (47) east to the WATER FALL/LWR HOT SHOT/OVER SHOT junction'),
(46,'SLEEPER CHUTES','black',H,'SLEEPER CHUTES printed inline (single diamond); leaves near the top of SLEEPER and rejoins it lower down'),
(47,'SLEEPER','blue',H,'two SLEEPER labels (both blue square) along it; continues past the SLEEPER RD junction to the Lincoln Peak base with no other label'),
(48,'SECOND THOUGHTS','blue',H,'short line with SECOND THOUGHTS (blue square) printed directly below it; the only line there'),
(49,'PUSHOVER','green',H,'PUSHOVER printed inline (green circle) on the green line in the yellow slow zone; continues as LWR PUSHOVER (54)'),
(50,'PUSHOVER CHUTE','blue',H,'PUSHOVER CHUTE (blue square) printed along it; short blue line ending at PUSHOVER'),
(51,'OVER SHOT','blue',H,'printed OVER SHOT (two words, blue square); from the PUSHOVER junction west to the WATER FALL/LWR HOT SHOT junction'),
(52,'OUT ROAD','green',H,'OUT ROAD (green circle) is drawn as a green line with a thin blue line alongside; this piece follows the blue edge of that same line'),
(53,'OUT TO LUNCH','green',H,'from the end of LWR PUSHOVER, curves down then runs along OUT TO LUNCH (green circle); no other label'),
(54,'LWR PUSHOVER','green',H,'LWR PUSHOVER printed inline (green circle); continuation of PUSHOVER below the OVER SHOT/SLOWPOKE junction'),
(55,'LWR HOT SHOT','blue',H,'LWR HOT SHOT printed inline (blue square) beside Gate House Express Quad'),
(56,'IN ROAD','green',H,'IN ROAD printed inline (green circle)'),
(57,'HOT SHOT','blue',H,'HOT SHOT printed inline (blue square); from the North Lynx base (info/first-aid icons) down to where the line turns black (WATER FALL, 40)'),
(58,'FIRST TIME','green',H,'FIRST TIME printed along it (green circle), beside the WELCOME MAT carpet'),
(59,'EASY RIDER','green',H,'EASY RIDER printed inline (green circle) above Village Quad; runs on to the Schoolhouse Lift area with no other label'),
(97,'RUMBLE','black',H,'leaves LIFT LINE near the top, RUMBLE printed inline (double diamond), ends on COTILLION'),
(98,'UNKNOWN','black','low','unnamed 29px connector from the RUMBLE line west to the LIFT LINE line (~1785,1067 to 1758,1078); no label; likely a second entrance to RUMBLE'),
(99,'MIDDLE EARTH','black',H,'from Castlerock summit east along the ridge, then down with MIDDLE EARTH printed inline (single diamond), continuous to CASTLEROCK CONNECTION with no other label'),
(100,'LOWER LIFT LINE','black',H,'LOWER LIFT LINE printed inline (single diamond); continuation of LIFT LINE below the COTILLION crossing, down to the Castlerock Double base'),
(101,'LOWER CASTLEROCK RUN','black',H,'LOWER CASTLEROCK RUN printed inline; single diamond after the name at the line\'s lower end'),
(102,'LIFT LINE','black',H,'LIFT LINE printed inline (double diamond) just right of Castlerock Double; summit down to where COTILLION crosses (~1652,1357), then continues as LOWER LIFT LINE (100)'),
(103,'COTILLION','black',H,'COTILLION printed inline (single diamond); crosses LIFT LINE/LOWER LIFT LINE and runs on to CASTLEROCK CONNECTION'),
(104,'CASTLEROCK RUNOUT','blue',H,'CASTLEROCK RUNOUT label (blue square ~1202,2115) is on its lower half, left of my tiles; the upper half from the Castlerock Double base (arrow) is the same continuous line (HEADER, 29, merges mid-way)'),
(105,'CASTLEROCK RUN','black',H,'from the Castlerock Warming Hut down, CASTLEROCK RUN printed inline (single diamond); ends at the TROLL ROAD junction where LOWER CASTLEROCK RUN begins'),
(106,'UNKNOWN','blue','low','unnamed 67px spur with an arrow from LOWER DOWNSPOUT\'s line east to the Castlerock Double base / top of CASTLEROCK RUNOUT; no label (could be counted as part of LOWER DOWNSPOUT)'),
(107,'CASTLEROCK CONNECTION','blue',H,'CASTLEROCK CONNECTION printed inline (blue square at its west end); North Lynx base west to the Castlerock Double base'),
(108,'BAILOUT','blue',H,'BAILOUT printed inline (blue square ~1317,1356), label just left of my tiles'),
(109,'TROLL ROAD','blue',H,'two TROLL ROAD labels (both blue square) along this winding line, from the CASTLEROCK RUN/LOWER CASTLEROCK RUN junction to CASTLEROCK CONNECTION'),
(113,'HI & LO ROAD','black',H,'U-shaped loop off CASTLEROCK RUN with HI & LO ROAD (single diamond) printed inside it'),
]
lines=[{'id':i,'mapName':n,'color':c,'confidence':cf,'tiles':tiles[i],'note':nt} for i,n,c,cf,nt in L]
assert sorted(tiles)==sorted(i for i,*_ in L), (sorted(tiles), sorted(i for i,*_ in L))
A='lincoln-peak'
LB=[
('CASTLEROCK RUN','diamond',False,[1608,1079],'single diamond before the name (~1529,1140)'),
('HI & LO ROAD','diamond',False,[1687,1087],'two-line label inside the loop of its line'),
('LIFT LINE','double-diamond',False,[1770,1038],'two stacked diamonds before the name (~1746,1096)'),
('RUMBLE','double-diamond',False,[1764,1160],'two stacked diamonds before the name (~1731,1212)'),
('MIDDLE EARTH','diamond',False,[1897,1149],''),
('TROLL ROAD','square',False,[1604,1222],'upper of two TROLL ROAD labels'),
('TROLL ROAD','square',False,[1727,1401],'lower of two TROLL ROAD labels'),
('COTILLION','diamond',False,[1633,1344],''),
('LOWER CASTLEROCK RUN','diamond',False,[1478,1470],'single diamond printed after the name (~1525,1611)'),
('LOWER LIFT LINE','diamond',False,[1594,1546],''),
('CASTLEROCK CONNECTION','square',False,[1672,1622],''),
('BIRCH RUN','square',False,[2094,1408],'snowflake before the square'),
('MORNING STAR','diamond',False,[2140,1426],''),
('SUNRISE','diamond',False,[2104,1531],'snowflake before the diamond'),
('LOWER DOWNSPOUT','square',False,[1446,1665],'label straddles the left edge of t102/t202'),
('WILD TURKEY','none-visible',True,[1405,1647],'glade (tree icon + red hatch); label mostly left of my tiles, partly visible at t102 left edge'),
('WITCH HAZEL','none-visible',True,[1410,1818],'glade (tree icon + red hatch); label mostly left of my tiles, partly visible at t202 left edge'),
('SLEEPER','square',False,[1677,1778],'upper of two SLEEPER labels'),
('SLEEPER','square',False,[1512,1938],'lower of two SLEEPER labels'),
('SLEEPER CHUTES','diamond',False,[1701,1815],''),
('HOT SHOT','square',False,[1810,1774],''),
('PUSHOVER CHUTE','square',False,[1873,1795],'two-line label'),
('SECOND THOUGHTS','square',False,[1835,1873],'two-line label below its short line'),
('PUSHOVER','circle',False,[1909,1862],''),
('DEEPER SLEEPER','none-visible',True,[1613,1907],'glade: bold name, tree icon and red hatch between SLEEPER CHUTES and WATER FALL; no line of its own'),
('WATER FALL','diamond',False,[1680,1897],'printed with a word gap (WATER FALL); may be spelled WATERFALL'),
('SLEEPER RD','square',False,[1500,2006],''),
('OVER SHOT','square',False,[1751,1980],'printed as two words'),
('SLOWPOKE','square',False,[1727,2058],'printed on an orange terrain-park pill (park)'),
('LWR PUSHOVER','circle',False,[1858,2058],''),
('VILLAGE RUN','square',False,[2216,1937],'caption TO CONDOS with an arrow under it (not part of the name); label straddles the right edge of t202'),
('LWR HOT SHOT','square',False,[1480,2085],''),
('SUGARBEAR RD','circle',False,[1574,2182],''),
('SUGARBEAR FOREST','circle',False,[1573,2217],'bold two-line label with a green line, no glade icon or hatch'),
('EASY RIDER','circle',False,[1670,2208],''),
('FIRST TIME','circle',False,[1456,2280],''),
('OUT TO LUNCH','circle',False,[1725,2317],''),
('IN ROAD','circle',False,[1573,2388],''),
('OUT ROAD','circle',False,[1518,2405],''),
]
labels=[]
for n,s,g,p,nt in LB:
    e={'mapName':n,'symbol':s,'glade':g,'area':A,'labelSrc':p,'note':nt}
    if n=='SLOWPOKE': e['park']=True
    labels.append(e)
out={'lines':lines,'labels':labels}
json.dump(out,open(T+'/result_2.json','w'),indent=1)
print(len(lines),'lines',len(labels),'labels')
