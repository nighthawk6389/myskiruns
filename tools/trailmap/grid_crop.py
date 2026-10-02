"""Look closely at one spot of a trail map: a zoomed crop with a labelled pixel grid, to read coordinates off
(traced stretches, cut points, decision points), optionally with the line pieces (numbered, or 'id:name'), the
finished overlays (tagged with trail names) and the difficulty symbols (tagged with their names) drawn on.

    python3 tools/trailmap/grid_crop.py --image map.png --box 1500,600,1800,800 --zoom 3 --out spot.png
    python3 tools/trailmap/grid_crop.py --image map.png --box 0,400,1100,1000 --box 1000,400,2100,1000 \\
        --zoom 1.5 --grid 0 --pieces pieces.json --names names.json --symbols named_syms.json --out work/tiles

--box can repeat (then --out is a directory: one png per box, named after it). --grid N labels a line every N
source px (0: none), with faint lines every --fine px. --pieces: linePolylines.json-style pieces, coloured per
id, ends circled; with --names ({id: name}, '-' for not a trail) each is tagged 'id:name' and undecided ones
'id?'. --paths trailPaths.json with --trails trails.ts: the overlays, tagged with names. --symbols:
[{c: [x, y], name?, t?}] in source px (raster_symbols.py output, or a named list). Plain crop by default.
Judge on crops at >= 1x zoom: judgements on shrunken images were wrong often enough to mislead.

Requires: pip install pillow
"""
import argparse
import colorsys
import json
import os
import re

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def colour(k):  # golden-ratio hues: neighbouring ids get far-apart colours
    return tuple(int(255 * c) for c in colorsys.hsv_to_rgb((k * 0.618) % 1, 1, 0.85))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', required=True)
    ap.add_argument('--box', action='append', required=True, help='x0,y0,x1,y1 in source px (repeatable)')
    ap.add_argument('--zoom', type=float, default=3.0)
    ap.add_argument('--out', required=True, help='png (one box) or directory (several)')
    ap.add_argument('--grid', type=int, default=100, help='labelled grid step in source px; 0 = none')
    ap.add_argument('--fine', type=int, default=25, help='faint grid step in source px; 0 = none')
    ap.add_argument('--pieces', help='linePolylines.json-style pieces (percent coords) to draw')
    ap.add_argument('--names', help='{piece id: name} for --pieces')
    ap.add_argument('--paths', help='trailPaths.json overlays to draw')
    ap.add_argument('--trails', help='trails.ts, for overlay names')
    ap.add_argument('--symbols', help='[{c: [x, y], name?, t?}] symbols to tag')
    a = ap.parse_args()

    img = Image.open(a.image).convert('RGB')
    W, H = img.size
    pieces = json.load(open(a.pieces))['polylines'] if a.pieces else []
    names = json.load(open(a.names)) if a.names else None
    paths = json.load(open(a.paths))['trails'] if a.paths else {}
    tnames = {m.group(1): m.group(2).strip('"\'') for m in re.finditer(
        r"id: '([^']+)', name: (\"[^\"]+\"|'[^']+')", open(a.trails).read())} if a.trails else {}
    syms = json.load(open(a.symbols)) if a.symbols else []
    f, fs = ImageFont.truetype(BOLD, 13), ImageFont.truetype(BOLD, 11)
    many = len(a.box) > 1
    if many:
        os.makedirs(a.out, exist_ok=True)
    for b in a.box:
        x0, y0, x1, y1 = map(int, b.split(','))
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        z = a.zoom
        im = img.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * z), int((y1 - y0) * z)), Image.LANCZOS).convert('RGBA')
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for step, alpha, label in ((a.fine, 45, False), (a.grid, 110, True)):
            if not step:
                continue
            for gx in range((x0 // step + 1) * step, x1, step):
                X = (gx - x0) * z
                d.line((X, 0, X, im.height), fill=(255, 0, 255, alpha))
                if label:
                    d.text((X + 2, 2), str(gx), fill=(200, 0, 200, 255), font=fs, stroke_width=2, stroke_fill='white')
            for gy in range((y0 // step + 1) * step, y1, step):
                Y = (gy - y0) * z
                d.line((0, Y, im.width, Y), fill=(255, 0, 255, alpha))
                if label:
                    d.text((2, Y + 2), str(gy), fill=(200, 0, 200, 255), font=fs, stroke_width=2, stroke_fill='white')

        def to_crop(q):  # percent of the image -> crop px
            return ((q[0] * W / 100 - x0) * z, (q[1] * H / 100 - y0) * z)

        def inside(pts):
            return [q for q in pts if 0 <= q[0] < im.width and 0 <= q[1] < im.height]

        tags = []
        for p in pieces:
            pts = [to_crop(q) for q in p['points']]
            if not inside(pts):
                continue
            c = colour(p['id'])
            d.line(pts, fill=c + (255,), width=3)
            for e in (pts[0], pts[-1]):
                d.ellipse((e[0] - 3, e[1] - 3, e[0] + 3, e[1] + 3), outline=c + (255,), width=2)
            nm = names.get(str(p['id'])) if names is not None else None
            t = str(p['id']) if names is None else (f"{p['id']}:{nm[:16]}" if nm else f"{p['id']}?")
            tags.append((inside(pts)[len(inside(pts)) // 2], t, c))
        for k, (tid, p) in enumerate(sorted(paths.items())):
            c = colour(k)
            for seg in p.get('segments', []):
                pts = [to_crop(q) for q in seg]
                d.line(pts, fill=c + (230,), width=4)
                if inside(pts):
                    tags.append((inside(pts)[len(inside(pts)) // 2], tnames.get(tid, tid), c))
            if p.get('label'):
                x, y = to_crop(p['label'])
                d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=c + (255,), width=4)
                tags.append(((x, y), tnames.get(tid, tid), c))
        for s in syms:
            X, Y = (s['c'][0] - x0) * z, (s['c'][1] - y0) * z
            if 0 <= X < im.width and 0 <= Y < im.height:
                t = ' '.join(str(v) for v in (f"#{s['i']}" if 'i' in s else None, s.get('name'), s.get('t')) if v)
                d.text((X + 8, Y + 6), t, fill=(220, 0, 0, 255), font=fs, stroke_width=2, stroke_fill='white')
        for (x, y), t, c in tags:  # last, so no line crosses a tag
            w = d.textlength(t, font=f)
            d.rectangle((x + 3, y - 8, x + w + 7, y + 8), fill=(255, 255, 160, 230))
            d.text((x + 5, y - 8), t, fill=c + (255,) if sum(c) < 500 else (0, 0, 0, 255), font=f)
        out = os.path.join(a.out, f'crop_{x0}_{y0}.png') if many else a.out
        Image.alpha_composite(im, ov).convert('RGB').save(out)
        print(out, im.size)


if __name__ == '__main__':
    main()
