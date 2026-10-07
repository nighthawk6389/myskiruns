"""und.py PANEL OUT_DIR [cols rows] [--all]: tiles of the panel's map holding undecided pieces (--all: every piece);
each piece drawn in its colour with id (named ones id:name), undecided ones thick red; printed labels magenta;
symbols red squares. The base is the PDF rendered sharp."""
import importlib.util, json, os, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
P_, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 4
rows = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 3
ALL = '--all' in sys.argv
H = '/home/user/myskiruns/tools/trailmap/resorts/palisades-tahoe'
W = f'/home/user/myskiruns/work/palisades-tahoe/{P_}'
spec = importlib.util.spec_from_file_location('r', f'{H}/panels/{P_}/resort.py')
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
pdf = {'palisades': 'palisades_main.pdf', 'alpine-front': 'alpine_front.pdf', 'alpine-back': 'alpine_back.pdf'}[P_]
page = pymupdf.open(f'/home/user/myskiruns/work/palisades-tahoe/{pdf}')[0]
os.makedirs(out, exist_ok=True)
x0c, y0c, x1c, y1c = R.CLIP
WW, HH = (x1c - x0c) * R.SCALE, (y1c - y0c) * R.SCALE
P = json.load(open(f'{W}/pieces_cut.json'))['polylines']; N = json.load(open(f'{W}/names.json'))
D = json.load(open(f'{W}/printed.json'))
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
F2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
col = {'green': (0, 150, 60), 'blue': (0, 110, 230), 'black': (40, 40, 40), 'freestyle': (240, 140, 0)}
pts = {p['id']: [(x * WW / 100, y * HH / 100) for x, y in p['points']] for p in P}
und = [p['id'] for p in P if ALL or N.get(str(p['id'])) == '?']
tw, th = WW / cols, HH / rows
n = 0
for r in range(rows):
    for c in range(cols):
        x0, y0, x1, y1 = c * tw, r * th, (c + 1) * tw, (r + 1) * th
        mine = [i for i in und if any(x0 <= x < x1 and y0 <= y < y1 for x, y in pts[i][len(pts[i]) // 2: len(pts[i]) // 2 + 1])]
        if not mine:
            continue
        m = 80
        box = (max(0, x0 - m), max(0, y0 - m), min(WW, x1 + m), min(HH, y1 + m))
        z = 1600 / (box[2] - box[0]) * R.SCALE  # px per PDF point
        rect = pymupdf.Rect(box[0] / R.SCALE + x0c, box[1] / R.SCALE + y0c, box[2] / R.SCALE + x0c, box[3] / R.SCALE + y0c)
        pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=rect)
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.25)
        d = ImageDraw.Draw(im)
        k = z / R.SCALE
        tr = lambda q: ((q[0] - box[0]) * k, (q[1] - box[1]) * k)  # noqa: E731
        trp = lambda q: ((q[0] - rect.x0) * z, (q[1] - rect.y0) * z)  # noqa: E731
        for l in D['labels']:
            q = [trp(v) for v in l['pts']]
            if any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q):
                d.line(q, fill=(255, 0, 255), width=1)
        for s in D['symbols']:
            x, y = trp(s['c'])
            if 0 <= x <= im.width and 0 <= y <= im.height:
                d.rectangle((x - 5, y - 5, x + 5, y + 5), outline=(255, 0, 0), width=2)
        for p in P:
            q = [tr(v) for v in pts[p['id']]]
            if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q):
                continue
            nm = N.get(str(p['id']), '?')
            if nm == '?':
                d.line(q, fill=(255, 0, 0), width=5)
            else:
                d.line(q, fill=col.get(p['cls'], (128, 0, 128)), width=2)
            for e in (q[0], q[-1]):
                d.ellipse((e[0] - 4, e[1] - 4, e[0] + 4, e[1] + 4), outline=(255, 0, 0) if nm == '?' else (90, 90, 90), width=2)
        for p in P:
            q = [tr(v) for v in pts[p['id']]]
            if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q):
                continue
            nm = N.get(str(p['id']), '?')
            mpt = q[len(q) // 2]
            if nm == '?':
                d.text((mpt[0] + 5, mpt[1] - 8), str(p['id']), fill=(255, 255, 255), font=F, stroke_width=3, stroke_fill=(200, 0, 0))
            elif not nm.endswith('~'):
                d.text((mpt[0] + 3, mpt[1] - 6), f"{p['id']}:{nm}", fill=(0, 0, 0), font=F2, stroke_width=2, stroke_fill=(255, 255, 210))
        f = f'{out}/r{r}c{c}.png'
        im.save(f); n += 1
        print(f, [i for i in mine], f'box {[round(v) for v in box]}')
print(n, 'tiles')
