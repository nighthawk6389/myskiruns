"""gischeck.py PANEL [--radius 320] [--out flags.json]: cross-check every named piece of a Whistler Blackcomb panel
against the resort's ArcGIS run lines. Per piece: fit an affine map (GIS metres -> map px) by ICP on the named
pieces around it (its neighbours, not itself), project the GIS run lines, and measure how much of the piece each
GIS run covers. Prints the pieces whose own name's run covers little of them while another run covers most."""
import argparse
import collections
import json
import math
import re
import sys

import numpy as np

sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr  # noqa: E402

S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad'
ap = argparse.ArgumentParser()
ap.add_argument('panel')
ap.add_argument('--radius', type=float, default=320)
ap.add_argument('--tol', type=float, default=14)
ap.add_argument('--out')
ap.add_argument('--only', default='')
ap.add_argument('--plot', help='out.png: for one --only piece, the projected GIS runs over its crop')
a = ap.parse_args()

ALIAS = {'NINE': '9', 'NUMBER': ''}


def base(name):
    t = name.upper().replace('’', "'")
    t = re.sub(r'\s+-\s*(UPPER|LOWER|MID|MAIN|RIGHT|LEFT|BYPASS|CAT TRACK|EAST|WEST|ROLLS|BUMPS|SNOOZER|GRUB|'
               r'FALLAWAY|WEASEL|FOON ALLEY|ADVENTURE TRAIL|LOWER ENTRANCE|UPPER ENTRANCE|BLUE|GREEN|CONNECTOR)\b.*$',
               '', t)
    t = re.sub(r'^(UPPER|LOWER)\s+', '', t)
    t = re.sub(r'^THE\s+', '', t)
    t = ' '.join(ALIAS.get(w, w) for w in t.split())
    return re.sub(r'[^A-Z0-9]', '', t)


r = pr.Resort(f'whistler-blackcomb/{a.panel}')
P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
N = json.load(open(r.work('names.json')))


def dense(pts, step):
    out = []
    for p, q in zip(pts, pts[1:]):
        n = max(1, int(math.dist(p, q) / step))
        out += [(p[0] + (q[0] - p[0]) * k / n, p[1] + (q[1] - p[1]) * k / n) for k in range(n)]
    return out + [tuple(pts[-1])]


def mountain_of(pid):
    if a.panel == 'symphony':
        return 'Whistler'
    if a.panel == 'glacier':
        return 'Blackcomb'
    m = pr.midpoint(P[pid])
    return 'Blackcomb' if m[0] < 2050 else 'Whistler'


feats = json.load(open(f'{S}/wb_truth/data/arcgis/features/Ski_Runs_GDB_L1_p0.geojson'))['features']
lat0 = 50.09


def xy(p):
    return ((p[0] + 122.92) * math.cos(math.radians(lat0)) * 111320, (p[1] - lat0) * 110540)


GIS = collections.defaultdict(list)  # (mountain, base) -> [np.array of points in metres]
GNAME = {}
for ft in feats:
    pp = ft['properties']; g = ft['geometry']
    if not g:
        continue
    parts = [g['coordinates']] if g['type'] == 'LineString' else g['coordinates']
    for part in parts:
        if len(part) < 2:
            continue
        pts = np.array(dense([xy(q) for q in part], 8))
        k = (pp.get('mountain'), base(pp['run_name']))
        GIS[k].append(pts)
        GNAME.setdefault(k, set()).add(pp['run_name'])
GALL = {k: np.vstack(v) for k, v in GIS.items()}

named = {}
for k, v in N.items():
    i = int(k)
    if v in ('?', '-') or '/' in v:
        continue
    named[i] = v.rstrip('~')
samples = {i: np.array(dense(P[i], 4)) for i in named}


def solve(A, B):
    X = np.hstack([A, np.ones((len(A), 1))])
    M, *_ = np.linalg.lstsq(X, B, rcond=None)
    return M


def apply(M, A):
    return np.hstack([A, np.ones((len(A), 1))]) @ M


# global init: centroids of each run (map pieces vs GIS lines), per mountain, trimmed least squares
inits = {}
for mtn in ('Whistler', 'Blackcomb'):
    pairs = []
    by = collections.defaultdict(list)
    for i, nm in named.items():
        if mountain_of(i) == mtn and (mtn, base(nm)) in GALL:
            by[base(nm)].append(samples[i])
    for b, arrs in by.items():
        pairs.append((GALL[(mtn, b)].mean(0), np.vstack(arrs).mean(0)))
    if len(pairs) < 4:
        continue
    A = np.array([p[0] for p in pairs]); B = np.array([p[1] for p in pairs])
    keep = np.ones(len(A), bool)
    for _ in range(6):
        M = solve(A[keep], B[keep])
        e = np.linalg.norm(apply(M, A) - B, axis=1)
        keep = e <= max(np.percentile(e, 70), 60)
    inits[mtn] = M
    print(f'{mtn}: global init from {len(pairs)} runs, {keep.sum()} kept, median error {np.median(e):.0f} px',
          file=sys.stderr)


def nearest_d(Q, T):
    """for each point of Q, the distance to the nearest point of T (both N x 2)."""
    out = np.empty(len(Q))
    for k in range(0, len(Q), 256):
        d = ((Q[k:k + 256, None, :] - T[None, :, :]) ** 2).sum(-1)
        out[k:k + 256] = np.sqrt(d.min(1))
    return out


