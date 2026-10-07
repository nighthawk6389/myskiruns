import json, sys
d = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))['polylines']
n = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/names.json'))
W, H = 4320, 2103
ids = sys.argv[1:]
for q in d:
    if str(q['id']) in ids:
        pts = [(round(a * W / 100), round(b * H / 100)) for a, b in q['points']]
        print(q['id'], q['cls'], q['lengthPx'], n.get(str(q['id'])), pts)
