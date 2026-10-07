"""vl_gapfix.py: for each symbol off its trail's overlay (vl_symgap.py), propose the stretch along the printed name
from the symbol to the overlay's nearest end; draw the proposals (cyan) over the overlay (magenta) on sheets
gapfix_<k>.png, and print them as TRACED entries."""
import json, math, re, subprocess
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
exec(open('vl_symnames.py').read())
exec(open('vl_pt.py').read())
R = '/home/user/myskiruns/src/data/resorts/vail'
slug = lambda n: re.sub(r'[^a-z0-9]+', '-', n.lower().replace("'", '')).strip('-')  # noqa: E731
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
rows = [l.split() for l in subprocess.run(['python3', 'vl_symgap.py'], capture_output=True, text=True).stdout.splitlines()[:-1]]
cells, imgs = [], {}
for r in rows:
    panel, i = r[0], int(r[1])
    W, H = SIZE[panel]
    s = next(x for x in json.load(open(f'syms_{panel}.json')) if x['i'] == i)
    n = NAMES[panel][i]
    p = json.load(open(f'{R}/panels/{panel}/trailPaths.json'))['trails'].get(slug(n))
    segs = [[(x * W / 100, y * H / 100) for x, y in g] for g in (p or {}).get('segments', [])]
    ends = [g[k] for g in segs for k in (0, -1)]
    e = min(ends, key=lambda q: math.dist(q, s['c']))
    c = (round(s['c'][0]), round(s['c'][1])); e = (round(e[0]), round(e[1]))
    print(f"    ({n!r}, [{c}, {e}]),  # {panel} #{i}")
    cx, cy = (c[0] + e[0]) / 2, (c[1] + e[1]) / 2
    half = max(70, abs(c[0] - e[0]) / 2 + 50, abs(c[1] - e[1]) / 2 + 50)
    x0, y0 = int(cx - half), int(cy - half)
    if panel not in imgs:
        imgs[panel] = Image.open(f'{panel}.png').convert('RGB')
    z = 360 / (2 * half)
    im = imgs[panel].crop((x0, y0, int(x0 + 2 * half), int(y0 + 2 * half))).resize((360, 360), Image.LANCZOS)
    d = ImageDraw.Draw(im, 'RGBA')
    for g in segs:
        d.line([((x - x0) * z, (y - y0) * z) for x, y in g], fill=(255, 0, 200, 220), width=3)
    d.line([((c[0] - x0) * z, (c[1] - y0) * z), ((e[0] - x0) * z, (e[1] - y0) * z)], fill=(0, 200, 255, 230), width=3)
    d.text((4, 4), f'{panel[:2]}#{i} {n}', fill='black', font=f, stroke_width=2, stroke_fill='white')
    cells.append(im)
cols = 4
for k in range(0, len(cells), 8):
    part = cells[k:k + 8]
    sheet = Image.new('RGB', (cols * 365, ((len(part) + cols - 1) // cols) * 365), 'white')
    for j, cimg in enumerate(part):
        sheet.paste(cimg, ((j % cols) * 365, (j // cols) * 365))
    sheet.save(f'gapfix_{k // 8}.png')
