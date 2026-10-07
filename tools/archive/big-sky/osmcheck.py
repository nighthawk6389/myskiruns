"""osmcheck.py RESORT/PANEL [--radius 320] [--only id,id] [--undecided] [--plot out.png]: cross-check pieces against
OpenStreetMap's ski runs (piste:type=downhill ways, fetched with Overpass). Per piece: fit an affine map (OSM metres
-> map px) by ICP on the named pieces around it (not itself), project the OSM runs, and measure how much of the
piece each covers. Prints named pieces whose own run covers little while another covers most, and with
--undecided each undecided piece's best-covering runs."""
import argparse, collections, json, math, re, sys
import numpy as np
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr  # noqa: E402

S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad'
ap = argparse.ArgumentParser()
ap.add_argument('panel')
ap.add_argument('--radius', type=float, default=320)
ap.add_argument('--tol', type=float, default=14)
ap.add_argument('--only', default='')
ap.add_argument('--undecided', action='store_true')
ap.add_argument('--plot')
ap.add_argument('--show', default='')
ap.add_argument('--along', action='store_true')  # per stretch of the piece: the nearest OSM runs (names as tagged)  # plot only these OSM runs (names, comma-separated)
a = ap.parse_args()


def base(name):
    t = name.upper().replace('’', "'").replace('É', 'E')
    t = re.sub(r'\s*\((FULL|LOWER|UPPER)\)', '', t)
    t = re.sub(r'^(UPPER|LOWER|MIDDLE|THE)\s+', '', t)
    t = re.sub(r'\s+RUN$', '', t)
    return re.sub(r'[^A-Z0-9]', '', t)


r = pr.Resort(a.panel)
P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
N = json.load(open(r.work('names.json')))
lat0, lon0 = 45.27, -111.43


def xy(p):
    return ((p[0] - lon0) * math.cos(math.radians(lat0)) * 111320, (lat0 - p[1]) * 110540)  # y down, like the map


def dense(pts, step):
    out = []
    for p, q in zip(pts, pts[1:]):
        n = max(1, int(math.dist(p, q) / step))
        out += [(p[0] + (q[0] - p[0]) * k / n, p[1] + (q[1] - p[1]) * k / n) for k in range(n)]
    return out + [tuple(pts[-1])]


OSM = collections.defaultdict(list)
RAW = []  # (name as tagged, dense points)
for e in json.load(open(f'{S}/bs/osm/bs.json'))['elements']:
    if e['type'] != 'way' or not e.get('tags', {}).get('name') or 'geometry' not in e:
        continue
    pts = [xy((g['lon'], g['lat'])) for g in e['geometry']]
    if len(pts) >= 2:
        OSM[base(e['tags']['name'])].append(np.array(dense(pts, 8)))
        RAW.append((e['tags']['name'], np.array(dense(pts, 8))))
OALL = {k: np.vstack(v) for k, v in OSM.items()}
named = {int(k): v.rstrip('~') for k, v in N.items() if v not in ('?', '-')}
samples = {i: np.array(dense(P[i], 4)) for i in P}


def solve(A, B):
    M, *_ = np.linalg.lstsq(np.hstack([A, np.ones((len(A), 1))]), B, rcond=None)
    return M


def apply(M, A):
    return np.hstack([A, np.ones((len(A), 1))]) @ M


from scipy.spatial import cKDTree


def nearest(Q, T):
    di, ix = cKDTree(T).query(Q)
    return di, ix


# global init: centroids of runs (OSM vs map), trimmed least squares
by = collections.defaultdict(list)
for i, nm in named.items():
    if base(nm) in OALL:
        by[base(nm)].append(samples[i])
pairs = [(OALL[b].mean(0), np.vstack(v).mean(0)) for b, v in by.items()]
A = np.array([p[0] for p in pairs]); B = np.array([p[1] for p in pairs])
keep = np.ones(len(A), bool)
for _ in range(8):
    M0 = solve(A[keep], B[keep]); e = np.linalg.norm(apply(M0, A) - B, axis=1)
    keep = e <= max(np.percentile(e, 60), 80)
print(f'global init from {len(pairs)} runs, {keep.sum()} kept, median error {np.median(e):.0f} px', file=sys.stderr)

