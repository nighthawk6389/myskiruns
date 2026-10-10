"""Snowbird: line pieces from the print's colour masks (raster_lines clean + skeleton), drawn for a look: lines_view.py
<map> x0,y0,x1,y1 <out.png> [text max]. On the front side it kept about half the runs' lines, broken where they
cross the blue-painted trees and shadows, and none of the cased ways down: why the map was read instead."""
import sys, math, json, collections
import numpy as np
from PIL import Image, ImageDraw
from skimage.morphology import skeletonize
sys.path.insert(0, 'tools/trailmap')
import raster_lines as rl
img, box, out = sys.argv[1], tuple(map(int, sys.argv[2].split(','))), sys.argv[3]
A = np.asarray(Image.open(img).convert('RGB').crop(box)).astype(np.int16)
r, g, b = A[..., 0], A[..., 1], A[..., 2]
mx, mn = A.max(2), A.min(2)
M = {'black': (mx < 80) & (mx - mn < 30),
     'blue': (b > 205) & (g > 145) & (g < 205) & (r < 70) & (b - g > 30),
     'green': (g > 130) & (g - r > 90) & (g - b > 50)}
res = []
for cls, m in M.items():
    cm = rl.clean(m, [], k=1.0, text_max=float(sys.argv[4]) if len(sys.argv) > 4 else 20)
    adj = rl.prune(rl.graph(skeletonize(cm)), 8)
    eds, nodes = rl.edges(adj)
    for ch in rl.through_pieces(eds, nodes):
        pts = [(x, y) for y, x in ch]
        L = sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))
        if L >= 20:
            res.append((cls, rl.simplify(pts, 1.0), L))
print(len(res), collections.Counter(c for c, _, _ in res))
im = Image.fromarray(A.astype(np.uint8))
fade = Image.blend(im, Image.new('RGB', im.size, (255, 255, 255)), 0.5)
d = ImageDraw.Draw(fade)
col = {'black': (255, 0, 0), 'blue': (0, 60, 255), 'green': (0, 170, 0)}
for c, pts, L in res:
    d.line(pts, fill=col[c], width=2)
fade.save(out)
json.dump([[c, [list(p) for p in pts]] for c, pts, L in res], open(out + '.json', 'w'))
