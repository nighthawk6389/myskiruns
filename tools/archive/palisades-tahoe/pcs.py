"""pcs.py PANEL OUT id[,id..] [--m 70] [--w 700]: one cell per piece: the PDF rendered sharp around it (margin m map
px), the piece drawn translucent red with its id at both ends, other pieces thin with id:name, labels magenta."""
import importlib.util, json, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
P_, out, ids = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3].split(',')]
m = float(sys.argv[sys.argv.index('--m') + 1]) if '--m' in sys.argv else 70
CW = int(sys.argv[sys.argv.index('--w') + 1]) if '--w' in sys.argv else 700
H = '/home/user/myskiruns/tools/trailmap/resorts/palisades-tahoe'
W = f'/home/user/myskiruns/work/palisades-tahoe/{P_}'
spec = importlib.util.spec_from_file_location('r', f'{H}/panels/{P_}/resort.py')
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
pdf = {'palisades': 'palisades_main.pdf', 'alpine-front': 'alpine_front.pdf', 'alpine-back': 'alpine_back.pdf'}[P_]
page = pymupdf.open(f'/home/user/myskiruns/work/palisades-tahoe/{pdf}')[0]
x0c, y0c, x1c, y1c = R.CLIP
WW, HH = (x1c - x0c) * R.SCALE, (y1c - y0c) * R.SCALE
P = json.load(open(f'{W}/pieces_cut.json'))['polylines']; N = json.load(open(f'{W}/names.json'))
D = json.load(open(f'{W}/printed.json'))
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
    for l in D['labels']:
        q = [trp(v) for v in l['pts']]
        if any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q):
            d.line(q, fill=(255, 0, 255, 200), width=1)
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
