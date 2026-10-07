"""Difficulty symbols on a Vail panel: solid squarish fills in a trail colour (blue square, green circle, black
diamond); a black pair of diamonds (two diamonds touching: a 2:1 rotated box with a notch) is a double diamond, and
one holding white letters (two or more holes) is EX. Writes syms_<panel>.json [{i, t, c:[x,y], r}]."""
import json, sys, math, collections
import numpy as np, cv2
from PIL import Image
from vl_lines import masks
Image.MAX_IMAGE_PIXELS = None
SIZE = {'front-side': (13, 24), 'back-bowls': (19, 30), 'blue-sky': (40, 62)}  # single symbol size per panel, px
EXCLUDE = {'front-side': [(0, 2050, 1700, 2594), (3600, 2250, 4990, 2594), (4335, 876, 4734, 1008)], 'back-bowls': [(45, 1620, 990, 1980)],
           'blue-sky': [(105, 2790, 600, 3180)]}
panel = sys.argv[1]; lo, hi = SIZE[panel]
# a double diamond's pair is drawn smaller than a single diamond: its area is about one single's to two
DOUBLE_AREA = {'front-side': (150, 330), 'back-bowls': (240, 560), 'blue-sky': (1150, 2700)}
A = np.asarray(Image.open(f'{panel}.png').convert('RGB'))
M = masks(A)
for x0, y0, x1, y1 in EXCLUDE[panel]:
    for m in M.values():
        m[y0:y1, x0:x1] = False
out = []
for cls, t in (('blue', 'square'), ('green', 'circle'), ('black', 'diamond')):
    m = M[cls].astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, connectivity=8)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        ext = max(w, h); asp = w / h; fill = a / (w * h)
        if lo <= ext <= hi and 0.75 <= asp <= 1.33 and fill >= 0.48:
            out.append({'t': t, 'c': [float(cen[i][0]), float(cen[i][1])], 'r': float(ext / 2)})
            continue
        if cls != 'black' or not (1.25 * lo <= ext <= 2.3 * hi):
            continue
        comp = (lab[y:y + h, x:x + w] == i).astype(np.uint8)
        cnts, hier = cv2.findContours(comp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts or not (DOUBLE_AREA[panel][0] <= a <= DOUBLE_AREA[panel][1]):
            continue
        holes = sum(1 for k in range(len(cnts)) if hier[0][k][3] >= 0 and cv2.contourArea(cnts[k]) > 2)
        # two lobes: along the principal axis the shape narrows to a waist between two wide parts
        ys, xs = np.nonzero(comp)
        xs = xs - xs.mean(); ys = ys - ys.mean()
        cxx, cyy, cxy = (xs * xs).mean(), (ys * ys).mean(), (xs * ys).mean()
        ang = 0.5 * math.atan2(2 * cxy, cxx - cyy)
        u = xs * math.cos(ang) + ys * math.sin(ang); v = -xs * math.sin(ang) + ys * math.cos(ang)
        bins = np.round(u).astype(int); bins -= bins.min()
        width = np.array([np.ptp(v[bins == b]) if np.any(bins == b) else 0 for b in range(bins.max() + 1)])
        L = len(width)
        if L < 8:
            continue
        mid = width[L // 3: 2 * L // 3 + 1]
        waist = mid.min(); left = width[:L // 2].max(); right = width[L // 2:].max()
        outer = max(cnts, key=cv2.contourArea)
        solidity = cv2.contourArea(outer) / (cv2.contourArea(cv2.convexHull(outer)) or 1)
        hole_area = sum(cv2.contourArea(cnts[k]) for k in range(len(cnts)) if hier[0][k][3] >= 0)
        if waist < 0.6 * min(left, right) and L > 1.4 * min(left, right) and solidity > 0.6:
            if holes == 0:
                kind = 'double-diamond'
            elif holes >= 2 and hole_area < 0.35 * a:
                kind = 'ex'  # white E and X inside (an icon frame has one big hole instead)
            else:
                continue
            out.append({'t': kind, 'c': [float(cen[i][0]), float(cen[i][1])], 'r': float(ext / 2)})
# two separate diamonds side by side also make a double diamond
dia = [s for s in out if s['t'] == 'diamond']
for a in range(len(dia)):
    for b in range(a + 1, len(dia)):
        if dia[a]['t'] != 'diamond' or dia[b]['t'] != 'diamond':
            continue
        if math.dist(dia[a]['c'], dia[b]['c']) < 2.2 * max(dia[a]['r'], dia[b]['r']):
            dia[a]['t'] = 'double-diamond'
            dia[a]['c'] = [(dia[a]['c'][0] + dia[b]['c'][0]) / 2, (dia[a]['c'][1] + dia[b]['c'][1]) / 2]
            dia[b]['t'] = None
out = [s for s in out if s['t']]
out.sort(key=lambda s: (s['c'][1] // 200, s['c'][0]))
for i, s in enumerate(out):
    s['i'] = i
json.dump(out, open(f'syms_{panel}.json', 'w'), indent=0)
print(panel, len(out), dict(collections.Counter(s['t'] for s in out)))
