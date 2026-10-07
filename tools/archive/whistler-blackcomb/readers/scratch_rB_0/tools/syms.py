import json, sys
d = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/printed.json'))
x0, y0, x1, y1 = map(float, sys.argv[1].split(','))
for s in d['symbols']:
    cx, cy = s['c'][0]*2.5, s['c'][1]*2.5
    if x0 <= cx <= x1 and y0 <= cy <= y1:
        print(s['t'], s['color'], '(%d,%d)' % (cx, cy), s['seq'])
