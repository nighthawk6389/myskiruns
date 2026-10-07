"""Vail label text: black glyph components (dark ink crowded by other glyph-sized parts), and for each named symbol
the chain of glyphs that starts beside it (its printed name). Writes text_<panel>.json:
{symbol index: {"pts": [glyph centres in chain order], "end": [x, y], "axis": [ux, uy], "h": glyph height}}."""
import json, math, sys
import numpy as np, cv2
from PIL import Image
from scipy.spatial import cKDTree
Image.MAX_IMAGE_PIXELS = None
exec(open('vl_symnames.py').read())
GLYPH = {'front-side': (8, 34), 'back-bowls': (12, 75), 'blue-sky': (20, 80)}  # glyph height range, px
panel = sys.argv[1]
gmin, gmax = GLYPH[panel]
A = np.asarray(Image.open(f'{panel}.png').convert('RGB')).astype(np.int16)
mx = A.max(2); mn = A.min(2)
ink = (mx < 90) & (mx - mn < 30)
n, lab, st, cen = cv2.connectedComponentsWithStats(ink.astype(np.uint8), connectivity=8)
G = []
for i in range(1, n):
    x, y, w, h, a = st[i]
    if gmin <= h <= gmax and w <= 1.6 * gmax and a >= 12 and a < 0.8 * w * h + 1:
        G.append((i, (float(cen[i][0]), float(cen[i][1])), (int(x), int(y), int(x + w), int(y + h))))
pts = np.array([c for _, c, _ in G])
tree = cKDTree(pts)


def bbox_gap(a, b):
    dx = max(0, max(a[0], b[0]) - min(a[2], b[2])); dy = max(0, max(a[1], b[1]) - min(a[3], b[3]))
    return math.hypot(dx, dy)


S = json.load(open(f'syms_{panel}.json'))
out = {}
for s in S:
    name = NAMES.get(panel, {}).get(s['i'])
    if not name or name == '?':
        continue
    c, r = s['c'], s['r']
    sb = (c[0] - r, c[1] - r, c[0] + r, c[1] + r)
    # first glyph: nearest glyph whose box is within ~one glyph height of the symbol's box
    near = tree.query_ball_point(c, r + 2.5 * gmax)
    near = [k for k in near if bbox_gap(sb, G[k][2]) < 0.9 * (G[k][2][3] - G[k][2][1])]
    if not near:
        continue
    chain = [min(near, key=lambda k: bbox_gap(sb, G[k][2]))]
    h0 = G[chain[0]][2][3] - G[chain[0]][2][1]
    seen = set(chain)
    frontier = list(chain)
    while frontier and len(chain) < 45:
        k = frontier.pop()
        for j in tree.query_ball_point(G[k][1], 2.2 * h0):
            if j in seen:
                continue
            hj = G[j][2][3] - G[j][2][1]
            if not (0.45 * h0 <= hj <= 2.2 * h0):
                continue
            if bbox_gap(G[k][2], G[j][2]) < 0.75 * h0:
                seen.add(j); chain.append(j); frontier.append(j)
    P = [G[k][1] for k in chain]
    far = max(P, key=lambda q: math.dist(q, c))
    d = math.dist(far, c) or 1
    out[s['i']] = {'pts': [[round(x, 1), round(y, 1)] for x, y in P], 'end': [round(far[0], 1), round(far[1], 1)],
                   'axis': [(far[0] - c[0]) / d, (far[1] - c[1]) / d], 'h': h0}
json.dump(out, open(f'text_{panel}.json', 'w'))
print(panel, len(G), 'glyphs;', len(out), 'labels chained; long chains:',
      [(NAMES[panel][i], len(v['pts'])) for i, v in out.items() if len(v['pts']) > 30][:10])
