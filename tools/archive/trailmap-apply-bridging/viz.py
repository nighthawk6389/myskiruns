"""viz.py: per changed trail, a crop around where its old and new paths differ: old path red, new green (drawn
thin over each other), on the map; a contact sheet of them."""
import json, os, math
from PIL import Image, ImageDraw, ImageFont
S = os.path.dirname(os.path.abspath(__file__))
R = '/home/user/myskiruns'
Image.MAX_IMAGE_PIXELS = None
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
cells = []
for f in sorted(os.listdir(f'{S}/old')):
    n = f[:-5]
    old = json.load(open(f'{S}/old/{f}'))['trails']; new = json.load(open(f'{S}/new/{f}'))['trails']
    img = Image.open(f'{R}/public/maps/{n}.jpg').convert('RGB')
    W, H = img.size
    px = lambda q: (q[0] * W / 100, q[1] * H / 100)
    for t in sorted(set(old) | set(new)):
        a, b = old.get(t, {}).get('segments', []), new.get(t, {}).get('segments', [])
        if a == b:
            continue
        pa = [px(q) for s in a for q in s]; pb = [px(q) for s in b for q in s]
        # points of a not in b and of b not in a: where they differ
        sa = {(round(x), round(y)) for x, y in pa}; sb = {(round(x), round(y)) for x, y in pb}
        diff = [q for q in sa ^ sb] or list(sa)
        cx = sum(q[0] for q in diff) / len(diff); cy = sum(q[1] for q in diff) / len(diff)
        r = max(60, max(math.dist(q, (cx, cy)) for q in diff) + 40)
        box = (int(max(0, cx - r)), int(max(0, cy - r)), int(min(W, cx + r)), int(min(H, cy + r)))
        z = min(4, 360 / (box[2] - box[0]))
        c = img.crop(box).resize((int((box[2] - box[0]) * z), int((box[3] - box[1]) * z)), Image.LANCZOS)
        d = ImageDraw.Draw(c)
        tr = lambda q: ((q[0] - box[0]) * z, (q[1] - box[1]) * z)
        for segs, col, w in ((a, (255, 0, 0), 5), (b, (0, 200, 0), 2)):
            for s in segs:
                d.line([tr(px(q)) for q in s], fill=col, width=w)
                for e in (s[0], s[-1]):
                    x, y = tr(px(e)); d.ellipse((x - 4, y - 4, x + 4, y + 4), outline=col, width=2)
        cap = Image.new('RGB', (c.width, c.height + 18), 'white'); cap.paste(c, (0, 18))
        ImageDraw.Draw(cap).text((3, 1), f'{n}: {t}', fill='black', font=F)
        cells.append(cap)
cw = max(c.width for c in cells); ch = max(c.height for c in cells)
cols = 3
sheet = Image.new('RGB', (cols * (cw + 8), ((len(cells) + cols - 1) // cols) * (ch + 8)), (90, 90, 90))
for k, c in enumerate(cells):
    sheet.paste(c, ((k % cols) * (cw + 8), (k // cols) * (ch + 8)))
sheet.save(f'{S}/sheet.jpg', quality=88)
print(len(cells), sheet.size)
