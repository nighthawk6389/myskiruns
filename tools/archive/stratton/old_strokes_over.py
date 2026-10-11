"""Stratton: the 2020-21 export's run strokes (thin, by drawing number) over this season's image, zoomed on a box:
to see which of its lines this season still draws, moved or anew.

    python3 -I tools/archive/stratton/old_strokes_over.py <work dir> <a,b,c,d,e,f> x0,y0,x1,y1 <zoom> <out.png>
"""
import math
import os
import sys

import pymupdf
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
W, A = sys.argv[1], tuple(float(v) for v in sys.argv[2].split(','))
x0, y0, x1, y1 = (int(v) for v in sys.argv[3].split(','))
z = float(sys.argv[4])
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
im = Image.open(os.path.join(W, 'map2025.png')).convert('RGB').crop((x0, y0, x1, y1))
im = im.resize((round(im.width * z), round(im.height * z)), Image.LANCZOS)
d = ImageDraw.Draw(im)
COLS = {(0.05, 0.49, 0.25): (0, 200, 0), (0.08, 0.46, 0.74): (0, 120, 255), (0.14, 0.12, 0.13): (255, 0, 255)}


def px(p):
    return ((A[0] * p.x + A[1] * p.y + A[2] - x0) * z, (A[3] * p.x + A[4] * p.y + A[5] - y0) * z)


for k, dr in enumerate(pymupdf.open(os.path.join(W, 'stratton_2020-21.pdf'))[0].get_drawings()):
    c = tuple(round(v, 2) for v in dr.get('color') or ())
    if dr['type'] not in ('s', 'fs') or c not in COLS or abs((dr.get('width') or 0) - 1.0) > 0.05:
        continue
    pts = []
    for it in dr['items']:
        ps = [it[1], it[2]] if it[0] == 'l' else ([it[1], it[2], it[3], it[4]] if it[0] == 'c' else [])
        pts += [px(p) for p in ps]
    if not any(0 <= X <= im.width and 0 <= Y <= im.height for X, Y in pts):
        continue
    d.line(pts, fill=COLS[c], width=2)
    mx, my = pts[len(pts) // 2]
    d.text((mx + 3, my - 7), str(k), fill=COLS[c], font=F, stroke_width=2, stroke_fill='white')
for gx in range((x0 // 50 + 1) * 50, x1, 50):
    d.text(((gx - x0) * z + 2, 2), str(gx), fill=(200, 0, 0), font=F)
for gy in range((y0 // 50 + 1) * 50, y1, 50):
    d.text((2, (gy - y0) * z + 2), str(gy), fill=(200, 0, 0), font=F)
im.save(sys.argv[5])
