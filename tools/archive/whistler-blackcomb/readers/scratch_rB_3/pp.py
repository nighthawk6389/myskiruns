import json, sys
W, H = 4320, 2103
d = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))['polylines']
names = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/names.json'))
by = {p['id']: p for p in d}
step = 1
args = sys.argv[1:]
if args and args[0].startswith('-s'):
    step = int(args[0][2:]); args = args[1:]
for a in args:
    p = by[int(a)]
    pts = [(round(x*W/100), round(y*H/100)) for x, y in p['points']]
    print(a, p['cls'], p['lengthPx'], names.get(a), len(pts))
    print('   ', pts[::step] + ([pts[-1]] if (len(pts)-1) % step else []))
