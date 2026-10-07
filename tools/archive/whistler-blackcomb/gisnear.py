"""gisnear.py MOUNTAIN NAME [NAME...]: for each GIS run (by base name), its parts' lengths and the runs its two ends
touch (nearest runs within 60 m), to read a run's topology."""
import collections
import json
import math
import re
import sys

import numpy as np

S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad'
mtn = sys.argv[1]
lat0 = 50.09


def xy(p):
    return ((p[0] + 122.92) * math.cos(math.radians(lat0)) * 111320, (p[1] - lat0) * 110540)


def dense(pts, step):
    out = []
    for p, q in zip(pts, pts[1:]):
        n = max(1, int(math.dist(p, q) / step))
        out += [(p[0] + (q[0] - p[0]) * k / n, p[1] + (q[1] - p[1]) * k / n) for k in range(n)]
    return out + [tuple(pts[-1])]


runs = []
for ft in json.load(open(f'{S}/wb_truth/data/arcgis/features/Ski_Runs_GDB_L1_p0.geojson'))['features']:
    pp = ft['properties']; g = ft['geometry']
    if not g or pp.get('mountain') != mtn:
        continue
    for part in ([g['coordinates']] if g['type'] == 'LineString' else g['coordinates']):
        if len(part) >= 2:
            runs.append((pp['run_name'], pp.get('difficulty'), pp.get('trailmap'), np.array(dense([xy(q) for q in part], 6))))
want = [w.upper() for w in sys.argv[2:]]
for nm, dif, tm, A in runs:
    if not any(w in nm.upper() for w in want):
        continue
    L = float(np.sum(np.linalg.norm(np.diff(A, axis=0), axis=1)))
    ends = []
    for e in (A[0], A[-1]):
        near = []
        for nm2, _d, _t, B in runs:
            if nm2 == nm:
                continue
            d = float(np.min(np.linalg.norm(B - e, axis=1)))
            if d < 60:
                near.append((round(d), nm2))
        ends.append(sorted(near)[:5])
    # runs crossing or touching its middle
    mid = []
    for nm2, _d, _t, B in runs:
        if nm2 == nm:
            continue
        d = np.sqrt(((A[::3, None, :] - B[None, ::3, :]) ** 2).sum(-1)).min(1)
        if (d[2:-2] < 15).any() if len(d) > 4 else False:
            mid.append(nm2)
    print(f'{nm} ({dif}, map {tm}) {L:.0f} m: start {ends[0]} | end {ends[1]} | touches along: {sorted(set(mid))}')
