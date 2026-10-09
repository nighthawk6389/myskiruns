"""Per interactive-map label: the offset (dx, dy within +-R px) that best puts its letter boxes on the print's ink."""
import json, sys, math
import numpy as np
from PIL import Image
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap/resorts/steamboat')
import prepare as P
img = np.asarray(Image.open('/home/user/myskiruns/work/steamboat/map.png').convert('RGB')).astype(float)
V = json.load(open('/home/user/myskiruns/work/steamboat/vicomap/trails.json'))
ink = {'black': img.max(axis=2) < 90}
for k, c in P.INK.items():
    ink[k] = np.linalg.norm(img - np.array(c), axis=2) < 70
R = 30
h, w = img.shape[:2]
out = []
for t in V['trails']:
    col = [f for f in t['fills'] if P.CLS.get(f['fill']) and not P.symbol_shape(f)]
    if not col:
        continue
    cls = P.CLS[col[0]['fill']]
    m = ink[cls]
    boxes = [(P.tf(f['box'][:2]), P.tf(f['box'][2:])) for f in col]
    def score(dx, dy):
        tot = 0
        for (x0, y0), (x1, y1) in boxes:
            sub = m[max(0, int(y0 + dy)):min(h, int(y1 + dy) + 1), max(0, int(x0 + dx)):min(w, int(x1 + dx) + 1)]
            tot += sub.mean() if sub.size else 0
        return tot / len(boxes)
    best = max(((score(dx, dy), dx, dy) for dx in range(-R, R + 1, 2) for dy in range(-R, R + 1, 2)))
    s0 = score(0, 0)
    cx = sum((a[0] + b[0]) / 2 for a, b in boxes) / len(boxes)
    cy = sum((a[1] + b[1]) / 2 for a, b in boxes) / len(boxes)
    out.append((t['name'], round(cx), round(cy), round(s0, 2), round(best[0], 2), best[1], best[2]))
for r in sorted(out, key=lambda r: -math.hypot(r[5], r[6])):
    print(r)
