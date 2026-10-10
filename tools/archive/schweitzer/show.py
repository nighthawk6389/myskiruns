"""Review crops for Schweitzer's panels: the map with prepare.py's labels (a magenta line through each label's letter
centres, its name at its first letter), symbols (a ring: S square, D diamond, DD double, C circle, with its group's
name) and cat-track pieces (cyan), or after a build pdf_resort.py's pieces with their names, on a grid in map px.

    python3 tools/archive/schweitzer/show.py <panel> <out dir> <zoom> x0,y0,x1,y1 [...]       (repo root)
    python3 tools/archive/schweitzer/show.py <panel> <out dir> <zoom> --built x0,y0,x1,y1 [...]

Reads work/schweitzer/<panel>/{map.png, printed.json ($PRINTED: another), pieces.json} (--built: pieces_cut.json
and names.json).
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

panel, out, zoom = sys.argv[1], sys.argv[2], float(sys.argv[3])
args = sys.argv[4:]
built = '--built' in args
args = [a for a in args if a != '--built']
D = f'work/schweitzer/{panel}'
os.makedirs(out, exist_ok=True)
Image.MAX_IMAGE_PIXELS = None
im = Image.open(f'{D}/map.png').convert('RGB')
W, H = im.size
P = json.load(open(f'{D}/{"pieces_cut" if built else "pieces"}.json'))['polylines']
N = json.load(open(f'{D}/names.json')) if built else {}
pr = json.load(open(os.environ.get('PRINTED', f'{D}/printed.json')))
font = ImageFont.load_default()
for box in args:
    x0, y0, x1, y1 = map(int, box.split(','))
    c = im.crop((x0, y0, x1, y1)).resize((round((x1 - x0) * zoom), round((y1 - y0) * zoom)), Image.LANCZOS)
    d = ImageDraw.Draw(c)

    def m(p):
        return ((p[0] - x0) * zoom, (p[1] - y0) * zoom)
    step = 50 if zoom >= 1.5 else 100
    for gx in range((x0 // step + 1) * step, x1, step):
        d.line([m((gx, y0)), m((gx, y1))], fill=(200, 120, 255), width=1)
        d.text((m((gx, y0))[0] + 2, 2), str(gx), fill=(150, 0, 200), font=font)
    for gy in range((y0 // step + 1) * step, y1, step):
        d.line([m((x0, gy)), m((x1, gy))], fill=(200, 120, 255), width=1)
        d.text((2, m((x0, gy))[1] + 2), str(gy), fill=(150, 0, 200), font=font)
    for p in P:
        pts = [m((x * W / 100, y * H / 100)) for x, y in p['points']]
        d.line(pts, fill=(0, 230, 255), width=2)
        t = f"{p['id']}:{N.get(str(p['id']), p.get('name', ''))}"
        mid = pts[len(pts) // 2]
        d.rectangle([mid[0], mid[1] - 5, mid[0] + d.textlength(t, font=font) + 2, mid[1] + 6], fill=(0, 0, 0))
        d.text((mid[0] + 1, mid[1] - 5), t, fill=(0, 230, 255), font=font)
    if not built:
        for lab in pr['labels']:
            pts = [m(q) for q in lab['pts']]
            if len(pts) > 1:
                d.line(pts, fill=(255, 0, 255), width=2)
            d.ellipse([pts[0][0] - 3, pts[0][1] - 3, pts[0][0] + 3, pts[0][1] + 3], outline=(255, 0, 255), width=2)
            t = lab['text']
            d.rectangle([pts[0][0], pts[0][1] - 14, pts[0][0] + d.textlength(t, font=font) + 2, pts[0][1] - 3],
                        fill=(255, 255, 210))
            d.text((pts[0][0] + 1, pts[0][1] - 14), t, fill=(200, 0, 120), font=font)
        for s in pr['symbols']:
            q = m(s['c'])
            d.ellipse([q[0] - 14, q[1] - 14, q[0] + 14, q[1] + 14], outline=(255, 140, 0), width=2)
            t = {'square': 'S', 'diamond': 'D', 'double-diamond': 'DD', 'circle': 'C'}[s['t']] + ':' + (s.get('group') or '')
            d.text((q[0] + 15, q[1] - 5), t, fill=(255, 100, 0), font=font)
    f = os.path.join(out, f'{panel}_{x0}_{y0}{"_built" if built else ""}.png')
    c.save(f)
    print(f, c.size)
