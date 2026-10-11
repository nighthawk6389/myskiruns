"""Stratton: the 2022-23 export's fills in the runs' colours (its dashed lines, a fill per line, and its symbols)
outlined over this season's image, zoomed on a box: does it draw this season's lines?

    python3 -I tools/archive/stratton/fills22_over.py <work dir> <a,b,c,d,e,f> x0,y0,x1,y1 <zoom> <out.png>
"""
import os
import sys

import pymupdf
from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None
W, A = sys.argv[1], tuple(float(v) for v in sys.argv[2].split(','))
x0, y0, x1, y1 = (int(v) for v in sys.argv[3].split(','))
z = float(sys.argv[4])
im = Image.open(os.path.join(W, 'map2025.png')).convert('RGB').crop((x0, y0, x1, y1))
im = im.resize((round(im.width * z), round(im.height * z)), Image.LANCZOS)
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.4)
d = ImageDraw.Draw(im)
COLS = {(0.05, 0.49, 0.25): (0, 200, 0), (0.08, 0.46, 0.74): (0, 90, 255), (0.14, 0.12, 0.13): (255, 0, 255),
        (0.01, 0.02, 0.02): (255, 120, 0)}


def px(p):
    return ((A[0] * p.x + A[1] * p.y + A[2] - x0) * z, (A[3] * p.x + A[4] * p.y + A[5] - y0) * z)


for dr in pymupdf.open(os.path.join(W, 'stratton_2022-23.pdf'))[0].get_drawings():
    c = tuple(round(v, 2) for v in dr.get('fill') or ())
    if dr['type'] not in ('f', 'fs') or c not in COLS:
        continue
    cur = []
    for it in dr['items']:
        if it[0] == 'l':
            ps = [it[1], it[2]]
        elif it[0] == 'c':
            ps = [it[1], it[2], it[3], it[4]]
        elif it[0] == 're':
            r = it[1]; ps = [r.tl, r.tr, r.br, r.bl, r.tl]
        elif it[0] == 'qu':
            q = it[1]; ps = [q.ul, q.ur, q.lr, q.ll, q.ul]
        else:
            continue
        pts = [px(p) for p in ps]
        d.line(pts, fill=COLS[c], width=1)
im.save(sys.argv[5])
