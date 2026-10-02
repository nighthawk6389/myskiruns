"""Check every named difficulty symbol against the finished overlays (trailPaths.json). Each symbol should lie on
its own trail's overlay, and one at an overlay END deserves a look: the run may start there, or the stretch past
the printed name, or the stub to its parent line, is missing. This caught 33 such gaps on Vail after the region
audit had passed.

    python3 tools/trailmap/symbol_audit.py --symbols named_syms.json --paths trailPaths.json \\
        --trails trails.ts --image map.png --out work/audit [--mode off|ends|diamonds|all]

--symbols: [{name, t, c: [x, y], r}] in source px (name as printed; t circle|square|diamond|double-diamond|ex;
Vail's reading.py writes one per panel). Modes:
  off       symbols farther than 1.5 r + 4 px from their trail's overlay, or whose trail has none on this map
  ends      symbols on their overlay but within 3 r of one of its ends
  diamonds  every diamond, double diamond and EX with its name: the single-vs-double spot check
Writes <out>/<mode>_<k>.png contact sheets (the symbol's surroundings with its trail's overlay in magenta) and
prints the list. A symbol at an end is fine when the run starts or ends there; decide each on its sheet, then a
grid crop (grid_crop.py) for the coordinates of anything missing.

Requires: pip install pillow
"""
import argparse
import json
import math
import os
import re

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None


def norm(n):
    n = n.upper().replace('’', "'").replace('‘', "'").replace('`', "'")
    return re.sub(r'\s+', ' ', n).strip(' .')


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy)), t


def along(c, seg):
    """(distance from c to the polyline, how far along it the nearest point is, its length)."""
    cum = [0]
    for a, b in zip(seg, seg[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    best = (math.inf, 0)
    for i in range(len(seg) - 1):
        d, t = seg_dist(c, seg[i], seg[i + 1])
        if d < best[0]:
            best = (d, cum[i] + t * (cum[i + 1] - cum[i]))
    return best[0], best[1], cum[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--symbols', required=True)
    ap.add_argument('--paths', required=True)
    ap.add_argument('--trails', required=True)
    ap.add_argument('--image', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--mode', default='all', choices=('off', 'ends', 'diamonds', 'all'))
    a = ap.parse_args()
    img = Image.open(a.image).convert('RGB')
    W, H = img.size
    paths = json.load(open(a.paths))['trails']
    ids = {norm(m.group(2).strip('"\'')): m.group(1) for m in re.finditer(
        r"id: '([^']+)', name: (\"[^\"]+\"|'[^']+')", open(a.trails).read())}
    syms = json.load(open(a.symbols))
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
    os.makedirs(a.out, exist_ok=True)
    modes = ('off', 'ends', 'diamonds') if a.mode == 'all' else (a.mode,)
    for mode in modes:
        rows = []
        for s in syms:
            tid = ids.get(norm(s['name']))
            p = paths.get(tid) if tid else None
            c, r = s['c'], s['r']
            segs = [[(x * W / 100, y * H / 100) for x, y in g] for g in (p or {}).get('segments', [])]
            if mode == 'diamonds':
                if s['t'] in ('diamond', 'double-diamond', 'ex'):
                    rows.append((s, segs, s['t']))
                continue
            if not tid:
                if mode == 'off':
                    rows.append((s, [], 'not in the trail list'))
                continue
            if p and p.get('label'):
                continue  # a marker: no line to be on
            if not segs:
                if mode == 'off':
                    rows.append((s, [], 'no overlay on this map'))
                continue
            near = [along(c, g) for g in segs]
            d = min(n[0] for n in near)
            if mode == 'off' and d > 1.5 * r + 4:
                rows.append((s, segs, f'{round(d)} px off its overlay'))
            # at an end: on the overlay, but inside no segment (a segment may start beside the symbol while
            # another runs through it: two lines joined at a junction)
            on = [(t, L) for d_, t, L in near if d_ <= 1.5 * r + 4]
            if mode == 'ends' and on and not any(3 * r <= t <= L - 3 * r for t, L in on):
                rows.append((s, segs, 'at an overlay end'))
        cells = []
        for s, segs, why in rows:
            c, r = s['c'], s['r']
            print(f"{mode}: {s['name']} ({s['t']}) at {round(c[0])},{round(c[1])}: {why}")
            half = max(11 * r, 85) if mode != 'diamonds' else 2.2 * r if s['t'] == 'diamond' else 1.3 * r
            x0, y0 = int(c[0] - half), int(c[1] - half)
            size = 300 if mode != 'diamonds' else 110
            z = size / (2 * half)
            im = img.crop((x0, y0, int(x0 + 2 * half), int(y0 + 2 * half))).resize((size, size), Image.LANCZOS)
            d = ImageDraw.Draw(im, 'RGBA')
            if mode != 'diamonds':
                for g in segs:
                    d.line([((x - x0) * z, (y - y0) * z) for x, y in g], fill=(255, 0, 200, 170), width=2)
                d.text((3, 3), f"{s['name'][:30]}", fill='black', font=font, stroke_width=2, stroke_fill='white')
            cells.append((im, f"{s['name'][:16]}", s['t']))
        if not cells:
            print(f'{mode}: none')
            continue
        cols, per = (5, 15) if mode != 'diamonds' else (12, 144)
        cw = cells[0][0].width + 4
        chh = cells[0][0].height + (4 if mode != 'diamonds' else 32)
        for k in range(0, len(cells), per):
            part = cells[k:k + per]
            sheet = Image.new('RGB', (cols * cw, ((len(part) + cols - 1) // cols) * chh), 'white')
            sd = ImageDraw.Draw(sheet)
            for j, (im, name, t) in enumerate(part):
                X, Y = (j % cols) * cw, (j // cols) * chh
                sheet.paste(im, (X, Y))
                if mode == 'diamonds':
                    sd.text((X, Y + im.height + 1), t.replace('double-diamond', 'DOUBLE'),
                            fill=(200, 0, 0) if t != 'diamond' else (0, 0, 0), font=font)
                    sd.text((X, Y + im.height + 15), name, fill=(60, 60, 60), font=font)
            sheet.save(os.path.join(a.out, f'{mode}_{k // per}.png'))
        print(f'{mode}: {len(rows)} symbols -> {a.out}/{mode}_*.png')


if __name__ == '__main__':
    main()
