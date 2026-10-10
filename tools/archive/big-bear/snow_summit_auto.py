import json, math, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from skimage.graph import MCP_Geometric
sys.path.insert(0, 'tools/trailmap')
from vicomap import dense_pts
A = np.asarray(Image.open('work/big-bear/snow-summit.png').convert('RGB')).astype(np.int16)
r, g, b = A[..., 0], A[..., 1], A[..., 2]
mx, mn = A.max(2), A.min(2)
M = {'blue': (b > 170) & (b - r > 120) & (g > 110) & (g < 195) & (r < 70),
     'green': (g > 100) & (g - r > 60) & (g - b > 35) & (r < 70),
     'black': (mx < 45) & (mx - mn < 22)}
CLS = {'#009fe0': 'blue', '#00a0e2': 'blue', '#2d9248': 'green', '#000': 'black'}
AF = (0.4721829, 0.0000057, -8.3442, -0.0000010, 0.4722086, -0.3331)
tf = lambda p: (AF[0] * p[0] + AF[1] * p[1] + AF[2], AF[3] * p[0] + AF[4] * p[1] + AF[5])
V = json.load(open('work/big-bear/vico_1818/trails.json'))
H, W = M['blue'].shape
out = []
for t in V['trails']:
    for pl, st in zip(t['lines'], t['styles']):
        cls = CLS[st['stroke']]
        pts = [tf(q) for q in pl]
        if sum(math.dist(a, c) for a, c in zip(pts, pts[1:])) < 15: continue
        dp = dense_pts(pts, 1.0)
        x0, y0 = max(0, int(min(p[0] for p in dp)) - 45), max(0, int(min(p[1] for p in dp)) - 45)
        x1, y1 = min(W, int(max(p[0] for p in dp)) + 46), min(H, int(max(p[1] for p in dp)) + 46)
        sub = M[cls][y0:y1, x0:x1]
        lm = np.ones(sub.shape, np.uint8)
        for x, y in dp:
            xi, yi = int(round(x)) - x0, int(round(y)) - y0
            if 0 <= yi < lm.shape[0] and 0 <= xi < lm.shape[1]: lm[yi, xi] = 0
        dist = cv2.distanceTransform(lm, cv2.DIST_L2, 3)
        cost = np.where(cv2.dilate(sub.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0, 1.0, 40.0)
        cost[dist > 40] = 1e6
        def snap(q):
            qx, qy = int(round(q[0])) - x0, int(round(q[1])) - y0
            ys, xs = np.nonzero(sub & (dist < 40))
            if not len(xs): return (min(max(qy, 0), sub.shape[0]-1), min(max(qx, 0), sub.shape[1]-1))
            k = np.argmin((xs - qx) ** 2 + (ys - qy) ** 2)
            return (ys[k], xs[k])
        s, e = snap(dp[0]), snap(dp[-1])
        mcp = MCP_Geometric(cost); mcp.find_costs([s], [e])
        path = [(c + x0, rr + y0) for rr, c in mcp.traceback(e)]
        on = np.mean([sub[y - y0, x - x0] for x, y in path])
        out.append({'name': t['name'], 'cls': cls, 'path': path[::3] + [path[-1]], 'vico': pts, 'on': round(float(on), 2)})
json.dump(out, open('work/big-bear/ss_auto.json', 'w'))
im = Image.open('work/big-bear/snow-summit.png').convert('RGB'); d = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
for o in out:
    d.line([tuple(p) for p in o['vico']], fill=(255, 255, 0), width=1)
    d.line([tuple(p) for p in o['path']], fill=(255, 0, 255), width=3)
    m = o['path'][len(o['path']) // 2]
    d.text(m, f"{o['name']} {o['on']}", fill=(255, 0, 255), font=f, stroke_width=2, stroke_fill='white')
im.save('work/big-bear/ss_auto.png')
for o in out: print(o['name'], o['cls'], o['on'], len(o['path']))
