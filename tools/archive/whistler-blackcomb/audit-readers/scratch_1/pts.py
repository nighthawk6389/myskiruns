import json, sys
panel = sys.argv[1]
sizes = {'main': (4320, 2103), 'symphony': (1704, 1022), 'glacier': (1114, 1008)}
W, H = sizes[panel]
d = json.load(open(f'/home/user/myskiruns/src/data/resorts/whistler-blackcomb/panels/{panel}/trailPaths.json'))['trails']
for t in sys.argv[2:]:
    p = d.get(t)
    if not p:
        print(t, 'none'); continue
    for s in p.get('segments', []):
        print(t, [(round(x * W / 100), round(y * H / 100)) for x, y in s])
    if p.get('label'):
        print(t, 'label', [round(p['label'][0] * W / 100), round(p['label'][1] * H / 100)])
    print(t, 'source', p.get('source'))
