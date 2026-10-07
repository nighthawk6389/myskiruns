"""vl_symgap.py: every named symbol whose trail's final overlay (trailPaths.json) does not reach it: a stub between
the parent line and the symbol, or the stretch along the printed name, that no piece covers."""
import json, math, re, sys
exec(open('vl_symnames.py').read())
exec(open('vl_pt.py').read())
R = '/home/user/myskiruns/src/data/resorts/vail'
slug = lambda n: re.sub(r'[^a-z0-9]+', '-', n.lower().replace("'", '')).strip('-')  # noqa: E731
out = []
for panel in ('front-side', 'back-bowls', 'blue-sky'):
    W, H = SIZE[panel]
    paths = json.load(open(f'{R}/panels/{panel}/trailPaths.json'))['trails']
    for s in json.load(open(f'syms_{panel}.json')):
        n = NAMES[panel].get(s['i'])
        if not n or n == '?':
            continue
        p = paths.get(slug(n))
        if not p:
            out.append((panel, s['i'], n, 'no overlay on this panel', s['c'])); continue
        if p.get('label'):
            continue
        segs = [[(x * W / 100, y * H / 100) for x, y in seg] for seg in p['segments']]
        d = min(seg_dist(s['c'], g[i], g[i + 1]) for g in segs for i in range(len(g) - 1))
        if d > 1.5 * s['r'] + 4:
            out.append((panel, s['i'], n, round(d), [round(v) for v in s['c']]))
for o in out:
    print(*o)
print(len(out), 'symbols off their overlay')
