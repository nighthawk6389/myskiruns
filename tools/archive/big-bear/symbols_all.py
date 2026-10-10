import numpy as np, cv2, sys, json
from PIL import Image
png = sys.argv[1]
A = np.asarray(Image.open(png).convert('RGB')).astype(np.int16)
r, g, b = A[..., 0], A[..., 1], A[..., 2]; mx, mn = A.max(2), A.min(2)
M = {'circle': (g > 100) & (g - r > 60) & (g - b > 20) & (r < 90),
     'square': (b > 150) & (b - r > 120) & (b - g > 40) & (r < 60),
     'diamond': (mx < 50) & (mx - mn < 20)}
lo, hi = float(sys.argv[2]), float(sys.argv[3])
out = []
for kind, m in M.items():
    n, lab, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if not (lo <= max(w, h) <= hi): continue
        fill = a / (w * h)
        if kind == 'circle' and not (0.8 <= w / h <= 1.25 and 0.65 <= fill <= 0.92): continue
        if kind == 'square' and not (0.8 <= w / h <= 1.25 and fill > 0.85): continue
        if kind == 'diamond' and not (0.75 <= h / w <= 1.6 and 0.4 <= fill <= 0.65): continue
        out.append((kind, (int(round(cen[i][0])), int(round(cen[i][1]))), (int(w), int(h))))
# pairs of diamonds side by side: double
ds = [o for o in out if o[0] == 'diamond']
used = set(); res = []
for i, d in enumerate(ds):
    if i in used: continue
    j = next((j for j, e in enumerate(ds) if j != i and j not in used and abs(e[1][1] - d[1][1]) < 6 and abs(e[1][0] - d[1][0]) < 1.8 * d[2][0]), None)
    if j is not None:
        used |= {i, j}; res.append(('double-diamond', ((d[1][0] + ds[j][1][0]) // 2, d[1][1]), d[2]))
    else:
        used.add(i); res.append(d)
res += [o for o in out if o[0] != 'diamond']
for o in sorted(res, key=lambda o: (o[1][1], o[1][0])): print(o)
