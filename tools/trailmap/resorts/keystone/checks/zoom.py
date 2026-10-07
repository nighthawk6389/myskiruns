"""zoom.py prefix x0,y0,x1,y1 ...  (PDF pt) - the PDF rendered with every piece drawn and tagged 'id:auto-name'
('?' unassigned, '!' several names), one prefix_<k>.jpg per box. Z env = zoom (default 3); ASSIGN env = build.py's
assign.json (default $KEYSTONE_WORK/assign.json); FINAL env = a {piece id: name} JSON to tag instead (scratch:
k_zoom.py; the reg/t_*.jpg region crops)."""
import json
import os
import sys

import pymupdf
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from common import PDF, data, work  # noqa: E402

page = pymupdf.open(PDF)[0]
X0, Y0, CW, CH = 0, 90, 1530, 990
P = json.load(open(data('linePolylines.json')))['polylines']
A = json.load(open(os.environ.get('ASSIGN', work('assign.json'))))['assign']
F = {k: str(v) for k, v in json.load(open(os.environ['FINAL'])).items()} if os.environ.get('FINAL') else None
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
C = {'blue': (255, 0, 255), 'black': (255, 110, 0), 'green': (0, 230, 230)}
z = float(os.environ.get('Z', '3'))
for k, b in enumerate(sys.argv[2:]):
    x0, y0, x1, y1 = map(float, b.split(','))
    pix = page.get_pixmap(clip=pymupdf.Rect(x0, y0, x1, y1), matrix=pymupdf.Matrix(z, z))
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('RGBA')
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    tags = []
    for p in P:
        pts = [((X0 + x * CW / 100 - x0) * z, (Y0 + y * CH / 100 - y0) * z) for x, y in p['points']]
        ins = [q for q in pts if 0 <= q[0] < im.width and 0 <= q[1] < im.height]
        if not ins:
            continue
        d.line(pts, fill=C[p['cls']] + (170,), width=3)
        for e in (pts[0], pts[-1]):
            d.ellipse((e[0] - 3, e[1] - 3, e[0] + 3, e[1] + 3), fill=(255, 0, 0, 220))
        q = ins[len(ins) // 2]
        if F is not None:
            t = f"{p['id']}:{F[str(p['id'])][:14]}" if str(p['id']) in F else f"{p['id']}?"
        else:
            nm = A.get(str(p['id']), [])
            t = f"{p['id']}" + (f":{nm[0][:12]}" if len(nm) == 1 else ('?' if not nm else '!'))
        tags.append((q, t))
    for (x, y), t in tags:
        w = d.textlength(t, font=f)
        d.rectangle((x + 3, y - 8, x + w + 7, y + 8), fill=(255, 255, 0, 200)); d.text((x + 5, y - 8), t, fill=(0, 0, 0, 255), font=f)
    Image.alpha_composite(im, ov).convert('RGB').save(f'{sys.argv[1]}_{k}.jpg', quality=88)
print(len(sys.argv) - 2, 'crops')
