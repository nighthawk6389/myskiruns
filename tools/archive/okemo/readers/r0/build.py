import json
BASE='/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/okemo/'
MY=['t000','t100','t200','t001','t101','t201','t301','t401']
idx=json.load(open(BASE+'tiles/index.json'))
polys={p['id']:p for p in json.load(open('/home/user/myskiruns/src/data/resorts/okemo/linePolylines.json'))['polylines']}
tiles_of={}
for t in idx['tiles']:
    if t['tile'] in MY:
        for i in t['ids']: tiles_of.setdefault(i,[]).append(t['tile'])
# id: (name, confidence, note)
A={
 4:('DOUBLE DIAMOND','high','glade line inside the dark-grey DOUBLE DIAMOND band, below its label (left arm of the U-shaped band shared with OUTRAGE)'),
 5:('DOUBLE DIAMOND','high','glade line inside the DOUBLE DIAMOND band, above its label; starts at the Rim Rock ridge line (49)'),
 6:('OUTRAGE','high','glade line inside the dark-grey OUTRAGE band, below its label (right arm of the U-shaped band)'),
 7:('OUTRAGE','high','glade line inside the OUTRAGE band, above its label'),
 8:('LOOSE SPRUCE','high','glade line inside the LOOSE SPRUCE band, lower part'),
 9:('LOOSE SPRUCE','high','glade line inside the LOOSE SPRUCE band, upper part'),
 10:('FORREST BUMP','high','glade line inside the FORREST BUMP band, below its label'),
 11:('FORREST BUMP','high','glade line inside the FORREST BUMP band, above its label'),
 29:('DREAM WEAVER','high','continues from the DREAM WEAVER label up the ridge to the summit'),
 30:('DREAM WEAVER','high','from the circle of the DREAM WEAVER label down to the slow zone at the Sunshine Quad / South Face Express bottom'),
 31:('CAT NAP','high','from the square of the CAT NAP label down to the slow zone'),
 32:('CAT NAP','high','from the CAT NAP label up to Rim Rock (47)'),
 33:('OFF THE RIM','high','from the square of the OFF THE RIM label down-left until it meets Dream Weaver (30)'),
 34:('OFF THE RIM','high','from the OFF THE RIM label up to Rim Rock (48)'),
 35:('STUMP JUMPER','high','from the diamond of the STUMP JUMPER label down to the slow zone'),
 36:('STUMP JUMPER','high','from the STUMP JUMPER label up to Rim Rock (48)'),
 37:('PUNCH LINE','high','from the diamond of the PUNCH LINE label down to the slow zone'),
 38:('PUNCH LINE','high','from the PUNCH LINE label up to Rim Rock (48)'),
 39:('LOWER WILD THING','high','from the LOWER WILD THING label up to the Rim Rock crossing; collinear with 242 (UPPER WILD THING) above the crossing'),
 40:('LOWER WILD THING','high','from the diamond of the LOWER WILD THING label down to the South Face Express bottom'),
 41:('BLIND FAITH','high','from the diamond of the BLIND FAITH label down to Cat Nap'),
 42:('BLIND FAITH','high','from the BLIND FAITH label up to Rim Rock (48)'),
 43:('MOMENT\'S REST','high','continues below the MOMENT\'S REST label down to Rim Rock (47)'),
 44:('MOMENT\'S REST','high','short piece from the bottom of the Double Diamond/Outrage glade band to the square of the MOMENT\'S REST label'),
 45:('SPRINT','high','short piece from the SPRINT label end to the Glades Peak Quad line'),
 46:('SPRINT','high','short piece from the bottom of the Moment\'s Rest label to the square of the SPRINT label'),
 47:('RIM ROCK','high','continues from the lower RIM ROCK label down into the slow zone at the Glades Peak Quad bottom'),
 48:('RIM ROCK','high','between the upper RIM ROCK label (square) and the lower RIM ROCK label (square)'),
 49:('RIM ROCK','high','one continuous stroke from the upper RIM ROCK label along the ridge to the summit patrol hut; Upper Wild Thing, Moon Dog, Double Diamond, Outrage, Sundog and Upper Fall Line start from it, no other label on it'),
 50:('UPPER WILD THING','high','short piece above the UPPER WILD THING label, up to Rim Rock (49)'),
 51:('SUNCATCHER','high','leaves the slow zone (separate stroke from Dream Weaver 30) and runs into the upper end of the SUNCATCHER label; Rossi Run (241) branches off it'),
 52:('SUNCATCHER','high','from the circle of the SUNCATCHER label down to the Sunshine Quad base (Southface Village)'),
 53:('FALL LINE','high','from the square of the FALL LINE label down to the slow zone'),
 54:('FALL LINE','high','above the FALL LINE label up to the Upper Fall Line / Countdown junction'),
 55:('COUNTDOWN','high','ends at the square of the COUNTDOWN label (label itself is just right of my tiles, in t002); runs down-left to the bottom of Upper Fall Line'),
 57:('TRIPLESEC','high','from the diamond of the TRIPLESEC label down to Upper Fall Line (59)'),
 58:('TRIPLESEC','high','from Buckhorn down to the upper end of the TRIPLESEC label'),
 59:('UPPER FALL LINE','high','from the diamond of the UPPER FALL LINE label down to the Countdown junction'),
 60:('UPPER FALL LINE','high','short piece above the UPPER FALL LINE label, from the summit ridge'),
 61:('CHALLENGER','high','from the diamond of the CHALLENGER label down-left to Upper Fall Line'),
 63:('MUELLERS\' RUN','high','from the diamond of the MUELLERS\' RUN label down to the top of the SCOOTER label'),
 64:('MUELLERS\' RUN','high','short piece above the MUELLERS\' RUN label, up to Countdown (55)'),
 65:('SACHEM','high','from the lower SACHEM label down to a road crossing; continues as 69'),
 66:('SACHEM','high','from the circle of the upper SACHEM label down through Okemo Trailside to the circle of the lower SACHEM label; Home Stretch joins it'),
 67:('SACHEM','high','continues from the upper SACHEM label up-right into the slow zone'),
 69:('SACHEM','high','continues 65 after the road crossing, under the Sachem Quad, to the circle of a third SACHEM label (just right of my tiles)'),
 70:('HOME STRETCH','high','short piece from the HOME STRETCH label end to the bottom of Easy Street'),
 71:('HOME STRETCH','high','short piece from the circle of the HOME STRETCH label to Sachem (66)'),
 72:('EASY STREET','high','short piece below the EASY STREET label, meets Home Stretch'),
 73:('EASY STREET','high','short piece above the EASY STREET label, from the slow zone'),
 74:('LEDGES','high','from the LEDGES label down to the Sachem Quad bottom'),
 75:('LEDGES','high','above the diamond of the LEDGES label, beside the Sachem Quad'),
 77:('BUCKHORN','high','from the summit patrol hut down to the circle of the BUCKHORN label'),
 78:('UPPER WORLD CUP','high','from the diamond of the UPPER WORLD CUP label down to the blue trails near Red Fox Woods'),
 79:('UPPER WORLD CUP','high','from Countdown down to the top of the UPPER WORLD CUP label'),
 145:('UPPER MOUNTAIN ROAD','high','short piece from the summit patrol hut to the circle of the UPPER MOUNTAIN ROAD label'),
 149:('FAIRWAY','high','short piece before the circle of the FAIRWAY label (148 continues after the label)'),
 151:('OPEN SLOPE','high','separate line starting just below the FAIRWAY circle and running up-right to the circle of the OPEN SLOPE label (label outside my tiles, in t302); the FAIRWAY text is aligned with 149/148, not with this line'),
 208:('LINK','high','from the slow zone to the square of the LINK label (the SCOOTER label ends just above this square)'),
 209:('LINK','high','continues after the LINK label'),
 235:('MOON DOG','high','short piece below the square of the MOON DOG label, down to Rim Rock (49)'),
 236:('MOON DOG','high','short piece above the MOON DOG label, up to the summit'),
 240:('ROSSI RUN','high','from the circle of the ROSSI RUN label around Southface Village to the Sunshine Quad base'),
 241:('ROSSI RUN','high','from the ROSSI RUN label up to Suncatcher (51)'),
 242:('UPPER WILD THING','high','from the double diamond of the UPPER WILD THING label down to the Rim Rock crossing; 39 (LOWER WILD THING) continues below the crossing'),
}
missing=sorted(set(tiles_of)-set(A)); extra=sorted(set(A)-set(tiles_of))
assert not missing and not extra, (missing, extra)
lines=[]
for i in sorted(A):
    n,c,note=A[i]
    lines.append({'id':i,'mapName':n,'color':polys[i]['cls'],'confidence':c,'tiles':tiles_of[i],'note':note})