def nearest_idx(Q, T):
    out = np.empty(len(Q), int)
    for k in range(0, len(Q), 256):
        d = ((Q[k:k + 256, None, :] - T[None, :, :]) ** 2).sum(-1)
        out[k:k + 256] = d.argmin(1)
    return out


rows = []
targets = [int(t) for t in a.only.split(',')] if a.only else sorted(named)
for t in targets:
    if t not in named:
        continue
    mtn = mountain_of(t)
    if mtn not in inits:
        continue
    St = samples[t]
    c = St.mean(0)
    anchors = [i for i in named if i != t and mountain_of(i) == mtn and (mtn, base(named[i])) in GALL
               and np.min(np.linalg.norm(samples[i] - c, axis=1)) < a.radius]
    if len(anchors) < 4:
        rows.append({'id': t, 'name': named[t], 'note': 'too few anchors'})
        continue
    M = inits[mtn]
    # GIS points of the anchors' runs (near the neighbourhood after the global init)
    for it in range(25):
        A, B = [], []
        for i in anchors:
            G = GALL[(mtn, base(named[i]))]
            Gp = apply(M, G)
            near = np.linalg.norm(Gp - c, axis=1) < a.radius * 2.5
            if near.sum() < 2:
                continue
            Gn, Gpn = G[near], Gp[near]
            idx = nearest_idx(samples[i], Gpn)
            d = np.linalg.norm(Gpn[idx] - samples[i], axis=1)
            A.append(Gn[idx]); B.append(samples[i]);
        if not A:
            break
        A = np.vstack(A); B = np.vstack(B)
        e = np.linalg.norm(apply(M, A) - B, axis=1)
        keep = e <= np.percentile(e, 75)
        M = solve(A[keep], B[keep])
    e = np.linalg.norm(apply(M, A) - B, axis=1)
    res = float(np.median(e))
    tol = max(a.tol, 1.2 * res)
    cov = {}
    for (m2, b), G in GALL.items():
        if m2 != mtn:
            continue
        Gp = apply(M, G)
        if np.min(np.linalg.norm(Gp - c, axis=1)) > 300:
            continue
        d = nearest_d(St, Gp)
        f = float((d < tol).mean())
        if f > 0.05:
            cov[b] = round(f, 2)
    own = cov.get(base(named[t]), 0.0)
    best = max(cov.items(), key=lambda kv: kv[1]) if cov else (None, 0)
    if a.plot:
        from PIL import Image, ImageDraw, ImageFont
        im = Image.open(r.work('map.png')).convert('RGB')
        x0, y0 = int(c[0] - 260), int(c[1] - 200)
        im = im.crop((x0, y0, x0 + 520, y0 + 400)).resize((1040, 800))
        dr = ImageDraw.Draw(im)
        F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
        tr = lambda q: ((q[0] - x0) * 2, (q[1] - y0) * 2)  # noqa: E731
        dr.line([tr(q) for q in St], fill=(255, 0, 255), width=7)
        cols = [(230, 0, 0), (0, 150, 0), (0, 0, 230), (200, 120, 0), (0, 160, 160), (130, 0, 200)]
        k = 0
        for (m2, b), arrs in GIS.items():
            if m2 != mtn:
                continue
            for G in arrs:
                Gp = apply(M, G)
                if np.min(np.linalg.norm(Gp - c, axis=1)) > 260:
                    continue
                col = cols[k % len(cols)]; k += 1
                dr.line([tr(q) for q in Gp], fill=col, width=2)
                q = Gp[len(Gp) // 2]
                dr.text(tr(q), b, fill=col, font=F, stroke_width=2, stroke_fill='white')
        im.save(a.plot)
    rows.append({'id': t, 'name': named[t], 'own': own, 'best': best[0], 'bestCov': best[1], 'res': round(res, 1),
                 'tol': round(tol, 1), 'anchors': len(anchors), 'cov': dict(sorted(cov.items(), key=lambda kv: -kv[1])[:4]),
                 'hasGis': (mtn, base(named[t])) in GALL, 'len': len(St) * 4})
flags = [x for x in rows if 'own' in x and x['hasGis'] and x['own'] < 0.35 and x['bestCov'] >= 0.5 and x['best'] != base(x['name'])]
nogis = sorted({x['name'] for x in rows if 'own' in x and not x['hasGis']})
print(f'{len(rows)} pieces checked; {len(flags)} flagged; names with no GIS run: {nogis}')
for x in sorted(flags, key=lambda x: (x['own'] - x['bestCov'])):
    print(f"  {x['id']:4d} {x['name']:28.28s} own {x['own']:.2f}  best {x['best']} {x['bestCov']:.2f}  res {x['res']} "
          f"tol {x['tol']} len {x['len']}  {x['cov']}")
weak = [x for x in rows if 'own' in x and x['hasGis'] and x['own'] < 0.35 and x not in flags]
print(f'{len(weak)} more with little cover by their own run and no clear other:')
for x in sorted(weak, key=lambda x: x['own']):
    print(f"  {x['id']:4d} {x['name']:28.28s} own {x['own']:.2f}  res {x['res']} tol {x['tol']} len {x['len']}  {x['cov']}")
if a.out:
    json.dump(rows, open(a.out, 'w'), indent=1)
