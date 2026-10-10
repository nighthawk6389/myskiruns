import numpy as np, cv2, sys, json
from PIL import Image
png, printed = sys.argv[1], sys.argv[2]
A = np.asarray(Image.open(png).convert('RGB')).astype(np.int16)
r, g, b = A[..., 0], A[..., 1], A[..., 2]; mx, mn = A.max(2), A.min(2)
M = {'circle': (g > 90) & (g - r > 45) & (g - b > 15) & (r < 110),
     'square': (b > 150) & (b - r > 90) & (b - g > 25) & (r < 110),
     'diamond': (mx < 60) & (mx - mn < 30)}
known = [tuple(s['c']) for s in json.load(open(printed))['symbols']]
lo, hi = float(sys.argv[3]), float(sys.argv[4])
for kind, m in M.items():
    n, lab, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if not (lo <= max(w, h) <= hi): continue
        fill = a / (w * h)
        if kind == 'circle' and not (0.85 <= w / h <= 1.18 and 0.65 <= fill <= 0.9): continue
        if kind == 'square' and not (0.85 <= w / h <= 1.18 and fill > 0.85): continue
        if kind == 'diamond' and not (1.2 <= h / w <= 1.9 and 0.4 <= fill <= 0.65): continue
        c = (round(cen[i][0]), round(cen[i][1]))
        near = min((np.hypot(c[0] - k[0], c[1] - k[1]) for k in known), default=999)
        if near > 12:
            print(kind, c, (w, h), round(fill, 2))
