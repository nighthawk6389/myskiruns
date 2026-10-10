"""Jackson Hole: colour masks for the trail lines and names (blue, black, green), drawn alone on the faded map."""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, 'tools/trailmap')
import raster_lines as rl
A = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.int16)
r, g, b = A[..., 0], A[..., 1], A[..., 2]
mx, mn = A.max(2), A.min(2)
M = {'blue': (r < 70) & (b > 170) & (b - r > 120) & (g > 100) & (g < 200) & (b - g > 25),
     'green': (r < 90) & (g > 110) & (g - r > 60) & (g - b > 10),
     'black': (mx < 45) & (mx - mn < 20)}
vis = (A * 0.35 + 165).astype(np.uint8)
col = {'blue': (0, 90, 255), 'green': (0, 170, 0), 'black': (0, 0, 0)}
for k, m in M.items():
    print(k, int(m.sum()))
    vis[m] = col[k]
x0, y0, x1, y1 = map(int, sys.argv[3].split(','))
Image.fromarray(vis[y0:y1, x0:x1]).save(sys.argv[2])
