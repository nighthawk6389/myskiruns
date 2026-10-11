"""Mount Snow: the 2023-24 PDF's run strokes (1.0-1.3 pt, in the runs' colours) drawn through a page-to-image affine
on this season's image (faded), to judge a registration by eye: the strokes should lie on the painted lines.

    python3 -I tools/archive/mount-snow/ov23.py <a,b,c,d,e,f> <out.png> [work dir]

The affine maps 2023-24 page points to image px (resort.AFFINE's form); the work dir defaults to work/mount-snow.
Saved at half size.
"""
import os
import sys

import pymupdf
from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None
A = tuple(float(v) for v in sys.argv[1].split(','))
W = sys.argv[3] if len(sys.argv) > 3 else 'work/mount-snow'


def T(x, y):
    return (A[0] * x + A[1] * y + A[2], A[3] * x + A[4] * y + A[5])


p = pymupdf.open(os.path.join(W, 'mountsnow_2023-24.pdf'))[0]
im = Image.open(os.path.join(W, 'mountsnow_2025-26.png')).convert('RGB')
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.5)
d = ImageDraw.Draw(im)
cols = {(0.0, 0.61, 0.86): (0, 0, 255), (0.0, 0.65, 0.32): (0, 170, 0), (0.98, 0.61, 0.14): (255, 120, 0),
        (0.12, 0.1, 0.1): (255, 0, 255), (0.14, 0.12, 0.13): (255, 0, 255)}
for dr in p.get_drawings():
    if dr['type'] not in ('s', 'fs') or not dr.get('color'):
        continue
    c = tuple(round(v, 2) for v in dr['color'])
    w = round(dr.get('width') or 0, 2)
    if c in cols and 1.0 <= w <= 1.3:
        for it in dr['items']:
            pts = [it[1], it[2]] if it[0] == 'l' else ([it[1], it[2], it[3], it[4]] if it[0] == 'c' else [])
            if pts:
                d.line([T(q.x, q.y) for q in pts], fill=cols[c], width=3)
im.resize((im.width // 2, im.height // 2)).save(sys.argv[2])
