import json, sys
d = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/printed.json'))
x0, y0, x1, y1 = map(float, sys.argv[1].split(','))
print(d.keys())
for L in d['labels']:
    cx, cy = L['c'][0]*2.5, L['c'][1]*2.5
    if x0 <= cx <= x1 and y0 <= cy <= y1:
        p0 = L['pts'][0]; p1 = L['pts'][-1]
        print(L['text'], L['color'], 'c=(%d,%d)' % (cx, cy), 'first=(%d,%d)' % (p0[0]*2.5, p0[1]*2.5), 'last=(%d,%d)' % (p1[0]*2.5, p1[1]*2.5), L.get('font'))
