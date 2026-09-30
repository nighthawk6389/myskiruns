"""Region audit sheets: every overlay drawn in its own colour and tagged with
its trail name, over zoomed regions of the map, to compare with the printed
labels in one look (how Sugarbush was checked without the review page).

    python3 tools/trailmap/region_audit.py --image map.png \\
        --paths src/data/resorts/sugarbush/trailPaths.json \\
        --trails src/data/resorts/sugarbush/trails.ts --out work/regions \\
        --grid 4x2 --area 200,840,4140,2440      # or --box x0,y0,x1,y1 --zoom 2

Markers (label-only trails) are circles with the name beside them. Judge at
>= 1x zoom; zoom into crowded spots with --box.

Requires: pip install pillow
"""
import argparse
import colorsys
import json
import os
import re

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', required=True, help='lossless source raster')
    ap.add_argument('--paths', required=True, help='trailPaths.json (segments/label in percent)')
    ap.add_argument('--trails', required=True, help='trails.ts, for the names')
    ap.add_argument('--out', required=True)
    ap.add_argument('--grid', default='4x3', help='regions across x down, over --area')
    ap.add_argument('--area', help='x0,y0,x1,y1 in source px to grid over (default: the whole image)')
    ap.add_argument('--box', action='append', default=[], help='x0,y0,x1,y1: one region (instead of --grid)')
    ap.add_argument('--zoom', type=float, default=1.0)
    ap.add_argument('--font', default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    a = ap.parse_args()

    img = Image.open(a.image).convert('RGB')
    W, H = img.size
    paths = json.load(open(a.paths))['trails']
    names = {m.group(1): m.group(2).strip('"\'') for m in re.finditer(
        r"id: '([^']+)', name: (\"[^\"]+\"|'[^']+')", open(a.trails).read())}
    font = ImageFont.truetype(a.font, 15)
    ids = sorted(paths)
    # golden-ratio hues: neighbours in id order get far-apart colours
    colour = {t: tuple(int(255 * c) for c in colorsys.hsv_to_rgb((i * 0.618) % 1, 0.95, 0.85))
              for i, t in enumerate(ids)}

    boxes = [tuple(map(int, b.split(','))) for b in a.box]
    if not boxes:
        gx, gy = map(int, a.grid.split('x'))
        X0, Y0, X1, Y1 = map(int, a.area.split(',')) if a.area else (0, 0, W, H)
        bw, bh = (X1 - X0) // gx, (Y1 - Y0) // gy
        boxes = [(X0 + i * bw - 60, Y0 + j * bh - 60, X0 + (i + 1) * bw + 60, Y0 + (j + 1) * bh + 60)
                 for j in range(gy) for i in range(gx)]

    os.makedirs(a.out, exist_ok=True)
    for k, box in enumerate(boxes):
        box = (max(0, box[0]), max(0, box[1]), min(W, box[2]), min(H, box[3]))
        z = a.zoom
        im = img.crop(box).resize((int((box[2] - box[0]) * z), int((box[3] - box[1]) * z)), Image.LANCZOS)
        im = im.convert('RGBA')
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)

        def to_crop(q):  # percent of the image -> crop px
            return ((q[0] * W / 100 - box[0]) * z, (q[1] * H / 100 - box[1]) * z)

        tags = []
        for t in ids:
            p, c = paths[t], colour[t]
            segs = [[to_crop(q) for q in s] for s in p['segments']]
            for s in segs:
                d.line(s, fill=c + (230,), width=4)
                inside = [q for q in s if 0 <= q[0] < im.width and 0 <= q[1] < im.height]
                if inside:
                    q = inside[len(inside) // 2]
                    tags.append((q[0] + 6, q[1] - 8, t, c))
            if p.get('label'):
                x, y = to_crop(p['label'])
                d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=c + (255,), width=4)
                tags.append((x + 10, y - 8, t, c))
        for x, y, t, c in tags:  # names last, so no line crosses a tag
            s = names.get(t, t)
            w = d.textlength(s, font=font)
            d.rectangle((x - 2, y - 1, x + w + 2, y + 17), fill=(255, 255, 255, 215))
            d.text((x, y), s, fill=c + (255,), font=font)
        Image.alpha_composite(im, ov).convert('RGB').save(f'{a.out}/r{k:02d}_{box[0]}_{box[1]}.jpg', quality=85)
    print(f'{len(boxes)} regions -> {a.out}')


if __name__ == '__main__':
    main()
