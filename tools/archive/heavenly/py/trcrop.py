"""Crops for tracing: the map with the panel's pieces (thin), every no-line name's label polyline (magenta, its start
circled) and candidate traces (traces.json: [[name, [[x, y], ...]], ...], cyan). trcrop.py panel out x0,y0,x1,y1 zoom"""
import sys, json, io, contextlib
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad'
panel, out = sys.argv[1], sys.argv[2]
box = [int(v) for v in sys.argv[3].split(',')]; z = float(sys.argv[4])
r = pr.Resort(f'heavenly/{panel}')
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
im = Image.open(r.work('map.png')).convert('RGB').crop(box)
im = im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)
d = ImageDraw.Draw(im)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
T = lambda p: ((p[0] - box[0]) * z, (p[1] - box[1]) * z)  # noqa: E731
for x in range(box[0] - box[0] % 50, box[2], 50):
    d.line([T((x, box[1])), T((x, box[3]))], fill=(255, 0, 255) if x % 100 == 0 else (200, 120, 255), width=1)
    if x % 100 == 0:
        d.text((T((x, box[1]))[0] + 2, 2), str(x), fill=(255, 0, 255), font=F)
for y in range(box[1] - box[1] % 50, box[3], 50):
    d.line([T((box[0], y)), T((box[2], y))], fill=(255, 0, 255) if y % 100 == 0 else (200, 120, 255), width=1)
    if y % 100 == 0:
        d.text((2, T((box[0], y))[1] + 2), str(y), fill=(255, 0, 255), font=F)
for p in r.P:
    if p['id'] in r.traced:
        continue
    d.line([T(q) for q in p['pt']], fill=(255, 255, 0), width=1)
drawn = {n for pid, v in r.assign.items() if pid not in r.traced for n in v}
for n in r.names_:
    if n['name'] in drawn:
        continue
    pts = [T(q) for q in n['pts']]
    if len(pts) > 1:
        d.line(pts, fill=(255, 0, 200), width=2)
    d.ellipse((pts[0][0] - 4, pts[0][1] - 4, pts[0][0] + 4, pts[0][1] + 4), outline=(255, 0, 200), width=2)
try:
    tr = json.load(open(f'{S}/hv/traces_{panel}.json'))
except FileNotFoundError:
    tr = []
for name, pts in tr:
    q = [T(p) for p in pts]
    d.line(q, fill=(0, 255, 255), width=3)
    for p in q:
        d.ellipse((p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3), fill=(0, 255, 255))
    d.text((q[0][0] + 5, q[0][1] - 14), name, fill=(0, 255, 255), font=F, stroke_width=2, stroke_fill=(0, 0, 0))
im.save(out)
print(out, im.size)
