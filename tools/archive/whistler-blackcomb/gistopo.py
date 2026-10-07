"""gistopo.py PANEL: where two trails' pieces meet on the map (a piece end on another trail's piece), check that the
resort's ArcGIS run lines for the two also come close. Prints the meetings whose GIS runs are far apart: one of
the two pieces may carry the wrong name."""
import collections
import json
import math
import re
import sys

import numpy as np

sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr  # noqa: E402

S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad'
sys.path.insert(0, f'{S}/wbt')
panel = sys.argv[1]
FAR = float(sys.argv[2]) if len(sys.argv) > 2 else 150


def base(name):
    t = name.upper().replace('’', "'")
    t = re.sub(r'\s+-\s*(UPPER|LOWER|MID|MAIN|RIGHT|LEFT|BYPASS|CAT TRACK|EAST|WEST|ROLLS|BUMPS|SNOOZER|GRUB|'
               r'FALLAWAY|WEASEL|FOON ALLEY|ADVENTURE TRAIL|LOWER ENTRANCE|UPPER ENTRANCE|BLUE|GREEN|CONNECTOR)\b.*$',
               '', t)
    t = re.sub(r'^(UPPER|LOWER)\s+', '', t)
    t = re.sub(r'^THE\s+', '', t)
    t = t.replace(' NINE', ' 9')
    return re.sub(r'[^A-Z0-9]', '', t)


r = pr.Resort(f'whistler-blackcomb/{panel}')
P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
N = json.load(open(r.work('names.json')))


def mountain_of(pid):
    if panel == 'symphony':
        return 'Whistler'
    if panel == 'glacier':
        return 'Blackcomb'
    return 'Blackcomb' if pr.midpoint(P[pid])[0] < 2050 else 'Whistler'


lat0 = 50.09


def xy(p):
    return ((p[0] + 122.92) * math.cos(math.radians(lat0)) * 111320, (p[1] - lat0) * 110540)


def dense(pts, step):
    out = []
    for p, q in zip(pts, pts[1:]):
        n = max(1, int(math.dist(p, q) / step))
        out += [(p[0] + (q[0] - p[0]) * k / n, p[1] + (q[1] - p[1]) * k / n) for k in range(n)]
    return out + [tuple(pts[-1])]


G = collections.defaultdict(list)
for ft in json.load(open(f'{S}/wb_truth/data/arcgis/features/Ski_Runs_GDB_L1_p0.geojson'))['features']:
    pp = ft['properties']; g = ft['geometry']
    if not g:
        continue
    for part in ([g['coordinates']] if g['type'] == 'LineString' else g['coordinates']):
        if len(part) >= 2:
            G[(pp.get('mountain'), base(pp['run_name']))] += dense([xy(q) for q in part], 8)
G = {k: np.array(v) for k, v in G.items()}

trail = {}
for k, v in N.items():
    if v not in ('?', '-') and '/' not in v:
        trail[int(k)] = v.rstrip('~')
meet = collections.defaultdict(list)
for i, nm in trail.items():
    for e in (P[i][0], P[i][-1]):
        for j, nm2 in trail.items():
            if nm2 == nm:
                continue
            if pr.line_dist(e, P[j]) < 6:
                meet[tuple(sorted((nm, nm2)))].append((i, j, (round(e[0]), round(e[1]))))
out = []
for (a, b), where in meet.items():
    i = where[0][0]
    m = mountain_of(i)
    ka, kb = (m, base(a)), (m, base(b))
    if ka not in G or kb not in G or ka == kb:
        continue
    A, B = G[ka], G[kb]
    d = min(float(np.sqrt(((A[k:k + 400, None, :] - B[None, :, :]) ** 2).sum(-1)).min()) for k in range(0, len(A), 400))
    if d > FAR:
        out.append((d, a, b, where))
print(f'{len(meet)} meetings of two trails on the map; {len(out)} whose GIS runs are over {FAR:.0f} m apart:')
for d, a, b, where in sorted(out, reverse=True):
    print(f'  {d:6.0f} m  {a} / {b}  at', [(i, j, e) for i, j, e in where[:3]])
