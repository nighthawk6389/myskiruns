"""viz2.py: like viz.py, but one crop per cluster of differing points (within 60 px), about 3x."""
import json, os, math
from PIL import Image, ImageDraw, ImageFont
S = os.path.dirname(os.path.abspath(__file__))
R = '/home/user/myskiruns'
Image.MAX_IMAGE_PIXELS = None
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
skip = {('whistler-blackcomb-main', 'dave-murray-downhill-lower'), ('whistler-blackcomb-main', 'harmony-ridge'), ('wildcat', 'tomcat')}
cells = []


def dense(segs, px):
    out = set()
    for s in segs:
        pts = [px(q) for q in s]
        for p, q in zip(pts, pts[1:]):
            n = max(1, int(math.dist(p, q) / 3))
            for k in range(n + 1):
                out.add((round((p[0] + (q[0] - p[0]) * k / n) / 3), round((p[1] + (q[1] - p[1]) * k / n) / 3)))
    return out


for f in sorted(os.listdir(f'{S}/old')):
    n = f[:-5]
    old = json.load(open(f'{S}/old/{f}'))['trails']; new = json.load(open(f'{S}/new/{f}'))['trails']
    img = Image.open(f'{R}/public/maps/{n}.jpg').convert('RGB')
    W, H = img.size
    px = lambda q: (q[0] * W / 100, q[1] * H / 100)
    for t in sorted(set(old) | set(new)):
        a, b = old.get(t, {}).get('segments', []), new.get(t, {}).get('segments', [])
        if a == b or (n, t) in skip:
            continue
        da, db = dense(a, px), dense(b, px)
        # cells covered by one path and not within 2 cells (6 px) of the other
        near = lambda c, D: any((c[0] + i, c[1] + j) in D for i in range(-2, 3) for j in range(-2, 3))
        diff = [(c[0] * 3, c[1] * 3) for c in da if not near(c, db)] + [(c[0] * 3, c[1] * 3) for c in db if not near(c, da)]
        clusters = []
        for q in diff:
            for cl in clusters:
                if math.dist(q, cl[0]) < 60:
                    cl.append(q); break
            else:
                clusters.append([q])
        for cl in clusters:
            cx = sum(q[0] for q in cl) / len(cl); cy = sum(q[1] for q in cl) / len(cl)
            r = max(45, max(math.dist(q, (cx, cy)) for q in cl) + 30)
            box = (int(max(0, cx - r)), int(max(0, cy - r)), int(min(W, cx + r)), int(min(H, cy + r)))
            z = min(5, 330 / (box[2] - box[0]))
            c = img.crop(box).resize((int((box[2] - box[0]) * z), int((box[3] - box[1]) * z)), Image.LANCZOS)
            d = ImageDraw.Draw(c)
            tr = lambda q: ((q[0] - box[0]) * z, (q[1] - box[1]) * z)
            for segs, col, w in ((a, (255, 0, 0), 6), (b, (0, 220, 0), 2)):
                for s in segs:
                    d.line([tr(px(q)) for q in s], fill=col, width=w)
            cap = Image.new('RGB', (c.width, c.height + 18), 'white'); cap.paste(c, (0, 18))
            ImageDraw.Draw(cap).text((3, 1), f'{n}: {t} @{round(cx)},{round(cy)} ({len(cl)})', fill='black', font=F)
            cells.append(cap)
cw = max(c.width for c in cells); ch = max(c.height for c in cells)
cols = 3
sheet = Image.new('RGB', (cols * (cw + 8), ((len(cells) + cols - 1) // cols) * (ch + 8)), (90, 90, 90))
for k, c in enumerate(cells):
    sheet.paste(c, ((k % cols) * (cw + 8), (k // cols) * (ch + 8)))
sheet.save(f'{S}/sheet2.jpg', quality=88)
print(len(cells), sheet.size)
