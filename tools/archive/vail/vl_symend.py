"""vl_symend.py: named symbols where their trail's overlay ENDS (rather than passing through): either the run starts
at its symbol, or the line resumes past the printed name and that stretch is missing. Sheets endsheet_<k>.png show
each with the overlay (magenta) for checking."""
import json, math, re
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
exec(open('vl_symnames.py').read())
exec(open('vl_pt.py').read())
R = '/home/user/myskiruns/src/data/resorts/vail'
slug = lambda n: re.sub(r'[^a-z0-9]+', '-', n.lower().replace("'", '')).strip('-')  # noqa: E731
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
cells, rows = [], []
for panel in ('front-side', 'back-bowls', 'blue-sky'):
    W, H = SIZE[panel]
    paths = json.load(open(f'{R}/panels/{panel}/trailPaths.json'))['trails']
    src = Image.open(f'{panel}.png').convert('RGB')
    for s in json.load(open(f'syms_{panel}.json')):
        n = NAMES[panel].get(s['i'])
        if not n or n == '?':
            continue
        p = paths.get(slug(n))
        if not p or p.get('label'):
            continue
        segs = [[(x * W / 100, y * H / 100) for x, y in g] for g in p['segments']]
        c, r = s['c'], s['r']
        through = False
        for g in segs:
            cum = [0]
            for a, b in zip(g, g[1:]):
                cum.append(cum[-1] + math.dist(a, b))
            best = None
            for i in range(len(g) - 1):
                d = seg_dist(c, g[i], g[i + 1])
                if best is None or d < best[0]:
                    (ax, ay), (bx, by) = g[i], g[i + 1]
                    L = math.dist(g[i], g[i + 1]) or 1e-9
                    t = max(0, min(1, ((c[0] - ax) * (bx - ax) + (c[1] - ay) * (by - ay)) / (L * L)))
                    best = (d, cum[i] + t * L)
            if best and best[0] < 1.6 * r + 4 and best[1] > 3 * r and cum[-1] - best[1] > 3 * r:
                through = True
        if through:
            continue
        rows.append((panel, s['i'], n))
        half = max(11 * r, 85)
        x0, y0 = int(c[0] - half), int(c[1] - half)
        z = 300 / (2 * half)
        im = src.crop((x0, y0, int(x0 + 2 * half), int(y0 + 2 * half))).resize((300, 300), Image.LANCZOS)
        d = ImageDraw.Draw(im, 'RGBA')
        for g in segs:
            d.line([((x - x0) * z, (y - y0) * z) for x, y in g], fill=(255, 0, 200, 170), width=2)
        d.text((3, 3), f'{panel[:2]}#{s["i"]} {n}', fill='black', font=f, stroke_width=2, stroke_fill='white')
        cells.append(im)
cols = 5
for k in range(0, len(cells), 15):
    part = cells[k:k + 15]
    sheet = Image.new('RGB', (cols * 304, ((len(part) + cols - 1) // cols) * 304), 'white')
    for j, im in enumerate(part):
        sheet.paste(im, ((j % cols) * 304, (j // cols) * 304))
    sheet.save(f'endsheet_{k // 15}.png')
for r_ in rows:
    print(*r_)
print(len(rows), 'symbols at an overlay end')
