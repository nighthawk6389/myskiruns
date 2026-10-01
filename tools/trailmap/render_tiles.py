"""Cut the trail map into overlapping, zoomed tiles with every detected line
piece drawn in magenta and labelled with its numeric id. These tiles are what
the naming readers (Claude sub-agents) look at.

    python3 tools/trailmap/render_tiles.py \\
        --image map.png --polylines src/data/resorts/killington/linePolylines.json --out work/tiles

Writes <out>/<tile>.jpg and <out>/index.json ([{tile, box:[x0,y0,x1,y1], ids}]).
Tile pixel (px,py) maps to source pixel (x0 + px/zoom, y0 + py/zoom).

Defaults (760x540 source px, 140 px overlap, 1.7x) gave 37 tiles for a
4572x2704 map and text readable by the readers; zoom so the map's smallest
labels are >= ~14 px tall in the tile.

Requires: pip install pillow
"""
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', required=True, help='lossless source raster')
    ap.add_argument('--polylines', required=True, help='linePolylines.json (points in percent)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--tile', default='760x540', help='tile size in source px, WxH')
    ap.add_argument('--overlap', type=int, default=140)
    ap.add_argument('--zoom', type=float, default=1.7)
    ap.add_argument('--font', default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    a = ap.parse_args()

    img = Image.open(a.image).convert('RGB')
    W, H = img.size
    tw, th = map(int, a.tile.split('x'))
    S = a.zoom
    polys = json.load(open(a.polylines))['polylines']
    for p in polys:
        p['px'] = [(x * W / 100, y * H / 100) for x, y in p['points']]
    # a map with no drawn lines (Jay Peak) has no pieces: tile the whole image
    xs = [q[0] for p in polys for q in p['px']] or [50, W - 50]
    ys = [q[1] for p in polys for q in p['px']] or [50, H - 50]
    X0, X1, Y0, Y1 = int(min(xs)) - 50, int(max(xs)) + 50, int(min(ys)) - 50, int(max(ys)) + 50
    try:
        font = ImageFont.truetype(a.font, 17)
    except OSError:
        font = ImageFont.load_default()

    os.makedirs(a.out, exist_ok=True)
    tiles = []
    for r, ty in enumerate(range(Y0, Y1, th - a.overlap)):
        for c, tx in enumerate(range(X0, X1, tw - a.overlap)):
            box = (max(0, tx), max(0, ty), min(W, tx + tw), min(H, ty + th))
            inside = [p for p in polys if any(box[0] <= x < box[2] and box[1] <= y < box[3] for x, y in p['px'])]
            if polys and not inside:
                continue
            name = f't{r}{c:02d}'
            crop = img.crop(box).resize((int((box[2] - box[0]) * S), int((box[3] - box[1]) * S)), Image.LANCZOS)
            crop = crop.convert('RGBA')
            ov = Image.new('RGBA', crop.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            tags = []
            for p in inside:
                q = [((x - box[0]) * S, (y - box[1]) * S) for x, y in p['px']]
                d.line(q, fill=(255, 0, 255, 170), width=2)
                for e in (q[0], q[-1]):
                    d.ellipse((e[0] - 3, e[1] - 3, e[0] + 3, e[1] + 3), fill=(255, 0, 255, 220))
                ins = [pt for pt in q if 0 <= pt[0] < crop.width and 0 <= pt[1] < crop.height]
                tags.append((p['id'], ins[len(ins) // 2]))
            for pid, (mx, my) in tags:
                t = str(pid)
                tw_ = d.textlength(t, font=font)
                bx = min(max(mx - tw_ / 2 - 3, 0), crop.width - tw_ - 6)
                by = min(max(my - 24, 0), crop.height - 22)
                d.rectangle((bx, by, bx + tw_ + 6, by + 21), fill=(255, 255, 0, 235), outline=(0, 0, 0, 255))
                d.text((bx + 3, by + 1), t, fill=(0, 0, 0, 255), font=font)
                d.line((bx + tw_ / 2 + 3, by + 21, mx, my), fill=(0, 0, 0, 200), width=1)
            Image.alpha_composite(crop, ov).convert('RGB').save(f'{a.out}/{name}.jpg', quality=88)
            tiles.append({'tile': name, 'box': box, 'ids': [p['id'] for p in inside]})
    json.dump({'zoom': S, 'imageSize': [W, H], 'tiles': tiles}, open(f'{a.out}/index.json', 'w'))
    print(f'{len(tiles)} tiles -> {a.out}')


if __name__ == '__main__':
    main()
