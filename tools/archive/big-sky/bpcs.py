"""bpcs.py RESORT/PANEL OUT id[,id..] [--m 70] [--w 700]: one cell per piece: the PDF rendered sharp around it (margin m
map px), the piece drawn translucent red with its id at both ends, other pieces thin with id:name, names (pdf_resort's
reading) magenta with their text."""
import contextlib, importlib.util, io, json, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
RID, out, ids = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3].split(',')]
m = float(sys.argv[sys.argv.index('--m') + 1]) if '--m' in sys.argv else 70
CW = int(sys.argv[sys.argv.index('--w') + 1]) if '--w' in sys.argv else 700
r = pr.Resort(RID)
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
R = r.R
PDFS = {'big-sky': {'main': 'bigsky_main.pdf', 'south-face': 'bigsky_south-face.pdf', 'bowl': 'bigsky_bowl.pdf'}}
page = pymupdf.open(r.work('../' + PDFS[r.id][r.panel]))[0]
x0c, y0c, x1c, y1c = R.CLIP
WW, HH = r.W, r.H
P = r.load('pieces_cut.json')['polylines']; N = json.load(open(r.work('names.json')))
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
F2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
col = {'green': (0, 150, 60), 'blue': (0, 110, 230), 'black': (40, 40, 40), 'freestyle': (240, 140, 0)}
pts = {p['id']: [(x * WW / 100, y * HH / 100) for x, y in p['points']] for p in P}
cls = {p['id']: p['cls'] for p in P}
cells = []
for i in ids:
    xs = [q[0] for q in pts[i]]; ys = [q[1] for q in pts[i]]
    box = (max(0, min(xs) - m), max(0, min(ys) - m), min(WW, max(xs) + m), min(HH, max(ys) + m))
    z = min(10, CW / (box[2] - box[0]) * R.SCALE, 520 / (box[3] - box[1]) * R.SCALE)
    rect = pymupdf.Rect(box[0] / R.SCALE + x0c, box[1] / R.SCALE + y0c, box[2] / R.SCALE + x0c, box[3] / R.SCALE + y0c)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=rect)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('RGBA')
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    k = z / R.SCALE
    tr = lambda q: ((q[0] - box[0]) * k, (q[1] - box[1]) * k)  # noqa: E731
    trp = lambda q: ((q[0] - rect.x0) * z, (q[1] - rect.y0) * z)  # noqa: E731
    for n in r.names_all:
        q = [tr(v) for v in n['pts']]
        if any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q):
            if len(q) > 1:
                d.line(q, fill=(255, 0, 255, 200), width=1)
            d.text((q[0][0], q[0][1] + 5), n['name'], fill=(200, 0, 200, 255), font=F2, stroke_width=2, stroke_fill=(255, 255, 255, 255))
    for p in P:
        if p['id'] == i:
            continue
        q = [tr(v) for v in pts[p['id']]]
        if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q):
            continue
        nm = N.get(str(p['id']), '?')
        d.line(q, fill=col.get(p['cls'], (128, 0, 128)) + (150,), width=2)
        mp = q[len(q) // 2]
        if 0 <= mp[0] <= im.width and 0 <= mp[1] <= im.height:
            d.text((mp[0] + 3, mp[1] - 6), f"{p['id']}:{nm}", fill=(0, 0, 0, 255), font=F2, stroke_width=2, stroke_fill=(255, 255, 210, 255))
    q = [tr(v) for v in pts[i]]
    d.line(q, fill=(255, 0, 0, 120), width=7)
    for e in (q[0], q[-1]):
        d.ellipse((e[0] - 6, e[1] - 6, e[0] + 6, e[1] + 6), outline=(255, 0, 0, 255), width=3)
    cell = Image.alpha_composite(im, ov).convert('RGB')
    cap = Image.new('RGB', (cell.width, cell.height + 22), 'white'); cap.paste(cell, (0, 22))
    ImageDraw.Draw(cap).text((4, 3), f"#{i} {cls[i]} {N.get(str(i), '?')}  ends ({pts[i][0][0]:.0f},{pts[i][0][1]:.0f})-({pts[i][-1][0]:.0f},{pts[i][-1][1]:.0f})", fill=(200, 0, 0), font=F)
    cells.append(cap)
cols = 2 if max(c.width for c in cells) > 520 else 3
cw = max(c.width for c in cells); ch = max(c.height for c in cells)
sheet = Image.new('RGB', (cols * (cw + 6), ((len(cells) + cols - 1) // cols) * (ch + 6)), (90, 90, 90))
for n, c in enumerate(cells):
    sheet.paste(c, ((n % cols) * (cw + 6), (n // cols) * (ch + 6)))
sheet.save(out); print(out, sheet.size)