targets = [int(t) for t in a.only.split(',')] if a.only else sorted(P)
out = []
for t in targets:
    und = N.get(str(t)) == '?'
    if a.undecided != und and not a.only:
        continue
    St = samples[t]; c = St.mean(0)
    anchors = [i for i in named if i != t and base(named[i]) in OALL and np.min(np.linalg.norm(samples[i] - c, axis=1)) < a.radius]
    if len(anchors) < 4:
        out.append((t, N.get(str(t)), 'too few anchors', {}))
        continue
    M = M0
    AA = BB = None
    for it in range(25):
        AA, BB = [], []
        for i in anchors:
            G = OALL[base(named[i])]; Gp = apply(M, G)
            near = np.linalg.norm(Gp - c, axis=1) < a.radius * 2.5
            if near.sum() < 2:
                continue
            d, ix = nearest(samples[i], Gp[near])
            AA.append(G[near][ix]); BB.append(samples[i])
        if not AA:
            AA = None
            break
        AA = np.vstack(AA); BB = np.vstack(BB)
        e = np.linalg.norm(apply(M, AA) - BB, axis=1)
        k = e <= np.percentile(e, 75)
        M = solve(AA[k], BB[k])
    if AA is None:
        out.append((t, N.get(str(t)), 'no anchor run near', {}))
        continue
    res = float(np.median(np.linalg.norm(apply(M, AA) - BB, axis=1)))
    tol = max(a.tol, 1.2 * res)
    cov = {}
    for b, G in OALL.items():
        Gp = apply(M, G)
        if np.min(np.linalg.norm(Gp - c, axis=1)) > 300:
            continue
        f = float((nearest(St, Gp)[0] < tol).mean())
        if f > 0.05:
            cov[b] = round(f, 2)
    out.append((t, N.get(str(t)), f'res {res:.0f} tol {tol:.0f}', dict(sorted(cov.items(), key=lambda kv: -kv[1])[:4])))
    if a.along:
        R2 = [(nm, apply(M, G)) for nm, G in RAW]
        R2 = [(nm, Gp) for nm, Gp in R2 if np.min(np.linalg.norm(Gp - c, axis=1)) < 400]
        line = []
        for k in range(0, len(St), 10):
            q = St[k]
            ds = sorted((float(np.min(np.linalg.norm(Gp - q, axis=1))), nm) for nm, Gp in R2)
            seen, best = set(), []
            for dd, nm in ds:
                if nm not in seen:
                    seen.add(nm); best.append(f'{nm} {dd:.0f}')
                if len(best) == 2:
                    break
            line.append(f'({q[0]:.0f},{q[1]:.0f}) ' + ' | '.join(best))
        print(f'#{t} res {res:.0f}:', *line, sep='\n   ')
    if a.plot:
        from PIL import Image, ImageDraw, ImageFont
        Image.MAX_IMAGE_PIXELS = None
        im = Image.open(r.work('map.png')).convert('RGB')
        x0, y0 = int(c[0] - 220), int(c[1] - 220)
        crop = im.crop((x0, y0, x0 + 440, y0 + 440)).resize((880, 880))
        d = ImageDraw.Draw(crop)
        F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
        cols = [(255, 0, 255), (255, 120, 0), (0, 160, 0), (200, 0, 0), (0, 0, 255), (120, 0, 200)]
        k = 0
        show = {base(v) for v in a.show.split(',') if v}
        for b, parts in OSM.items():
            if show and b not in show:
                continue
            for part in parts:
                Gp = apply(M, part)
                if np.min(np.linalg.norm(Gp - c, axis=1)) > 260:
                    continue
                col = cols[k % len(cols)]
                d.line([((x - x0) * 2, (y - y0) * 2) for x, y in Gp], fill=col, width=3)
                m = Gp[len(Gp) // 2]; d.text(((m[0] - x0) * 2 + 4, (m[1] - y0) * 2), b, fill=col, font=F)
            k += 1
        d.line([((x - x0) * 2, (y - y0) * 2) for x, y in St], fill=(0, 0, 0), width=1)
        crop.save(a.plot.replace('.png', f'_{t}.png'))
for t, nm, note, cov in out:
    if nm != '?' and nm is not None:
        own = cov.get(base(nm.rstrip('~')), 0)
        best = max(cov.values(), default=0)
        if not a.only and (own >= 0.5 or best < 0.6):
            continue
    print(f'{t:4d} {str(nm):26s} {note:18s} {cov}')