L=lambda n,s,g,x,y,note='': {'mapName':n,'symbol':s,'glade':g,'area':'okemo-mountain','labelSrc':[x,y],'note':note}
labels=[
 L('SUNDOG','circle',False,1350,362,'green; no drawn line of its own: the vertical label spans the short run from the summit down to the Rim Rock ridge line (49)'),
 L('MOON DOG','square',False,1260,385,'lines 235 and 236'),
 L('UPPER MOUNTAIN ROAD','circle',False,1586,417,'label runs right out of my tiles; line 145 before it'),
 L('BUCKHORN','circle',False,1547,455,'label runs right out of my tiles; line 77 before it'),
 L('RIM ROCK','square',False,1119,471,'upper of two RIM ROCK labels'),
 L('OUTRAGE','double-diamond',True,1300,478,'two diamonds + tree icon, checked on a zoomed vector render; dark-grey band'),
 L('UPPER FALL LINE','diamond',False,1396,492,'single diamond, checked on a zoomed vector render'),
 L('DOUBLE DIAMOND','double-diamond',True,1212,512,'two diamonds + tree icon, checked on a zoomed vector render; dark-grey band'),
 L('UPPER WILD THING','double-diamond',False,1124,510,'TWO diamonds (not a glade), checked on a zoomed vector render'),
 L('TRIPLESEC','diamond',False,1468,531,'single diamond, checked on a zoomed vector render'),
 L('DREAM WEAVER','circle',False,783,559),
 L('OFF THE RIM','square',False,850,586),
 L('CHALLENGER','diamond',False,1516,587,'single diamond, checked on a zoomed vector render'),
 L('COUNTDOWN','square',False,1603,598,'label itself is just right of my tiles (t002); included because piece 55 ends at its square'),
 L('STUMP JUMPER','diamond',False,852,645,'single diamond, checked on a zoomed vector render'),
 L('LOOSE SPRUCE','double-diamond',True,754,670,'two diamonds + tree icon, checked on a zoomed vector render; dark-grey band'),
 L('MUELLERS\' RUN','diamond',False,1476,711,'printed MUELLERS’ RUN; single diamond, checked on a zoomed vector render'),
 L('MOMENT\'S REST','square',False,1205,722,'printed MOMENT’S REST'),
 L('SPRINT','square',False,1266,762),
 L('PUNCH LINE','diamond',False,756,772,'single diamond, checked on a zoomed vector render'),
 L('RIM ROCK','square',False,1079,809,'lower of two RIM ROCK labels'),
 L('LOWER WILD THING','diamond',False,779,829,'single diamond, checked on a zoomed vector render'),
 L('FORREST BUMP','double-diamond',True,1009,855,'spelled FORREST; two diamonds + tree icon, checked on a zoomed vector render; dark-grey band'),
 L('BLIND FAITH','diamond',False,829,865,'single diamond, checked on a zoomed vector render'),
 L('FALL LINE','square',False,1298,872),
 L('UPPER WORLD CUP','diamond',False,1540,888,'single diamond, checked on a zoomed vector render'),
 L('DROP OFF','square',False,1482,900,'no drawn line: label sits in the gap between Muellers’ Run (63) and Upper World Cup (79/78)'),
 L('SCOOTER','square',False,1447,953,'no separate line piece: the vertical label spans from the bottom of Muellers’ Run (63) to the LINK square'),
 L('CAT NAP','square',False,794,989),
 L('LINK','square',False,1482,1007,'lines 208 and 209'),
 L('SACHEM','circle',False,1250,1029,'upper SACHEM label'),
 L('EASY STREET','none-visible',False,1418,1073,'green text and green line (72/73) but NO symbol printed at either end of the label (zoomed vector render)'),
 L('HOME STRETCH','circle',False,1363,1186),
 L('ROSSI RUN','circle',False,294,1236),
 L('SUNCATCHER','circle',False,415,1266),
 L('LEDGES','diamond',False,1492,1358,'single diamond, checked on a zoomed vector render'),
 L('SACHEM','circle',False,1348,1456,'lower SACHEM label (a third SACHEM label is just right of my tiles at ~[1567,1727])'),
 L('OPEN SLOPE','circle',False,1754,1828,'label outside my tiles (t302); included because piece 151 ends at its circle'),
 L('FAIRWAY','circle',False,1520,1900,'lines 149 (before) and 148 (after, outside my tiles)'),
 L('GALAXY BOWL','circle',False,1461,2051,'small green circle; two-line label beside carpets 2 and 3 at the Clock Tower base; no drawn trail line (carpet-served learning slope)'),
]
json.dump({'lines':lines,'labels':labels},open(BASE+'tiles/result_0.json','w'),indent=1,ensure_ascii=False)
print(len(lines),'lines',len(labels),'labels')
import collections
print(collections.Counter(l['symbol'] for l in labels))
print(collections.Counter(l['mapName'] for l in lines).most_common())
