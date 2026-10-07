"""wp_zoom.py prefix x0,y0,x1,y1 ...  (PDF pt) - crops of the source PNG with every piece drawn and tagged
'id:auto-name' ('?' unassigned, '!' several names). Z env = zoom (default 1.3). Was the scratch wp_zoom.py.

    Z=2.6 python3 tools/trailmap/resorts/winter-park/checks/zoom.py reg/chutes 335,505,425,590   # from the repo root

Reads $WINTER_PARK_WORK (default work/winter-park)/wp_source.png, wp_assign.json (automatch.py; ASSIGN env: another
file) and src/data/resorts/winter-park/linePolylines.json; writes <prefix>_<k>.jpg in the work folder.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
S, X0, Y0 = 3.2, 40, 165
WORK = os.environ.get('WINTER_PARK_WORK', 'work/winter-park')
src = Image.open(os.path.join(WORK, 'wp_source.png')).convert('RGB'); W, H = src.size
P = json.load(open('src/data/resorts/winter-park/linePolylines.json'))['polylines']
A = json.load(open(os.environ.get('ASSIGN', os.path.join(WORK, 'wp_assign.json'))))['assign']
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
prefix = os.path.join(WORK, sys.argv[1])
os.makedirs(os.path.dirname(prefix), exist_ok=True)
C = {'blue': (255, 0, 255), 'black': (255, 110, 0), 'green': (0, 230, 230)}
z = float(os.environ.get('Z', '1.3'))
for k, b in enumerate(sys.argv[2:]):
    x0, y0, x1, y1 = map(float, b.split(','))
    box = tuple(int(v) for v in ((x0 - X0) * S, (y0 - Y0) * S, (x1 - X0) * S, (y1 - Y0) * S))
    im = src.crop(box).resize((int((box[2] - box[0]) * z), int((box[3] - box[1]) * z)), Image.LANCZOS)
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    tags = []
    for p in P:
        pts = [((x * W / 100 - box[0]) * z, (y * H / 100 - box[1]) * z) for x, y in p['points']]
        ins = [q for q in pts if 0 <= q[0] < im.width and 0 <= q[1] < im.height]
        if not ins:
            continue
        d.line(pts, fill=C[p['cls']] + (170,), width=3)
        for e in (pts[0], pts[-1]):
            d.ellipse((e[0] - 3, e[1] - 3, e[0] + 3, e[1] + 3), fill=(255, 0, 0, 220))
        q = ins[len(ins) // 2]
        nm = A.get(str(p['id']), [])
        tags.append((q, f"{p['id']}" + (f":{nm[0][:12]}" if len(nm) == 1 else ('?' if not nm else '!'))))
    for (x, y), t in tags:
        w = d.textlength(t, font=f)
        d.rectangle((x + 3, y - 8, x + w + 7, y + 8), fill=(255, 255, 0, 200)); d.text((x + 5, y - 8), t, fill=(0, 0, 0, 255), font=f)
    Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB').save(f'{prefix}_{k}.jpg', quality=88)
print(len(sys.argv) - 2, 'crops')
