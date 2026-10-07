"""OSM runs touching a given way's ends, and their ends (warped into map px). osmnear.py way_id|name ..."""
import json, math, sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import importlib.util
spec = importlib.util.spec_from_file_location('w', sys.argv[0].rsplit('/', 1)[0] + '/osmwarp.py')
sys.argv_saved = sys.argv; sys.argv = ['x']
W = importlib.util.module_from_spec(spec); spec.loader.exec_module(W)
sys.argv = sys.argv_saved
d = W.d
ways = []
for e in d['elements']:
    t = e.get('tags', {})
    if e['type'] == 'way' and t.get('piste:type') == 'downhill':
        pts = [W.m(g['lat'], g['lon']) for g in e['geometry']]
        ways.append((e['id'], t.get('name', ''), t.get('piste:difficulty', ''), pts))
for q in sys.argv[1:]:
    sel = [w for w in ways if str(w[0]) == q or w[1] == q]
    for wid, nm, dif, pts in sel:
        a, b = W.warp([pts[0], pts[-1]])
        L = sum(math.dist(p, r) for p, r in zip(pts, pts[1:]))
        print(f'{nm or "-"} {wid} {dif} {L:.0f} m: start ~({a[0]:.0f},{a[1]:.0f}) end ~({b[0]:.0f},{b[1]:.0f})')
        for k, e in (('start', pts[0]), ('end', pts[-1])):
            near = []
            for w2, n2, d2, p2 in ways:
                if w2 == wid:
                    continue
                dmin = min(math.dist(e, p) for p in p2)
                if dmin < 15:
                    pos = 'its start' if math.dist(e, p2[0]) < 15 else 'its end' if math.dist(e, p2[-1]) < 15 else 'its middle'
                    near.append(f'{n2 or "-"} {w2} ({pos})')
            print(f'   {k} meets: {near}')
