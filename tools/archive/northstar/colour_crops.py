"""Review crops for Northstar's pieces (whitefish/thin_crops.py with each piece in its own bright colour, the map's
blue and purple lines under them being hard to tell from thin magenta): its id and names at its middle, a dot at
each end, on a labelled grid in map px.

    python3 tools/archive/northstar/colour_crops.py <work dir> <out dir> <zoom> x0,y0,x1,y1 [...]   (repo root)
    python3 tools/archive/northstar/colour_crops.py <work dir> <out dir> <zoom> piece <id> [...]

Reads <work dir>/{map.png, pieces_cut.json, names.json} (pdf_resort.py northstar build writes them).
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W_DIR = sys.argv.pop(1)
out, zoom = sys.argv[1], float(sys.argv[2])
os.makedirs(out, exist_ok=True)
Image.MAX_IMAGE_PIXELS = None
im = Image.open(f'{W_DIR}/map.png').convert('RGB')
W, H = im.size
P = json.load(open(f'{W_DIR}/pieces_cut.json'))['polylines']
if sys.argv[3] == 'piece':
    jobs = []
    for i in map(int, sys.argv[4:]):
        p = next(q for q in P if q['id'] == i)
        xs, ys = [x * W / 100 for x, _ in p['points']], [y * H / 100 for _, y in p['points']]
        jobs.append(((int(min(xs)) - 80, int(min(ys)) - 80, int(max(xs)) + 80, int(max(ys)) + 80), [p]))
else:
    jobs = [(tuple(map(int, b.split(','))), P) for b in sys.argv[3:]]
N = json.load(open(f'{W_DIR}/names.json')) if os.path.exists(f'{W_DIR}/names.json') else {}
font = ImageFont.load_default()
COLOURS = [(255, 230, 0), (0, 255, 120), (255, 60, 60), (0, 230, 255), (255, 140, 0), (255, 0, 255),
           (160, 255, 0), (255, 255, 255)]


def mid(pts):
    L = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    run = 0
    for a, b in zip(pts, pts[1:]):
        d = math.dist(a, b)
        if run + d >= L / 2:
            f = (L / 2 - run) / (d or 1)
            return a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1])
        run += d
    return pts[0]


for (x0, y0, x1, y1), show in jobs:
    z = zoom if len(show) > 1 else min(zoom, 1000 / max(x1 - x0, y1 - y0))
    c = im.crop((x0, y0, x1, y1)).resize((round((x1 - x0) * z), round((y1 - y0) * z)), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    step = 50 if z >= 1.2 else 100
    for gx in range((x0 // step + 1) * step, x1, step):
        d.line([((gx - x0) * z, 0), ((gx - x0) * z, c.height)], fill=(200, 120, 255), width=1)
        d.text(((gx - x0) * z + 2, 2), str(gx), fill=(150, 0, 200), font=font)
    for gy in range((y0 // step + 1) * step, y1, step):
        d.line([(0, (gy - y0) * z), (c.width, (gy - y0) * z)], fill=(200, 120, 255), width=1)
        d.text((2, (gy - y0) * z + 2), str(gy), fill=(150, 0, 200), font=font)
    tags = []
    for p in show:
        pts = [((x * W / 100 - x0) * z, (y * H / 100 - y0) * z) for x, y in p['points']]
        if not any(-50 < x < c.width + 50 and -50 < y < c.height + 50 for x, y in pts):
            continue
        col = COLOURS[p['id'] % len(COLOURS)]
        d.line(pts, fill=col, width=2)
        for e in (pts[0], pts[-1]):
            d.ellipse([e[0] - 4, e[1] - 4, e[0] + 4, e[1] + 4], outline=col, width=2)
        tags.append((mid(pts), f'{p["id"]}:{N.get(str(p["id"]), "")}', col))
    for m, t, col in tags:
        tw = d.textlength(t, font=font)
        d.rectangle([m[0], m[1] - 5, m[0] + tw + 2, m[1] + 6], fill=(0, 0, 0), outline=col)
        d.text((m[0] + 1, m[1] - 5), t, fill=col, font=font)
    f = os.path.join(out, f'piece_{show[0]["id"]}.png' if len(show) == 1 else f'col_{x0}_{y0}.png')
    c.save(f)
    print(f, c.size)
