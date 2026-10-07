"""vl_gapsheet.py out.png: for each symbol vl_symgap.py lists, a crop around the symbol and its trail's nearest
overlay end, the overlay drawn in magenta and a 25 px grid, to read off the stretch to trace."""
import json, math, re, subprocess
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
exec(open('vl_symnames.py').read())
exec(open('vl_pt.py').read())
R = '/home/user/myskiruns/src/data/resorts/vail'
slug = lambda n: re.sub(r'[^a-z0-9]+', '-', n.lower().replace("'", '')).strip('-')  # noqa: E731
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
rows = [l.split() for l in subprocess.run(['python3', 'vl_symgap.py'], capture_output=True, text=True).stdout.splitlines()[:-1]]
cells = []
imgs = {}
for r in rows:
    panel, i = r[0], int(r[1])
    W, H = SIZE[panel]
    s = next(x for x in json.load(open(f'syms_{panel}.json')) if x['i'] == i)
    n = NAMES[panel][i]
    p = json.load(open(f'{R}/panels/{panel}/trailPaths.json'))['trails'].get(slug(n))
    segs = [[(x * W / 100, y * H / 100) for x, y in g] for g in (p or {}).get('segments', [])]
    ends = [g[k] for g in segs for k in (0, -1)]
    e = min(ends, key=lambda q: math.dist(q, s['c'])) if ends else s['c']
    cx, cy = (s['c'][0] + e[0]) / 2, (s['c'][1] + e[1]) / 2
    half = max(70, abs(s['c'][0] - e[0]) / 2 + 50, abs(s['c'][1] - e[1]) / 2 + 50)
    x0, y0 = int(cx - half), int(cy - half)
    if panel not in imgs:
        imgs[panel] = Image.open(f'{panel}.png').convert('RGB')
    z = 360 / (2 * half)
    im = imgs[panel].crop((x0, y0, int(x0 + 2 * half), int(y0 + 2 * half))).resize((360, 360), Image.LANCZOS)
    d = ImageDraw.Draw(im, 'RGBA')
    for g in range((x0 // 25 + 1) * 25, int(x0 + 2 * half), 25):
        d.line(((g - x0) * z, 0, (g - x0) * z, 360), fill=(255, 0, 255, 50 if g % 100 else 120))
    for g in range((y0 // 25 + 1) * 25, int(y0 + 2 * half), 25):
        d.line((0, (g - y0) * z, 360, (g - y0) * z), fill=(255, 0, 255, 50 if g % 100 else 120))
    for g in segs:
        d.line([((x - x0) * z, (y - y0) * z) for x, y in g], fill=(255, 0, 200, 200), width=2)
    d.text((4, 4), f'{panel[:2]}#{i} {n}', fill='black', font=f, stroke_width=2, stroke_fill='white')
    d.text((4, 344), f'x0={x0} y0={y0} 100s:{(x0 // 100 + 1) * 100},{(y0 // 100 + 1) * 100}', fill='black', font=f,
           stroke_width=2, stroke_fill='white')
    cells.append(im)
cols = 4
sheet = Image.new('RGB', (cols * 365, ((len(cells) + cols - 1) // cols) * 365), 'white')
for k, c in enumerate(cells):
    sheet.paste(c, ((k % cols) * 365, (k // cols) * 365))
for k in range(0, len(cells), 8):
    part = sheet.crop((0, (k // cols) * 365, cols * 365, min(sheet.height, (k // cols + 2) * 365)))
    part.save(f'gap_{k // 8}.png')
print(len(cells), 'cells')
