import numpy as np, cv2, sys
from PIL import Image
from skimage.morphology import skeletonize
sys.path.insert(0, 'tools/trailmap')
import raster_lines as rl
A = np.asarray(Image.open('work/big-bear/snow-summit/map.png').convert('RGB')).astype(np.int16)
mx, mn = A.max(2), A.min(2)
m = (mx < 70) & (mx - mn < 30)
cm = rl.clean(m, [(1730, 1190, 1995, 1625)], k=1.0, text_max=40)
n, lab, st, _ = cv2.connectedComponentsWithStats(cm.astype(np.uint8), connectivity=8)
sk = skeletonize(cm)
skl = np.bincount(lab[sk], minlength=n)
keep = np.zeros(n, bool)
ys, xs = np.nonzero(sk)
L0, S0 = float(sys.argv[1]), float(sys.argv[2])
import collections
pts = collections.defaultdict(list)
for y, x in zip(ys, xs): pts[lab[y, x]].append((x, y))
for i in range(1, n):
    L = skl[i]
    if L < L0: continue
    p = np.array(pts[i]); c = p.mean(0)
    d = np.linalg.norm(p - c, axis=1); a = p[d.argmax()]; b = p[np.linalg.norm(p - a, axis=1).argmax()]
    if np.linalg.norm(a - b) / L < S0: continue
    if st[i, 4] / L > 5: continue
    keep[i] = True
out = keep[lab]
print(n, keep.sum())
vis = (A * 0.3 + 170).astype(np.uint8); vis[cm & ~out] = (255, 150, 150); vis[out] = (0, 0, 0)
Image.fromarray(vis).resize((1250, 930)).save('work/big-bear/ss_black.png')
