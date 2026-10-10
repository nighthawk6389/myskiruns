"""Tally colours of a crop of the Jackson Hole map: the line/text colours (blue, black, green, red lifts)."""
import sys, collections
import numpy as np
from PIL import Image
im = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
x0, y0, x1, y1 = map(int, sys.argv[2].split(','))
A = im[y0:y1, x0:x1].reshape(-1, 3)
q = (A // 16) * 16
c = collections.Counter(map(tuple, q))
for k, n in c.most_common(int(sys.argv[3]) if len(sys.argv) > 3 else 40):
    r, g, b = k
    print(k, n, 'sat' if max(k) - min(k) > 80 else '')
