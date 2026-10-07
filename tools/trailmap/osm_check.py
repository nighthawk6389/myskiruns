"""Cross-check a PDF resort's line pieces against OpenStreetMap's ski runs: where a line between two names could be
either run's, which run does it follow? (Park City, Palisades Tahoe, Big Sky: docs/trail-map-playbook.md.)

    python3 tools/trailmap/osm_check.py fetch big-sky --bbox 45.22,-111.50,45.32,-111.35
    python3 tools/trailmap/osm_check.py check big-sky/main                  # named pieces another run covers
    python3 tools/trailmap/osm_check.py check big-sky/main --undecided      # each undecided piece's best runs
    python3 tools/trailmap/osm_check.py check park-city --only 412,413 --plot work/park-city/osm.png --along

fetch: piste:type=downhill ways and aerialways in the box (south,west,north,east) from an Overpass mirror (the main
one resets connections from here; kumi.systems answers), saved to work/<id>/osm.json.

check: per piece, an affine map from OSM (metres) to map px is fitted by ICP on the named pieces around it (not the
piece itself: `--radius` map px), the OSM runs are projected, and the share of the piece each run covers (within
`--tol` px, or 1.2x the fit's residual) is measured. Prints the named pieces whose own run covers little while
another covers most (or, with --only, every piece asked for; with --undecided, each undecided piece's runs).
`--plot` draws the projected runs over the piece's crop, `--along` lists the nearest runs every few px along it.
OpenStreetMap is not the truth where runs lie side by side (the fit can't tell them apart): settle each case on a
crop of the map itself. Run the resort's regen.sh first (it leaves pieces_cut.json and names.json in work/).
"""
import argparse
import collections
import json
import math
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdf_resort as pr  # noqa: E402

MIRRORS = ['https://overpass.kumi.systems/api/interpreter', 'https://overpass-api.de/api/interpreter',
           'https://maps.mail.ru/osm/tools/overpass/api/interpreter']


def base(name):
    """A run's name without Upper/Lower/The/Run, case and punctuation: how map names and OSM names are matched."""
    t = name.upper().replace('’', "'").replace('É', 'E')
    t = re.sub(r'\s*\((FULL|LOWER|UPPER)\)', '', t)
    t = re.sub(r'^(UPPER|LOWER|MIDDLE|THE)\s+', '', t)
    t = re.sub(r'\s+RUN$', '', t)
    return re.sub(r'[^A-Z0-9]', '', t)


