"""Contact sheets: each piece alone (magenta) on its own crop, other pieces thin grey, symbols tagged with names."""
import json, sys, math
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
img_path, pieces_path, names_path, syms_path, out, *ids = sys.argv[1:]
im = Image.open(img_path).convert('RGB'); W, H = im.size
P = {p['id']: p for p in json.load(open(pieces_path))['polylines']}
N = json.load(open(names_path))
S = json.load(open(syms_path))
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
ids = [int(i) for i in ids] if ids else sorted(P)
tiles = []
for pid in ids:
    p = P[pid]
    pts = [(x * W / 100, y * H / 100) for x, y in p['points']]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    pad = 120
    x0, y0, x1, y1 = max(0, min(xs) - pad), max(0, min(ys) - pad), min(W, max(xs) + pad), min(H, max(ys) + pad)
    side = max(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x0, y0, x1, y1 = cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2
    crop = im.crop((int(x0), int(y0), int(x1), int(y1)))
    z = 520 / side
    crop = crop.resize((520, 520))
    d = ImageDraw.Draw(crop)
    tr = lambda q: ((q[0] - x0) * z, (q[1] - y0) * z)
    for o in P.values():
        if o['id'] == pid: continue
        op = [tr((x * W / 100, y * H / 100)) for x, y in o['points']]
        d.line(op, fill=(160, 160, 160), width=1)
    d.line([tr(q) for q in pts], fill=(255, 0, 255), width=4)
    d.ellipse([*[v - 6 for v in tr(pts[0])], *[v + 6 for v in tr(pts[0])]], outline=(255, 0, 255), width=3)
    for s in S:
        q = tr(s['c'])
        if 0 <= q[0] < 520 and 0 <= q[1] < 520:
            d.text((q[0] + 8, q[1] - 8), (s.get('name') or '?')[:18], fill=(255, 0, 0), font=font, stroke_width=2, stroke_fill='white')
    d.rectangle([0, 0, 519, 24], fill='white')
    d.text((4, 3), f"{pid} {p['cls']} {N.get(str(pid), '?')[:30]}", fill='black', font=font)
    tiles.append(crop)
cols = 3
for k in range(0, len(tiles), 6):
    group = tiles[k:k + 6]
    rows = (len(group) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 525, rows * 525), 'white')
    for i, t in enumerate(group):
        sheet.paste(t, ((i % cols) * 525, (i // cols) * 525))
    sheet.save(f'{out}_{k // 6}.png')
    print(f'{out}_{k // 6}.png', [ids[j] for j in range(k, min(k + 6, len(ids)))])
