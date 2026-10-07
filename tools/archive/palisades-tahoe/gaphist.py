"""gaphist.py PANEL: histogram of letter-to-letter gaps (pt, along each run's end-to-end direction) for a panel's black
glyph runs, with the letter pairs: word gaps sit apart from letter gaps."""
import json, math, collections, sys
p = sys.argv[1]
W = f'/home/user/myskiruns/work/palisades-tahoe/{p}'
G = json.load(open(f'{W}/glyphs.json'))['glyphs']
L = json.load(open('/home/user/myskiruns/tools/trailmap/resorts/palisades-tahoe/letters.json'))
def letter(g):
    best = None
    for t in L:
        if t['kinds'] != g['kinds'] or len(t['sig']) != len(g['sig']):
            continue
        if max(abs(a - b) for a, b in zip(t['sig'], g['sig'])) >= 0.03:
            continue
        r = abs(math.log(t['size'] / g['size']))
        if r < math.log(1.15) and (best is None or r < best[0]):
            best = (r, t['ch'])
    return best[1] if best else None
GG = [g for g in G if g['col'] == 'black']
for g in GG:
    g['ch'] = letter(g)
runs, cur = [], []
for g in (g for g in GG if g['ch'] and g['ch'] != '*'):
    if cur and (math.dist(g['c'], cur[-1]['c']) > 9 or g['seq'] - cur[-1]['seq'] > 6):
        runs.append(cur); cur = []
    cur.append(g)
runs.append(cur)
rows = []
for run in runs:
    if len(run) < 3:
        continue
    run = sorted(run, key=lambda g: g['seq'])
    p0, q0 = run[0]['c'], run[-1]['c']
    n = math.dist(p0, q0) or 1
    u = ((q0[0] - p0[0]) / n, (q0[1] - p0[1]) / n)
    run = sorted(run, key=lambda g: g['c'][0] * u[0] + g['c'][1] * u[1])
    for a, b in zip(run, run[1:]):
        gap = min(x * u[0] + y * u[1] for x, y in b['pts']) - max(x * u[0] + y * u[1] for x, y in a['pts'])
        rows.append((round(gap, 2), a['ch'] + b['ch']))
hist = collections.Counter(round(r[0] * 5) / 5 for r in rows)
for k in sorted(hist):
    if -1 <= k <= 4:
        print(f'{k:5.1f} {hist[k]:4d}', ' '.join(r[1] for r in rows if round(r[0] * 5) / 5 == k)[:120])
