"""Jackson Hole: the printed names' letters (glyph-sized components of each colour mask), chained into labels
(letters closer than a letter's height apart), drawn numbered on the map; writes the labels as JSON."""
import json, math, sys, collections
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
A = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.int16)
r, g, b = A[..., 0], A[..., 1], A[..., 2]
mx, mn = A.max(2), A.min(2)
M = {'blue': (r < 70) & (b > 170) & (b - r > 120) & (g > 100) & (g < 200) & (b - g > 25),
     'green': (r < 90) & (g > 110) & (g - r > 60) & (g - b > 10),
     'black': (mx < 45) & (mx - mn < 20)}
TMAX, TMIN, LINK = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
labels = []
for cls, m in M.items():
    n, lab, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    gl = [i for i in range(1, n) if TMIN <= max(st[i, 2], st[i, 3]) <= TMAX and st[i, 4] >= 12]
    # each glyph's pixels' points, to measure gaps between glyphs
    boxes = {i: st[i, :4] for i in gl}
    par = {i: i for i in gl}
    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    # candidate pairs by centre distance, then the real gap between their bounding boxes
    pts = np.array([cen[i] for i in gl]) if gl else np.zeros((0, 2))
    from scipy.spatial import cKDTree
    tree = cKDTree(pts)
    for a, bb in tree.query_pairs(TMAX * 1.6):
        i, j = gl[a], gl[bb]
        xi, yi, wi, hi = boxes[i]; xj, yj, wj, hj = boxes[j]
        dx = max(0, max(xi, xj) - min(xi + wi, xj + wj)); dy = max(0, max(yi, yj) - min(yi + hi, yj + hj))
        hh = max(max(wi, hi), max(wj, hj))
        if math.hypot(dx, dy) <= LINK * hh and 0.4 <= max(wi, hi) / max(wj, hj) <= 2.5:
            par[find(i)] = find(j)
    groups = collections.defaultdict(list)
    for i in gl:
        groups[find(i)].append(i)
    for k, mem in groups.items():
        if len(mem) < 3:
            continue
        c = np.array([cen[i] for i in mem])
        # order along the label: by the principal axis
        mu = c.mean(0); u, s, vt = np.linalg.svd(c - mu); d = vt[0]
        order = np.argsort((c - mu) @ d)
        c = c[order]
        x0 = int(min(boxes[i][0] for i in mem)); y0 = int(min(boxes[i][1] for i in mem))
        x1 = int(max(boxes[i][0] + boxes[i][2] for i in mem)); y1 = int(max(boxes[i][1] + boxes[i][3] for i in mem))
        labels.append({'cls': cls, 'n': len(mem), 'box': [x0, y0, x1, y1], 'pts': [[round(float(x), 1), round(float(y), 1)] for x, y in c]})
labels.sort(key=lambda l: (l['box'][1] // 100, l['box'][0]))
for i, l in enumerate(labels):
    l['id'] = i
json.dump(labels, open(sys.argv[2], 'w'))
print(len(labels), collections.Counter(l['cls'] for l in labels))
