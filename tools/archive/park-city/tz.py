"""tz.py OUT tid[,tid...] [--box x0,y0,x1,y1 (map px)] [--zoom Z] [--pieces]: the PDF rendered sharp around the given
trails' overlays, plain on top, below with every overlay drawn thin (the given trails red/orange, others cyan, each
with its name at its middle); --pieces: piece ids from names.json instead of trail names on the given trails."""
import json, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]; want = sys.argv[2].split(',')
arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d  # noqa: E731
W, H = 4365, 2275
T = json.load(open('/home/user/myskiruns/src/data/resorts/park-city/trailPaths.json'))['trails']
px = lambda q: (q[0] * W / 100, q[1] * H / 100)  # noqa: E731
if arg('--box'):
    box = tuple(map(float, arg('--box').split(',')))
else:
    pts = [px(q) for t in want for s in T[t].get('segments', []) for q in s] + [px(T[t]['label']) for t in want if T[t].get('label')]
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
    box = (min(xs) - 40, min(ys) - 40, max(xs) + 40, max(ys) + 40)
z = float(arg('--zoom', 0)) or min(10.0, 1400 / ((box[2] - box[0]) / 2.5))
pt = lambda q: (q[0] / 2.5 + 12, q[1] / 2.5 + 12)  # noqa: E731
r0, r1 = pt(box[:2]), pt(box[2:])
page = pymupdf.open('/home/user/myskiruns/work/park-city/parkcity.pdf')[0]
pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*r0, *r1))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
ov = im.copy(); d = ImageDraw.Draw(ov)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
tr = lambda q: ((pt(q)[0] - r0[0]) * z, (pt(q)[1] - r0[1]) * z)  # noqa: E731
inside = lambda q: 0 <= q[0] <= im.width and 0 <= q[1] <= im.height  # noqa: E731
cols = [(255, 0, 0), (255, 120, 0), (200, 0, 200), (0, 160, 0)]
for tid, p in T.items():
    k = want.index(tid) if tid in want else -1
    for s in p.get('segments', []):
        q = [tr(px(v)) for v in s]
        if not any(inside(v) for v in q):
            continue
        d.line(q, fill=cols[k % 4] if k >= 0 else (0, 200, 230), width=3 if k >= 0 else 2)
        for e in (q[0], q[-1]):
            d.ellipse((e[0] - 4, e[1] - 4, e[0] + 4, e[1] + 4), outline=cols[k % 4] if k >= 0 else (0, 150, 200), width=2)
        m = q[len(q) // 2]
        if inside(m):
            d.text((m[0] + 4, m[1] - 14), tid, fill=cols[k % 4] if k >= 0 else (0, 90, 160), font=F)
    if p.get('label'):
        m = tr(px(p['label']))
        if inside(m):
            d.ellipse((m[0] - 6, m[1] - 6, m[0] + 6, m[1] + 6), outline=(255, 0, 255), width=2)
            d.text((m[0] + 7, m[1] - 7), tid + ' (marker)', fill=(160, 0, 160), font=F)
sheet = Image.new('RGB', (im.width, im.height * 2 + 6), (90, 90, 90))
sheet.paste(im, (0, 0)); sheet.paste(ov, (0, im.height + 6))
sheet.save(out, quality=88); print(out, sheet.size, 'zoom', round(z, 2), 'box', [round(v) for v in box])
