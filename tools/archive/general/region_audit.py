"""Region audit: every overlay drawn in its own colour with its trail name tagged on it, over zoomed
regions of the map, to compare with the printed labels. python3 region_audit.py --image src.png
--paths trailPaths.json --trails trails.ts --out dir --grid 4x3 [--zoom 1.0] [--box x0,y0,x1,y1]"""
import argparse, colorsys, json, math, os, re
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
ap = argparse.ArgumentParser()
for k in ('--image', '--paths', '--trails', '--out'): ap.add_argument(k)
ap.add_argument('--grid', default='4x3'); ap.add_argument('--zoom', type=float, default=1.0)
ap.add_argument('--box', action='append', default=[]); ap.add_argument('--area', help='x0,y0,x1,y1 to grid over')
a = ap.parse_args()
img = Image.open(a.image).convert('RGB'); W, H = img.size
paths = json.load(open(a.paths))['trails']
names = {m.group(1): m.group(2).strip('"\'') for m in re.finditer(r"id: '([^']+)', name: (\"[^\"]+\"|'[^']+')", open(a.trails).read())}
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
ids = sorted(paths)
col = {t: tuple(int(255 * c) for c in colorsys.hsv_to_rgb((i * 0.618) % 1, 0.95, 0.85)) for i, t in enumerate(ids)}
px = lambda q: (q[0] * W / 100, q[1] * H / 100)
boxes = [tuple(map(int, b.split(','))) for b in a.box]
if not boxes:
    gx, gy = map(int, a.grid.split('x'))
    X0, Y0, X1, Y1 = map(int, a.area.split(',')) if a.area else (0, 0, W, H)
    bw, bh = (X1 - X0) // gx, (Y1 - Y0) // gy
    boxes = [(X0 + i * bw - 60, Y0 + j * bh - 60, X0 + (i + 1) * bw + 60, Y0 + (j + 1) * bh + 60) for j in range(gy) for i in range(gx)]
os.makedirs(a.out, exist_ok=True)
for k, box in enumerate(boxes):
    box = (max(0, box[0]), max(0, box[1]), min(W, box[2]), min(H, box[3]))
    z = a.zoom
    im = img.crop(box).resize((int((box[2] - box[0]) * z), int((box[3] - box[1]) * z)), Image.LANCZOS).convert('RGBA')
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    tr = lambda p: ((p[0] - box[0]) * z, (p[1] - box[1]) * z)
    tags = []
    for t in ids:
        p = paths[t]; c = col[t]
        segs = [[tr(px(q)) for q in s] for s in p['segments']]
        for s in segs:
            d.line(s, fill=c + (230,), width=4)
        if p.get('label'):
            x, y = tr(px(p['label'])); d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=c + (255,), width=4)
            tags.append((x + 10, y - 8, t, c))
        for s in segs:
            inside = [q for q in s if 0 <= q[0] < im.width and 0 <= q[1] < im.height]
            if len(inside) >= 1:
                q = inside[len(inside) // 2]
                tags.append((q[0] + 6, q[1] - 8, t, c))
    for x, y, t, c in tags:
        s = names.get(t, t); w = d.textlength(s, font=font)
        d.rectangle((x - 2, y - 1, x + w + 2, y + 17), fill=(255, 255, 255, 215))
        d.text((x, y), s, fill=c + (255,), font=font)
    Image.alpha_composite(im, ov).convert('RGB').save(f'{a.out}/r{k:02d}_{box[0]}_{box[1]}.jpg', quality=85)
print(len(boxes), 'regions ->', a.out)
