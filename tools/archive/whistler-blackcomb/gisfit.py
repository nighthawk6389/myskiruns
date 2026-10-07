"""gisfit.py PANEL 'GISNAME=id,id;GISNAME=id' 'QUERY,QUERY' [out.png box zoom]: fit a local affine map (GIS lon/lat ->
map px) by ICP on the given correspondences (GIS run line -> map pieces), print the residual per run, then project
the QUERY runs and list the pieces they lie on."""
import json, math, os, sys
import numpy as np
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad'
panel, corr, query = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
r = pr.Resort(f'whistler-blackcomb/{panel}')
P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
G = {}
for ft in json.load(open(f'{S}/wb_truth/data/arcgis/features/Ski_Runs_GDB_L1_p0.geojson'))['features']:
    g = ft['geometry']; nm = ft['properties']['run_name']
    if os.environ.get('MOUNTAIN') and ft['properties'].get('mountain') != os.environ['MOUNTAIN']:
        continue
    parts = [g['coordinates']] if g['type'] == 'LineString' else g['coordinates']
    G.setdefault(nm, []).extend(parts)
lat0 = 50.08
def xy(p): return ((p[0] + 122.89) * math.cos(math.radians(lat0)) * 111320, (p[1] - lat0) * 110540)
def dense(pts, step):
    out = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out + [pts[-1]]
pairs = []
for item in corr.split(';'):
    nm, ids = item.split('=')
    src = [q for part in G[nm] for q in dense([xy(p) for p in part], 10)]
    dst = [q for i in ids.split(',') for q in dense(P[int(i)], 3)]
    pairs.append((nm, np.array(src), np.array(dst)))
def solve(A, B):
    X = np.hstack([A, np.ones((len(A), 1))])
    M, *_ = np.linalg.lstsq(X, B, rcond=None)
    return M
def apply(M, A): return np.hstack([A, np.ones((len(A), 1))]) @ M
# init: centroids
M = solve(np.array([s.mean(0) for _, s, _ in pairs]), np.array([d.mean(0) for _, _, d in pairs])) if len(pairs) >= 3 else None
for it in range(60):
    A, B = [], []
    for nm, s, d in pairs:
        t = apply(M, s)
        idx = np.argmin(((t[:, None, :] - d[None, :, :]) ** 2).sum(-1), axis=1)
        A.append(s); B.append(d[idx])
        # and the reverse: each map point to its nearest GIS point (so the whole map line is covered)
        idx2 = np.argmin(((d[:, None, :] - t[None, :, :]) ** 2).sum(-1), axis=1)
        A.append(s[idx2]); B.append(d)
    M = solve(np.vstack(A), np.vstack(B))
for nm, s, d in pairs:
    t = apply(M, s)
    e = np.sqrt(((t[:, None, :] - d[None, :, :]) ** 2).sum(-1).min(1))
    print(f'{nm:24s} mean {e.mean():6.1f} px  max {e.max():6.1f}')
out = {}
for q in query:
    for k, part in enumerate(G[q]):
        t = apply(M, np.array(dense([xy(p) for p in part], 10)))
        out[f'{q}#{k}'] = t.tolist()
        near = {}
        for x, y in t:
            best = min(((pr.line_dist((x, y), pts), i) for i, pts in P.items()))
            if best[0] < 15:
                near[best[1]] = near.get(best[1], 0) + 1
        print(q, k, 'from', [round(v) for v in t[0]], 'to', [round(v) for v in t[-1]], 'pieces (samples within 15px):', sorted(near.items(), key=lambda kv: -kv[1]))
json.dump(out, open(f'{S}/wb/gisproj.json', 'w'))
if len(sys.argv) > 4:
    from PIL import Image, ImageDraw
    o, box, z = sys.argv[4], tuple(map(int, sys.argv[5].split(','))), float(sys.argv[6])
    im = Image.open(f'/home/user/myskiruns/work/whistler-blackcomb/{panel}/map.png').convert('RGB').crop(box)
    im = im.resize((int(im.width * z), int(im.height * z)))
    dr = ImageDraw.Draw(im)
    for nm, s, d in pairs:
        t = apply(M, s); dr.line([((x - box[0]) * z, (y - box[1]) * z) for x, y in t], fill=(0, 200, 0), width=2)
    for k, (nm, t) in enumerate(out.items()):
        c = [(255, 0, 255), (255, 120, 0), (0, 120, 255), (200, 0, 0)][k % 4]
        dr.line([((x - box[0]) * z, (y - box[1]) * z) for x, y in t], fill=c, width=3)
        x, y = t[len(t) // 2]; dr.text(((x - box[0]) * z + 4, (y - box[1]) * z), nm, fill=c)
    im.save(o); print(o)
