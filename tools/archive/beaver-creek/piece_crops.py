"""zoomed crops of pieces: each piece magenta thick, others by name colour, labels; 2 per row"""
import json, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
import os
OTHERS = os.environ.get("OTHERS")
W = sys.argv[1]; out = sys.argv[2]; ids = [int(x) for x in sys.argv[3:]]
im = Image.open(f'{W}/map.png').convert('RGB')
P = {p['id']: p for p in json.load(open(f'{W}/pieces_cut.json'))['polylines']}
N = json.load(open(f'{W}/names.json'))
S = json.load(open(f'{W}/named_syms.json'))
iw, ih = im.size
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
tiles = []
for pid in ids:
    pts = [(x * iw / 100, y * ih / 100) for x, y in P[pid]['points']]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    half = max(max(xs) - min(xs), max(ys) - min(ys)) / 2 + 90
    half = max(half, 150)
    box = (int(cx - half), int(cy - half), int(cx + half), int(cy + half))
    t = im.crop(box); d = ImageDraw.Draw(t)
    for q in (P.values() if OTHERS else ()):
        if q['id'] == pid: continue
        qp = [(x * iw / 100 - box[0], y * ih / 100 - box[1]) for x, y in q['points']]
        if any(0 <= x <= box[2]-box[0] and 0 <= y <= box[3]-box[1] for x, y in qp):
            d.line(qp, fill=(255, 210, 0), width=1)
            mid = qp[len(qp)//2]
            d.text(mid, f"{q['id']}:{N.get(str(q['id']),'')}", fill=(200, 0, 0), font=f, stroke_width=2, stroke_fill='white')
    pp = [(x - box[0], y - box[1]) for x, y in pts]
    d.line(pp, fill=(255, 0, 255), width=2)
    d.ellipse((pp[0][0]-5, pp[0][1]-5, pp[0][0]+5, pp[0][1]+5), outline=(255, 0, 255), width=2)
    for s in S:
        x, y = s['c'][0] - box[0], s['c'][1] - box[1]
        if 0 <= x <= box[2]-box[0] and 0 <= y <= box[3]-box[1]:
            d.text((x + 6, y - 6), s['name'], fill=(0, 0, 160), font=f, stroke_width=2, stroke_fill='white')
    scale = 560 / t.width
    t = t.resize((560, int(t.height * scale)))
    ImageDraw.Draw(t).text((4, 4), f'{pid} {P[pid]["cls"]} {N.get(str(pid))} box {box[:2]} x{scale:.2f}', fill='red', font=f, stroke_width=2, stroke_fill='white')
    tiles.append(t)
cols = 2
rows = (len(tiles) + 1) // 2
H = max(t.height for t in tiles)
o = Image.new('RGB', (cols * 565, rows * (H + 5)), 'grey')
for i, t in enumerate(tiles):
    o.paste(t, ((i % cols) * 565, (i // cols) * (H + 5)))
o.save(out)