def fetch(a):
    s, w, n, e = (float(v) for v in a.bbox.split(','))
    q = (f'[out:json][timeout:90];(way["piste:type"="downhill"]({s},{w},{n},{e});way["aerialway"]({s},{w},{n},{e}););'
         'out geom tags;')
    out = a.out or os.path.join(pr.work_root(a.resort.partition('/')[0]), 'osm.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    for url in MIRRORS:
        r = subprocess.run(['curl', '-sS', '-m', '120', '-A', 'myskiruns-trailmap/1.0', '--data-urlencode', f'data={q}',
                            url, '-o', out], capture_output=True, text=True)
        try:
            d = json.load(open(out))
        except Exception:
            print(f'{url}: no JSON ({r.stderr.strip()[:120]})', file=sys.stderr)
            continue
        ways = [x for x in d.get('elements', []) if x['type'] == 'way']
        print(f'{len(ways)} ways ({sum(1 for x in ways if "piste:type" in x.get("tags", {}))} runs) from {url} -> {out}')
        return
    raise SystemExit('no Overpass mirror answered')


def dense(pts, step):
    out = []
    for p, q in zip(pts, pts[1:]):
        k = max(1, int(math.dist(p, q) / step))
        out += [(p[0] + (q[0] - p[0]) * j / k, p[1] + (q[1] - p[1]) * j / k) for j in range(k)]
    return out + [tuple(pts[-1])]


def solve(A, B):
    M, *_ = np.linalg.lstsq(np.hstack([A, np.ones((len(A), 1))]), B, rcond=None)
    return M


def apply(M, A):
    return np.hstack([A, np.ones((len(A), 1))]) @ M


def check(a):
    from scipy.spatial import cKDTree
    r = pr.Resort(a.resort)
    osm = json.load(open(a.osm or os.path.join(pr.work_root(r.id), 'osm.json')))
    P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
    N = json.load(open(r.work('names.json')))
    runs = [e for e in osm['elements'] if e['type'] == 'way' and e.get('tags', {}).get('name') and 'geometry' in e
            and 'piste:type' in e['tags']]
    lat0 = float(np.mean([g['lat'] for e in runs for g in e['geometry']]))
    lon0 = float(np.mean([g['lon'] for e in runs for g in e['geometry']]))

    def xy(g):  # metres east and south of the runs' middle (y down, like the map)
        return ((g['lon'] - lon0) * math.cos(math.radians(lat0)) * 111320, (lat0 - g['lat']) * 110540)

    OSM, RAW = collections.defaultdict(list), []
    for e in runs:
        pts = [xy(g) for g in e['geometry']]
        if len(pts) >= 2:
            OSM[base(e['tags']['name'])].append(np.array(dense(pts, 8)))
            RAW.append((e['tags']['name'], np.array(dense(pts, 8))))
    OALL = {k: np.vstack(v) for k, v in OSM.items()}
    named = {int(k): v.rstrip('~') for k, v in N.items() if v not in ('?', '-')}
    samples = {i: np.array(dense(P[i], 4)) for i in P}

    def nearest(Q, T):
        return cKDTree(T).query(Q)

    # a first global fit: the runs' centroids, OSM against the map, trimmed least squares
    by = collections.defaultdict(list)
    for i, nm in named.items():
        if base(nm) in OALL:
            by[base(nm)].append(samples[i])
    pairs = [(OALL[b].mean(0), np.vstack(v).mean(0)) for b, v in by.items()]
    if len(pairs) < 4:
        raise SystemExit(f'only {len(pairs)} map names match an OSM run: nothing to fit on')
    A, B = np.array([p[0] for p in pairs]), np.array([p[1] for p in pairs])
    keep = np.ones(len(A), bool)
    for _ in range(8):
        M0 = solve(A[keep], B[keep])
        e = np.linalg.norm(apply(M0, A) - B, axis=1)
        keep = e <= max(np.percentile(e, 60), 80)
    print(f'global fit on {len(pairs)} runs, {keep.sum()} kept, median error {np.median(e):.0f} px', file=sys.stderr)

    targets = [int(t) for t in a.only.split(',')] if a.only else sorted(P)
    out = []
    for t in targets:
        und = N.get(str(t)) == '?'
        if a.undecided != und and not a.only:
            continue
        St = samples[t]
        c = St.mean(0)
        anchors = [i for i in named if i != t and base(named[i]) in OALL
                   and np.min(np.linalg.norm(samples[i] - c, axis=1)) < a.radius]
        if len(anchors) < 4:
            out.append((t, N.get(str(t)), 'too few anchors', {}))
            continue
        M, AA, BB = M0, None, None
        for _ in range(25):  # ICP: each anchor piece against its own run, nearest points
            AA, BB = [], []
            for i in anchors:
                G = OALL[base(named[i])]
                Gp = apply(M, G)
                near = np.linalg.norm(Gp - c, axis=1) < a.radius * 2.5
                if near.sum() < 2:
                    continue
                _d, ix = nearest(samples[i], Gp[near])
                AA.append(G[near][ix])
                BB.append(samples[i])
            if not AA:
                AA = None
                break
            AA, BB = np.vstack(AA), np.vstack(BB)
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
            near_runs = [(nm, apply(M, G)) for nm, G in RAW]
            near_runs = [(nm, Gp) for nm, Gp in near_runs if np.min(np.linalg.norm(Gp - c, axis=1)) < 400]
            line = []
            for k in range(0, len(St), 10):
                q = St[k]
                ds = sorted((float(np.min(np.linalg.norm(Gp - q, axis=1))), nm) for nm, Gp in near_runs)
                seen, best = set(), []
                for dd, nm in ds:
                    if nm not in seen:
                        seen.add(nm)
                        best.append(f'{nm} {dd:.0f}')
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
            show = {base(v) for v in a.show.split(',') if v}
            k = 0
            for b, parts in OSM.items():
                if show and b not in show:
                    continue
                for part in parts:
                    Gp = apply(M, part)
                    if np.min(np.linalg.norm(Gp - c, axis=1)) > 260:
                        continue
                    col = cols[k % len(cols)]
                    d.line([((x - x0) * 2, (y - y0) * 2) for x, y in Gp], fill=col, width=3)
                    m = Gp[len(Gp) // 2]
                    d.text(((m[0] - x0) * 2 + 4, (m[1] - y0) * 2), b, fill=col, font=F)
                k += 1
            d.line([((x - x0) * 2, (y - y0) * 2) for x, y in St], fill=(0, 0, 0), width=1)
            crop.save(a.plot.replace('.png', f'_{t}.png'))
    for t, nm, note, cov in out:
        if nm != '?' and nm is not None:
            own, best = cov.get(base(nm.rstrip('~')), 0), max(cov.values(), default=0)
            if not a.only and (own >= 0.5 or best < 0.6):
                continue
        print(f'{t:4d} {str(nm):26s} {note:18s} {cov}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    f = sub.add_parser('fetch')
    f.add_argument('resort')
    f.add_argument('--bbox', required=True, help='south,west,north,east (degrees)')
    f.add_argument('--out')
    c = sub.add_parser('check')
    c.add_argument('resort', help='<id> or <id>/<panel>')
    c.add_argument('--osm', help='Overpass JSON (default work/<id>/osm.json)')
    c.add_argument('--radius', type=float, default=320)
    c.add_argument('--tol', type=float, default=14)
    c.add_argument('--only', default='')
    c.add_argument('--undecided', action='store_true')
    c.add_argument('--plot')
    c.add_argument('--show', default='', help='plot only these OSM runs (names, comma-separated)')
    c.add_argument('--along', action='store_true')
    a = ap.parse_args()
    (fetch if a.cmd == 'fetch' else check)(a)


if __name__ == '__main__':
    main()
