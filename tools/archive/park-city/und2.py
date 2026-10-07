"""und2.py OUT_DIR [cols rows]: tiles of the map (with a margin) holding undecided pieces; in each, every piece
drawn thin in its colour with id:name labels for named ones near undecided ones, undecided ones thick red with ids."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
W = '/home/user/myskiruns/work/park-city'
out = sys.argv[1]; cols = int(sys.argv[2]) if len(sys.argv) > 2 else 8; rows = int(sys.argv[3]) if len(sys.argv) > 3 else 5
os.makedirs(out, exist_ok=True)
base = Image.open(f'{W}/map.png').convert('RGB'); WW, HH = base.size
P = json.load(open(f'{W}/pieces_cut.json'))['polylines']; N = json.load(open(f'{W}/names.json'))
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
F2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
col = {'green': (0, 150, 60), 'blue': (0, 110, 230), 'black': (40, 40, 40), 'freestyle': (240, 140, 0)}
pts = {p['id']: [(x * WW / 100, y * HH / 100) for x, y in p['points']] for p in P}
und = [p['id'] for p in P if N.get(str(p['id'])) == '?']
tw, th = WW / cols, HH / rows
done = 0
for r in range(rows):
    for c in range(cols):
        x0, y0, x1, y1 = c * tw, r * th, (c + 1) * tw, (r + 1) * th
        mine = [i for i in und if any(x0 <= x < x1 and y0 <= y < y1 for x, y in pts[i][len(pts[i]) // 2: len(pts[i]) // 2 + 1])]
        if not mine:
            continue
        m = 90
        box = (int(max(0, x0 - m)), int(max(0, y0 - m)), int(min(WW, x1 + m)), int(min(HH, y1 + m)))
        z = 1.9
        im = base.crop(box).resize((int((box[2] - box[0]) * z), int((box[3] - box[1]) * z)), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        tr = lambda q: ((q[0] - box[0]) * z, (q[1] - box[1]) * z)  # noqa: E731
        for p in P:
            q = [tr(v) for v in pts[p['id']]]
            if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q):
                continue
            nm = N.get(str(p['id']), '?')
            if nm == '?':
                d.line(q, fill=(255, 0, 0), width=5)
                for e in (q[0], q[-1]):
                    d.ellipse((e[0] - 4, e[1] - 4, e[0] + 4, e[1] + 4), outline=(255, 0, 0), width=2)
            else:
                d.line(q, fill=col.get(p['cls'], (128, 0, 128)), width=2)
        for p in P:
            q = [tr(v) for v in pts[p['id']]]
            if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q):
                continue
            nm = N.get(str(p['id']), '?')
            mpt = q[len(q) // 2]
            if nm == '?':
                d.text((mpt[0] + 5, mpt[1] - 8), str(p['id']), fill=(255, 255, 255), font=F, stroke_width=3, stroke_fill=(200, 0, 0))
            elif not nm.endswith('~'):
                d.text((mpt[0] + 3, mpt[1] - 6), f"{p['id']}:{nm}", fill=(0, 0, 0), font=F2, stroke_width=2, stroke_fill=(255, 255, 210))
        fn = f'{out}/t{r}{c}_{box[0]}_{box[1]}_{box[2]}_{box[3]}.jpg'
        im.save(fn, quality=88); done += 1
        print(fn, len(mine), sorted(mine))
print(done, 'tiles')
