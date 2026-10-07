"""allstrokes.py PANEL OUT x0,y0,x1,y1 (map px) ZOOM: the PDF region sharp, and beside it every trail-coloured stroke
crossing the region redrawn on white with its seqno (d: dashed)."""
import importlib.util, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
P_, out = sys.argv[1], sys.argv[2]; b = list(map(float, sys.argv[3].split(','))); z = float(sys.argv[4])
H = '/home/user/myskiruns/tools/trailmap/resorts/palisades-tahoe'
spec = importlib.util.spec_from_file_location('r', f'{H}/panels/{P_}/resort.py')
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
pdf = {'palisades': 'palisades_main.pdf', 'alpine-front': 'alpine_front.pdf', 'alpine-back': 'alpine_back.pdf'}[P_]
page = pymupdf.open(f'/home/user/myskiruns/work/palisades-tahoe/{pdf}')[0]
pt = lambda x, y: (x / R.SCALE + R.CLIP[0], y / R.SCALE + R.CLIP[1])  # noqa: E731
r0, r1 = pt(b[0], b[1]), pt(b[2], b[3])
pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*r0, *r1))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
ov = Image.new('RGB', im.size, 'white'); d = ImageDraw.Draw(ov)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
TR = {(0.0, 0.65, 0.32): (0, 150, 60), (0.0, 0.61, 0.86): (0, 110, 230), (0.14, 0.12, 0.13): (30, 30, 30), (0.0, 0.0, 0.0): (30, 30, 30)}
tr = lambda p: ((p[0] - r0[0]) * z, (p[1] - r0[1]) * z)  # noqa: E731
inside = lambda q: 0 <= q[0] <= im.width and 0 <= q[1] <= im.height  # noqa: E731
for d0 in page.get_drawings():
    c = tuple(round(v, 2) for v in (d0.get('color') or ()))
    if d0['type'] not in ('s', 'fs') or c not in TR or (d0.get('width') or 0) < 0.5 or (d0.get('width') or 0) > 1.6:
        continue
    pts = []
    for it in d0['items']:
        if it[0] == 'l':
            pts += [tr((it[1].x, it[1].y)), tr((it[2].x, it[2].y))]
        elif it[0] == 'c':
            a, bb, cc, e = it[1:5]
            pts += [tr(((1-t)**3*a.x+3*(1-t)**2*t*bb.x+3*(1-t)*t*t*cc.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*bb.y+3*(1-t)*t*t*cc.y+t**3*e.y)) for t in [j/10 for j in range(11)]]
    if not pts or not any(inside(q) for q in pts):
        continue
    dashed = d0.get('dashes') not in (None, '[] 0')
    d.line(pts, fill=TR[c], width=2)
    for e in (pts[0], pts[-1]):
        d.ellipse((e[0] - 3, e[1] - 3, e[0] + 3, e[1] + 3), outline=TR[c], width=1)
    m = [q for q in pts if inside(q)]; m = m[len(m) // 2]
    d.text((m[0] + 3, m[1] + 2), f"{d0['seqno']}{'d' if dashed else ''}", fill=(200, 0, 0), font=F)
sheet = Image.new('RGB', (im.width * 2 + 6, im.height), (90, 90, 90)); sheet.paste(im, (0, 0)); sheet.paste(ov, (im.width + 6, 0))
sheet.save(out); print(out, sheet.size)
