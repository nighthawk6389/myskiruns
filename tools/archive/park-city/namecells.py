"""namecells.py OUT NAME[,NAME...] [--margin 70] [--zoom 2.2]: one cell per printed label of each name (Park City):
the map crop, the label boxed in magenta, every piece drawn thin in its colour with id:name; a contact sheet of
2 columns."""
import json, sys, io, contextlib
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
Image.MAX_IMAGE_PIXELS = None
out = sys.argv[1]; want = sys.argv[2].split(',')
margin = float(sys.argv[sys.argv.index('--margin') + 1]) if '--margin' in sys.argv else 70
z = float(sys.argv[sys.argv.index('--zoom') + 1]) if '--zoom' in sys.argv else 2.2
r = pr.Resort('park-city')
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
base = Image.open(r.work('map.png')).convert('RGB')
P = [p for p in r.P]
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
F2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 10)
col = {'green': (0, 150, 60), 'blue': (0, 110, 230), 'black': (40, 40, 40), 'freestyle': (240, 140, 0)}
cells = []
for nm in want:
    for n in [n for n in r.names_ if n['name'] == nm]:
        xs = [q[0] for q in n['pts']]; ys = [q[1] for q in n['pts']]
        box = (int(min(xs) - margin), int(min(ys) - margin), int(max(xs) + margin), int(max(ys) + margin))
        im = base.crop(box).resize((int((box[2] - box[0]) * z), int((box[3] - box[1]) * z)), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        tr = lambda q: ((q[0] - box[0]) * z, (q[1] - box[1]) * z)  # noqa: E731
        for p in P:
            q = [tr(v) for v in p['pt']]
            if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q):
                continue
            d.line(q, fill=col.get(p['cls'], (128, 0, 128)), width=1)
        for p in P:
            q = [tr(v) for v in p['pt']]
            if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q) or p['id'] in r.traced:
                continue
            m = q[len(q) // 2]
            lab = next(iter(r.assign.get(p['id'], {'-'})))
            d.text((m[0] + 3, m[1] - 6), f"{p['id']}:{lab}", fill=(0, 0, 0), font=F2, stroke_width=2, stroke_fill=(255, 255, 210))
        b = tr((min(xs) - 5, min(ys) - 5)) + tr((max(xs) + 5, max(ys) + 5))
        d.rectangle(b, outline=(255, 0, 255), width=2)
        cap = Image.new('RGB', (im.width, im.height + 18), 'white'); cap.paste(im, (0, 18))
        ImageDraw.Draw(cap).text((3, 2), f"{nm} ({n.get('symbol')})", fill='black', font=F)
        cells.append(cap)
cw = max(c.width for c in cells); ch = max(c.height for c in cells)
sheet = Image.new('RGB', (2 * cw + 10, ((len(cells) + 1) // 2) * (ch + 10)), (90, 90, 90))
for k, c in enumerate(cells):
    sheet.paste(c, ((k % 2) * (cw + 10), (k // 2) * (ch + 10)))
sheet.save(out); print(out, sheet.size, len(cells))
