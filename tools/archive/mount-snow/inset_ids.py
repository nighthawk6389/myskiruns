"""Mount Snow: the Sunbrook inset's pieces (from pdf_resort.py's pieces_cut.json, put back through
resort.INSET_AFFINE) drawn with their ids on a 3.5x render of the 2023-24 PDF's inset, whose names (outlined glyphs)
are legible there; read to settle the inset's pieces (decisions.py) and place its names (resort.EXTRA).

    python3 -I tools/archive/mount-snow/inset_ids.py <out.png> [first id] [last id] [work dir]
"""
import colorsys
import json
import os
import sys

import pymupdf
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../../trailmap/resorts/mount-snow'))
import resort as R  # noqa: E402

out = sys.argv[1]
lo, hi = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 10 ** 6)
W = sys.argv[4] if len(sys.argv) > 4 else 'work/mount-snow'
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
Z, X0, Y0 = 3.5, 8, 0
A = R.INSET_AFFINE
mw, mh = R.BOX[2] - R.BOX[0], R.BOX[3] - R.BOX[1]
p = pymupdf.open(os.path.join(W, 'mountsnow_2023-24.pdf'))[0]
pix = p.get_pixmap(matrix=pymupdf.Matrix(Z, Z), clip=pymupdf.Rect(X0, Y0, 355, 259))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.35)
d = ImageDraw.Draw(im)
for q in json.load(open(os.path.join(W, 'pieces_cut.json')))['polylines']:
    if not lo <= q['id'] <= hi:
        continue
    pts = []
    for x, y in q['points']:  # percent of the map -> image px -> the inset's points -> this render
        X, Y = x * mw / 100 + R.BOX[0], y * mh / 100 + R.BOX[1]
        u, v = (X - A[2]) / A[0], (Y - A[5]) / A[4]
        if not (R.INSET[0] <= u <= R.INSET[2] and R.INSET[1] <= v <= R.INSET[3]):
            break
        pts.append(((u - X0) * Z, (v - Y0) * Z))
    else:
        if len(pts) < 2:
            continue
        col = tuple(int(255 * c) for c in colorsys.hsv_to_rgb((q['id'] * 0.618) % 1, 1, 0.85))
        d.line(pts, fill=col, width=5)
        m = pts[len(pts) // 2]
        d.text((m[0] + 6, m[1] - 10), str(q['id']), fill=col, font=F, stroke_width=3, stroke_fill='white')
        for e in (pts[0], pts[-1]):
            d.ellipse((e[0] - 5, e[1] - 5, e[0] + 5, e[1] + 5), outline=col, width=3)
im.save(out)
