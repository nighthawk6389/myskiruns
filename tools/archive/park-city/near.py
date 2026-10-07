"""near.py [--d 4] [--min 25]: pairs of Park City trails whose overlays run within d map px of each other for at least
min px of length (sampled every 2 px) -- two names on one drawn line, or two lines drawn closer than a line's width."""
import json, math, sys
import numpy as np
from scipy.spatial import cKDTree
D = float(sys.argv[sys.argv.index('--d') + 1]) if '--d' in sys.argv else 4
MIN = float(sys.argv[sys.argv.index('--min') + 1]) if '--min' in sys.argv else 25
W, H = 4365, 2275
T = json.load(open('/home/user/myskiruns/src/data/resorts/park-city/trailPaths.json'))['trails']
samp = {}
for tid, p in T.items():
    out = []
    for s in p.get('segments', []):
        q = [(x * W / 100, y * H / 100) for x, y in s]
        for a, b in zip(q, q[1:]):
            n = max(1, int(math.dist(a, b) / 2))
            out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    if out:
        samp[tid] = np.array(out)
trees = {t: cKDTree(v) for t, v in samp.items()}
res = []
ids = sorted(samp)
for i, a in enumerate(ids):
    for b in ids[i + 1:]:
        d, _ = trees[b].query(samp[a], distance_upper_bound=D)
        n = int(np.isfinite(d).sum())
        if n * 2 >= MIN:
            pts = samp[a][np.isfinite(d)]
            res.append((n * 2, a, b, pts.mean(0)))
for L, a, b, c in sorted(res, reverse=True):
    print(f'{L:5d} px  {a:24s} {b:24s} at ({c[0]:.0f},{c[1]:.0f})')
