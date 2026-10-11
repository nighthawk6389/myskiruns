"""Sheets of crops, one cell per piece: the piece thick in magenta, the other named pieces thin with their names,
on the map; for settling undecided pieces.

    piece_sheet.py <work panel dir> <out prefix> [ids,...] [--per 6] [--size 520]
"""
import json, math, sys
from PIL import Image, ImageDraw, ImageFont
W = sys.argv[1]; out = sys.argv[2]
args = sys.argv[3:]
per = 6; size = 520
ids = None
i = 0
while i < len(args):
    if args[i] == '--per': per = int(args[i + 1]); i += 2
    elif args[i] == '--size': size = int(args[i + 1]); i += 2
    else: ids = [int(a) for a in args[i].split(',')]; i += 1
P = {p['id']: p for p in json.load(open(W + '/pieces_cut.json'))['polylines']}
N = json.load(open(W + '/names.json'))
im = Image.open(W + '/map.png').convert('RGB')
w, h = im.size
if ids is None:
    ids = sorted(int(k) for k, v in N.items() if v == '?')
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
COL = {'black': (255, 0, 0), 'blue': (0, 90, 255), 'green': (0, 170, 0)}
def px(p): return [(x * w / 100, y * h / 100) for x, y in p['points']]
cells = []
for pid in ids:
    pts = px(P[pid])
    x0, y0 = min(x for x, _ in pts), min(y for _, y in pts)
    x1, y1 = max(x for x, _ in pts), max(y for _, y in pts)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    half = max(x1 - x0, y1 - y0) / 2 + 90
    box = (int(cx - half), int(cy - half), int(cx + half), int(cy + half))
    crop = im.crop(box)
    z = size / crop.width
    crop = crop.resize((size, size), Image.LANCZOS)
    dr = ImageDraw.Draw(crop)
    def tr(q): return ((q[0] - box[0]) * z, (q[1] - box[1]) * z)
    for j, p in P.items():
        if j == pid: continue
        q = px(p)
        if all(not (box[0] <= a <= box[2] and box[1] <= b <= box[3]) for a, b in q): continue
        dr.line([tr(a) for a in q], fill=COL.get(p['cls'], (255, 128, 0)), width=2)
        m = q[len(q) // 2]
        if box[0] <= m[0] <= box[2] and box[1] <= m[1] <= box[3]:
            t = f"{j}:{N.get(str(j), '?')}"
            dr.text(tr(m), t, fill=(0, 0, 0), font=font, stroke_width=2, stroke_fill=(255, 255, 255))
    dr.line([tr(a) for a in pts], fill=(255, 0, 255), width=5)
    dr.ellipse([tr(pts[0])[0] - 5, tr(pts[0])[1] - 5, tr(pts[0])[0] + 5, tr(pts[0])[1] + 5], outline=(255, 0, 255), width=2)
    dr.rectangle([0, 0, size, 18], fill=(255, 255, 255))
    dr.text((3, 2), f"#{pid} {P[pid]['cls']} {round(P[pid]['lengthPx'])}px  mid {round(pts[len(pts)//2][0])},{round(pts[len(pts)//2][1])}", fill=(200, 0, 0), font=font)
    cells.append(crop)
cols = 3
for s in range(0, len(cells), per):
    group = cells[s:s + per]
    rows = math.ceil(len(group) / cols)
    sheet = Image.new('RGB', (cols * size + (cols - 1) * 6, rows * size + (rows - 1) * 6), (90, 90, 90))
    for k, c in enumerate(group):
        sheet.paste(c, ((k % cols) * (size + 6), (k // cols) * (size + 6)))
    sheet.save(f'{out}_{s // per:02d}.jpg', quality=88)
    print(f'{out}_{s // per:02d}.jpg', ids[s:s + per])
