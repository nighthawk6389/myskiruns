"""Contact sheet: each glyph cluster drawn upright (rotated so the direction to the neighbouring glyph of the
same label points right), 3 instances each, with the cluster id and size.

    python3 tools/trailmap/resorts/copper-mountain/checks/sheet.py out.png [id,id,...]   (was cu_sheet.py)

Reads the PDF and clusters.json (cluster.py) in the working folder; every cluster, or only the given ids. Each
cluster's letter, read here once, goes into letters.json by its first glyph's kinds and signature.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import PDF, work  # noqa: E402
import json, math
import pymupdf
from PIL import Image, ImageChops, ImageDraw, ImageFont
p = pymupdf.open(PDF)[0]
D = {d['seqno']: d for d in p.get_drawings()}
C = json.load(open(work('clusters.json')))
G = C['glyphs']
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)


def bez(a, b, c, e, n=8):
    return [((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*c.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*c.y+t**3*e.y)
            for t in [i / n for i in range(1, n + 1)]]


def subpolys(items):
    polys, cur, last = [], [], None
    for it in items:
        if it[0] in ('re', 'qu'):
            continue
        s = it[1]
        if last is not None and math.dist((s.x, s.y), last) > 0.01:
            polys.append(cur); cur = []
        if not cur:
            cur.append((s.x, s.y))
        cur += bez(*it[1:5]) if it[0] == 'c' else [(it[2].x, it[2].y)]
        last = (it[-1].x, it[-1].y)
    if cur:
        polys.append(cur)
    return polys


def direction(i):
    g = G[i]
    best = None
    for j in (i - 1, i + 1):
        if 0 <= j < len(G) and G[j]['col'] == g['col']:
            d = math.dist(G[j]['c'], g['c'])
            if d < 9 and (best is None or d < best[0]):
                best = (d, j)
    if not best:
        return 0.0
    j = best[1]
    a, b = (g['c'], G[j]['c']) if j > i else (G[j]['c'], g['c'])
    return math.atan2(b[1] - a[1], b[0] - a[0])


def render(i, S=40):
    g = G[i]; th = -direction(i)
    polys = subpolys(D[g['seq']]['items'])
    cx, cy = g['c']
    rot = [[((x - cx) * math.cos(th) - (y - cy) * math.sin(th), (x - cx) * math.sin(th) + (y - cy) * math.cos(th)) for x, y in pl] for pl in polys]
    mask = Image.new('1', (S * 2, S * 2), 0)
    for pl in rot:
        m = Image.new('1', mask.size, 0)
        ImageDraw.Draw(m).polygon([(S + x * 4.5, S + y * 4.5) for x, y in pl], fill=1)
        mask = ImageChops.logical_xor(mask, m)
    return mask.convert('L').point(lambda v: 0 if v else 255)


which = range(len(C['clusters'])) if len(sys.argv) < 3 else [int(v) for v in sys.argv[2].split(',')]
cells = []
for k in which:
    c = C['clusters'][k]
    ims = [render(i) for i in c['m'][:3]]
    cells.append((k, c['n'], G[c['m'][0]]['col'], ims))
cols, W, H = 8, 270, 110
sheet = Image.new('RGB', (cols * W, ((len(cells) + cols - 1) // cols) * H), 'white')
d = ImageDraw.Draw(sheet)
for n, (k, cnt, col, ims) in enumerate(cells):
    x, y = (n % cols) * W, (n // cols) * H
    for m, im in enumerate(ims):
        sheet.paste(im, (x + 5 + m * 85, y + 5))
    d.text((x + 5, y + 88), f'#{k} n={cnt} {col}', fill=(200, 0, 0), font=f)
    d.rectangle((x, y, x + W - 2, y + H - 2), outline=(200, 200, 200))
sheet.save(sys.argv[1]); print(len(cells), sheet.size)
