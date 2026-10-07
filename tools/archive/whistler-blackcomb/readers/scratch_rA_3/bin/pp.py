import json, sys
W, H = 4320, 2103
P = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))['polylines']
N = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/names.json'))
byid = {p['id']: p for p in P}
for a in sys.argv[1:]:
    p = byid[int(a)]
    pts = [(round(x * W / 100), round(y * H / 100)) for x, y in p['points']]
    print(p['id'], p['cls'], p['lengthPx'], N.get(str(p['id'])), len(pts))
    print('   ', ' '.join(f'{x},{y}' for x, y in pts))
