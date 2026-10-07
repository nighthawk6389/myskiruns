"""ovl.py PANEL TRAIL_ID x0,y0,x1,y1 ZOOM OUT: one trail's overlay (trailPaths.json) in orange over the map (map px box,
zoom vs map px), other overlays thin cyan."""
import json, sys
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
P, tid, b, z, out = sys.argv[1], sys.argv[2], list(map(float, sys.argv[3].split(','))), float(sys.argv[4]), sys.argv[5]
img = Image.open(f'/home/user/myskiruns/work/palisades-tahoe/{P}/map.png').convert('RGB')
W, H = img.size
paths = json.load(open(f'/home/user/myskiruns/src/data/resorts/palisades-tahoe/panels/{P}/trailPaths.json'))['trails']
crop = img.crop(tuple(int(v) for v in b)).resize((int((b[2] - b[0]) * z), int((b[3] - b[1]) * z)), Image.LANCZOS).convert('RGBA')
ov = Image.new('RGBA', crop.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
tr = lambda q: ((q[0] * W / 100 - b[0]) * z, (q[1] * H / 100 - b[1]) * z)  # noqa: E731
for oid, p in paths.items():
    for seg in p.get('segments', []):
        if oid == tid:
            d.line([tr(q) for q in seg], fill=(255, 90, 0, 210), width=4)
            for e in (seg[0], seg[-1]):
                x, y = tr(e); d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 0, 0, 230))
        else:
            d.line([tr(q) for q in seg], fill=(0, 230, 255, 140), width=2)
Image.alpha_composite(crop, ov).convert('RGB').save(out)
print(out, crop.size)
