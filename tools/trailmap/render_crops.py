"""Render zoomed crops of trail overlays on the source map for visual checks.

    python3 tools/trailmap/render_crops.py --image map.png \\
        --paths src/data/resorts/killington/trailPaths.json --out work/crops breakaway great-northern
    python3 tools/trailmap/render_crops.py --image map.png \\
        --paths src/data/resorts/killington/trailPaths.json --out work/crops --pair upper-skyelark skyelark

Each trail is drawn in orange (a second trail with --pair in cyan) over a
crop of its bounding box. Use it to audit a random sample (is the orange line
the trail whose name is printed along it, and does it cover the whole run?),
and to check every split/merge before shipping. Judge on crops at >= 1x
zoom: distances judged on shrunken images were wrong often enough to mislead.

Requires: pip install pillow
"""
import argparse
import json
import os

from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None
COLORS = [(255, 90, 31, 210), (0, 220, 255, 210)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', required=True)
    ap.add_argument('--paths', required=True, help='trailPaths.json (segments/label in percent)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--pair', action='store_true', help='draw the given trails together in one crop')
    ap.add_argument('--max', type=int, default=1100, help='max crop edge in output px')
    ap.add_argument('trails', nargs='+')
    a = ap.parse_args()

    img = Image.open(a.image).convert('RGB')
    W, H = img.size
    paths = json.load(open(a.paths))['trails']
    os.makedirs(a.out, exist_ok=True)
    groups = [a.trails] if a.pair else [[t] for t in a.trails]
    for group in groups:
        pts = []
        for t in group:
            p = paths[t]
            pts += [q for s in p['segments'] for q in s] + ([p['label']] if p.get('label') else [])
        xs = [q[0] * W / 100 for q in pts]
        ys = [q[1] * H / 100 for q in pts]
        box = (max(0, int(min(xs)) - 150), max(0, int(min(ys)) - 150), min(W, int(max(xs)) + 150), min(H, int(max(ys)) + 150))
        s = min(2.0, a.max / max(box[2] - box[0], box[3] - box[1]))
        crop = img.crop(box).resize((int((box[2] - box[0]) * s), int((box[3] - box[1]) * s))).convert('RGBA')
        ov = Image.new('RGBA', crop.size)
        d = ImageDraw.Draw(ov)
        for t, col in zip(group, COLORS * 10):
            p = paths[t]
            for seg in p['segments']:
                d.line([((q[0] * W / 100 - box[0]) * s, (q[1] * H / 100 - box[1]) * s) for q in seg], fill=col, width=5)
            if p.get('label'):
                x, y = (p['label'][0] * W / 100 - box[0]) * s, (p['label'][1] * H / 100 - box[1]) * s
                d.ellipse((x - 12, y - 12, x + 12, y + 12), outline=col, width=4)
        out = f"{a.out}/{'__'.join(group)}.jpg"
        Image.alpha_composite(crop, ov).convert('RGB').save(out, quality=85)
        print(out)


if __name__ == '__main__':
    main()
