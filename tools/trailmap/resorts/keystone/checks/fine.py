"""fine.py out.png x0,y0,x1,y1 zoom ids...  - the PDF rendered at zoom with the given pieces drawn thin in
distinct colours, numbered at both ends (to see exactly which drawn line a piece is; scratch: k_fine.py, the f_*.png
crops)."""
import json
import os
import sys

import pymupdf
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from common import PDF, data  # noqa: E402

p = pymupdf.open(PDF)[0]
x0, y0, x1, y1 = map(float, sys.argv[2].split(',')); z = float(sys.argv[3]); ids = [int(v) for v in sys.argv[4:]]
pix = p.get_pixmap(clip=pymupdf.Rect(x0, y0, x1, y1), matrix=pymupdf.Matrix(z, z))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('RGBA')
ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
P = {q['id']: q for q in json.load(open(data('linePolylines.json')))['polylines']}
COLS = [(255, 0, 255), (0, 200, 255), (255, 140, 0), (0, 220, 0), (255, 0, 0), (140, 0, 255), (0, 120, 255), (200, 200, 0)]
for k, i in enumerate(ids):
    c = COLS[k % len(COLS)]
    pts = [((q[0] * 15.3 - x0) * z, (90 + q[1] * 9.9 - y0) * z) for q in P[i]['points']]
    d.line(pts, fill=c + (200,), width=2)
    for e in (pts[0], pts[-1]):
        d.ellipse((e[0] - 4, e[1] - 4, e[0] + 4, e[1] + 4), outline=c + (255,), width=2)
        d.text((e[0] + 5, e[1] - 16), str(i), fill=c + (255,), font=f, stroke_width=2, stroke_fill=(255, 255, 255, 255))
Image.alpha_composite(im, ov).convert('RGB').save(sys.argv[1]); print(im.size)
