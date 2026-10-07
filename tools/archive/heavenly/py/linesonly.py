"""Render only the line-colour fills (blue, green, dark lines) of the 2022 page in a main-map box, over a faded copy
of the 2024 image: linesonly.py out x0,y0,x1,y1 zoom"""
import sys, numpy as np, pymupdf
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap/resorts/heavenly')
sys.path.insert(0, '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/hv/tools')
import prepare as P
from redraw import redraw
out, box, z = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], float(sys.argv[3])
pg = pymupdf.open('/home/user/myskiruns/work/heavenly/heavenly_2022.pdf')[0]
A = P.top().AFFINE['main']
x0 = (box[0] - A[2]) / A[0]; y0 = (box[1] - A[5]) / A[4]; x1 = (box[2] - A[2]) / A[0]; y1 = (box[3] - A[5]) / A[4]
clip = pymupdf.Rect(x0, y0, x1, y1)
D = []
for d in pg.get_drawings():
    f = d.get('fill') if d['type'] == 'f' else None
    if f and any(max(abs(a - b) for a, b in zip(f, c)) < 0.01 for c in (P.BLUE, P.GREEN)) and d['rect'].intersects(clip):
        D.append(d)
s = A[0] * z
a = redraw(pg, D, s, clip=clip)
im = Image.fromarray(a)
base = Image.open('/home/user/myskiruns/work/heavenly/main/map.png').convert('RGB').crop(box).resize(im.size)
fade = Image.blend(base, Image.new('RGB', im.size, 'white'), 0.75)
arr = np.asarray(im).astype(int); m = (arr.sum(2) < 600)
res = np.asarray(fade).copy(); res[m] = arr[m]
Image.fromarray(res.astype(np.uint8)).save(out)
print(out, im.size, len(D))
