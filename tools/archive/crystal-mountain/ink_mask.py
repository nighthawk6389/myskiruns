"""Crystal Mountain: the Northway inset's black ink (every run's line is a black stroke there, whatever its rating) over
a faint copy of the image, with a grid every 100 px labelled in map px: the network of lines to read names.py's
points from.

    python3 -I tools/archive/crystal-mountain/ink_mask.py <work/crystal-mountain/northway/map.png> <out.png>
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

base = Image.open(sys.argv[1]).convert('RGB')
im = np.asarray(base).astype(int)
mx, mn = im.max(axis=2), im.min(axis=2)
m = (mx < 75) & (mx - mn < 25)
out = np.full(im.shape, 255, np.uint8)
out[m] = (0, 0, 0)
o = Image.blend(base, Image.fromarray(out), 0.75)
d = ImageDraw.Draw(o)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
for x in range(0, o.width, 100):
    d.line([(x, 0), (x, o.height)], fill=(255, 0, 255) if x % 500 == 0 else (240, 170, 240), width=1)
    d.text((x + 2, 2), str(x), fill=(200, 0, 200), font=F)
for y in range(0, o.height, 100):
    d.line([(0, y), (o.width, y)], fill=(255, 0, 255) if y % 500 == 0 else (240, 170, 240), width=1)
    d.text((2, y + 2), str(y), fill=(200, 0, 200), font=F)
o.resize((o.width // 2, o.height // 2)).save(sys.argv[2])
