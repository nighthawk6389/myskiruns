import sys
import numpy as np
from PIL import Image
sys.path.insert(0, 'tools/trailmap/resorts/jackson-hole'); sys.path.insert(0, 'tools/trailmap')
import prepare as P, raster_lines as rl
A = np.asarray(Image.open('work/jackson-hole/map.png').convert('RGB'))
x0, y0, x1, y1 = map(int, sys.argv[2].split(','))
M = P.masks(A)
vis = (A.astype(np.int16) * 0.3 + 175).astype(np.uint8)
for cls, col, ccol in (('blue', (150, 190, 255), (0, 60, 255)), ('black', (170, 170, 170), (0, 0, 0)), ('green', (150, 230, 150), (0, 150, 0))):
    m = M[cls]
    cm = rl.clean(m, P.EXCLUDE, k=1.0, text_max=P.TEXT_MAX)
    vis[m] = col; vis[cm] = ccol
Image.fromarray(vis[y0:y1, x0:x1]).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.NEAREST).save(sys.argv[1])
