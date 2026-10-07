"""Audit sheets: each trail's overlay (orange) over its crop, other trails thin cyan, 2 per sheet.
python3 audit_sheets.py --image src.png --paths trailPaths.json --trails trails.ts --out dir [--only id,id] [--per 2]"""
import argparse, json, os, re
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
ap = argparse.ArgumentParser()
ap.add_argument('--image'); ap.add_argument('--paths'); ap.add_argument('--trails'); ap.add_argument('--out')
ap.add_argument('--only', default=''); ap.add_argument('--per', type=int, default=2); ap.add_argument('--max', type=int, default=950)
a = ap.parse_args()
img = Image.open(a.image).convert('RGB'); W, H = img.size
paths = json.load(open(a.paths))['trails']
names = {m.group(1): (m.group(2).strip('"\''), m.group(3)) for m in re.finditer(
    r"id: '([^']+)', name: (\"[^\"]+\"|'[^']+'), difficulty: '([^']+)'", open(a.trails).read())}
ids = [i for i in (a.only.split(',') if a.only else sorted(paths)) if i in paths]
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
px = lambda q: (q[0] * W / 100, q[1] * H / 100)
os.makedirs(a.out, exist_ok=True)
cells = []
for tid in ids:
    p = paths[tid]
    pts = [px(q) for s in p['segments'] for q in s] + ([px(p['label'])] if p.get('label') else [])
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    box = (max(0, int(min(xs)) - 130), max(0, int(min(ys)) - 130), min(W, int(max(xs)) + 130), min(H, int(max(ys)) + 130))
    s = min(2.0, a.max / max(box[2] - box[0], box[3] - box[1]))
    crop = img.crop(box).resize((int((box[2] - box[0]) * s), int((box[3] - box[1]) * s)), Image.LANCZOS).convert('RGBA')
    ov = Image.new('RGBA', crop.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    tr = lambda q: ((px(q)[0] - box[0]) * s, (px(q)[1] - box[1]) * s)
    for oid, op in paths.items():
        if oid == tid: continue
        for seg in op['segments']:
            d.line([tr(q) for q in seg], fill=(0, 230, 255, 120), width=2)
    for seg in p['segments']:
        d.line([tr(q) for q in seg], fill=(255, 90, 0, 200), width=5)
        for e in (seg[0], seg[-1]):
            x, y = tr(e); d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 0, 0, 230))
    if p.get('label'):
        x, y = tr(p['label']); d.ellipse((x - 11, y - 11, x + 11, y + 11), outline=(255, 90, 0, 255), width=4)
    cell = Image.alpha_composite(crop, ov).convert('RGB')
    cap = Image.new('RGB', (cell.width, cell.height + 22), 'white'); cap.paste(cell, (0, 22))
    n, dif = names.get(tid, (tid, '?'))
    ImageDraw.Draw(cap).text((4, 2), f"{tid}: {n} ({dif}) x{s:.2f}{' MARKER' if p.get('label') else ''}", fill='black', font=font)
    cells.append((tid, cap))
for k in range(0, len(cells), a.per):
    grp = cells[k:k + a.per]
    w = sum(c.width for _, c in grp) + 10 * (len(grp) - 1); h = max(c.height for _, c in grp)
    sheet = Image.new('RGB', (w, h), (90, 90, 90)); x = 0
    for _, c in grp: sheet.paste(c, (x, 0)); x += c.width + 10
    sheet.save(f"{a.out}/{k // a.per:03d}_{'+'.join(t for t, _ in grp)}.jpg", quality=85)
print(len(cells), 'trails ->', a.out)
