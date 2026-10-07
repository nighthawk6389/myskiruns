import json, sys
d = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/printed.json'))
x0, y0, x1, y1 = map(float, sys.argv[1].split(','))
S = 2.5
for l in d['labels']:
    cx, cy = l['c'][0]*S, l['c'][1]*S
    if x0 <= cx <= x1 and y0 <= cy <= y1:
        p0 = l['pts'][0]; p1 = l['pts'][-1]
        print(f"{l['text']!r:32} {l['color']:6} c=({cx:.0f},{cy:.0f}) first=({p0[0]*S:.0f},{p0[1]*S:.0f}) last=({p1[0]*S:.0f},{p1[1]*S:.0f}) font={l.get('font')}")
for s in d['symbols']:
    cx, cy = s['c'][0]*S, s['c'][1]*S
    if x0 <= cx <= x1 and y0 <= cy <= y1:
        print('SYM', s['t'], s['color'], f"({cx:.0f},{cy:.0f})")
