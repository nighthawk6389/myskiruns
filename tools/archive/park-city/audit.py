"""audit4.py PANEL OUT [--per 4] [--max 560] [--only id,id]: per-trail audit cells for a Whistler Blackcomb panel, 2x2 per
sheet: the map crop around the trail's overlay and its printed names; the trail's overlay thick orange (red dots at
part ends; a marker is a circle), other overlays thin cyan, each label printing the trail's name boxed in magenta.
The caption: id, name, difficulty, how its pieces were named (auto / checked / stretch)."""
import argparse
import io
import contextlib
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
ap = argparse.ArgumentParser()
ap.add_argument('panel', help='ignored')
ap.add_argument('out')
ap.add_argument('--per', type=int, default=6)
ap.add_argument('--max', type=int, default=420)
ap.add_argument('--only', default='')
a = ap.parse_args()
D = '/home/user/myskiruns/src/data/resorts/park-city'
r = pr.Resort('park-city')
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
Image.MAX_IMAGE_PIXELS = None
img = Image.open(r.work('map.png')).convert('RGB')
W, H = img.size
paths = json.load(open(f'{D}/trailPaths.json'))['trails']
ts = open(f'{D}/trails.ts').read()
info = {m.group(1): (m.group(3), m.group(4)) for m in re.finditer(
    r"id: '([^']+)', name: (['\"])(.*?)\2, difficulty: '([^']+)'", ts)}


def slug(nm):
    return re.sub(r'[^a-z0-9]+', '-', nm.lower().replace('’', '').replace("'", '')).strip('-')


labels = {}
for n in r.names_:
    labels.setdefault(slug(n['name']), []).append(n)
how = {}
for pid, v in r.assign.items():
    k = slug(next(iter(v)))
    w = r.why.get(pid, '')
    tag = 'stretch' if pid in r.traced else ('checked' if w == 'checked' else 'auto')
    how.setdefault(k, set()).add(tag)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
px = lambda q: (q[0] * W / 100, q[1] * H / 100)  # noqa: E731
ids = [i for i in (a.only.split(',') if a.only else sorted(paths)) if i in paths and i in info]
os.makedirs(a.out, exist_ok=True)
cells = []
for tid in ids:
    p = paths[tid]
    pts = [px(q) for s in p.get('segments', []) for q in s] + ([px(p['label'])] if p.get('label') else [])
    pts += [q for n in labels.get(tid, []) for q in n['pts']]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    box = (max(0, int(min(xs)) - 70), max(0, int(min(ys)) - 70), min(W, int(max(xs)) + 70), min(H, int(max(ys)) + 70))
    s = min(2.5, a.max / max(box[2] - box[0], box[3] - box[1]))
    crop = img.crop(box).resize((int((box[2] - box[0]) * s), int((box[3] - box[1]) * s)), Image.LANCZOS).convert('RGBA')
    ov = Image.new('RGBA', crop.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    tr = lambda q: ((q[0] - box[0]) * s, (q[1] - box[1]) * s)  # noqa: E731
    for oid, op in paths.items():
        if oid == tid:
            continue
        for seg in op.get('segments', []):
            d.line([tr(px(q)) for q in seg], fill=(0, 230, 255, 110), width=2)
    for n in labels.get(tid, []):
        lx = [q[0] for q in n['pts']]; ly = [q[1] for q in n['pts']]
        b = tr((min(lx) - 8, min(ly) - 8)) + tr((max(lx) + 8, max(ly) + 8))
        d.rectangle(b, outline=(255, 0, 255, 230), width=2)
    for seg in p.get('segments', []):
        d.line([tr(px(q)) for q in seg], fill=(255, 110, 0, 190), width=5)
        for e in (seg[0], seg[-1]):
            x, y = tr(px(e)); d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 0, 0, 230))
    if p.get('label'):
        x, y = tr(px(p['label'])); d.ellipse((x - 10, y - 10, x + 10, y + 10), outline=(255, 110, 0, 255), width=4)
    cell = Image.alpha_composite(crop, ov).convert('RGB')
    cap = Image.new('RGB', (cell.width, cell.height + 20), 'white'); cap.paste(cell, (0, 20))
    nm, dif = info[tid]
    ImageDraw.Draw(cap).text((3, 2), f"{tid}: {nm} ({dif}) x{s:.1f} {'+'.join(sorted(how.get(tid, {'marker'})))}"
                             f"{' MARKER' if p.get('label') else ''}", fill='black', font=F)
    cells.append((tid, cap))
for k in range(0, len(cells), a.per):
    grp = cells[k:k + a.per]
    cw = max(c.width for _, c in grp); ch = max(c.height for _, c in grp)
    cols = 3
    rows = (len(grp) + 2) // 3
    sheet = Image.new('RGB', (cols * cw + 10, rows * ch + 10 * (rows - 1)), (90, 90, 90))
    for n, (_, c) in enumerate(grp):
        sheet.paste(c, ((n % 3) * (cw + 10), (n // 3) * (ch + 10)))
    sheet.save(f"{a.out}/{k // a.per:03d}_{'+'.join(t for t, _ in grp)}.jpg", quality=85)
print(len(cells), 'trails ->', a.out)
