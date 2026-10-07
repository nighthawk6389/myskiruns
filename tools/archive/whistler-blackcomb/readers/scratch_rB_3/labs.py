import json, sys
S = 2.5
d = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/printed.json'))
x0, y0, x1, y1 = [float(v) for v in sys.argv[1:5]]
for l in d['labels']:
    cx, cy = l['c'][0]*S, l['c'][1]*S
    if x0 <= cx <= x1 and y0 <= cy <= y1:
        p0 = l['pts'][0]; p1 = l['pts'][-1]
        print(repr(l['text']), l['color'], round(l['size'],1), 'c', (round(cx), round(cy)), 'first', (round(p0[0]*S), round(p0[1]*S)), 'last', (round(p1[0]*S), round(p1[1]*S)), l.get('font'))
for s in d['symbols']:
    cx, cy = s['c'][0]*S, s['c'][1]*S
    if x0 <= cx <= x1 and y0 <= cy <= y1:
        print('SYM', s['t'], s['color'], (round(cx), round(cy)))
