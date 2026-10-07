"""pcrop.py out.png x0 y0 x1 y1 zoom [pieces|all|none] [grid step] [trace json list or {name:list}]
Renders the PDF vectors (page 1) at zoom x source px; draws pieces with ids, a source-px grid, traces."""
import json, sys, io
import pymupdf
from PIL import Image, ImageDraw, ImageFont
PDF = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/okemo/okemo.pdf'
W, H = 4374, 2739
polys = {p['id']: (p['cls'], [(x * W / 100, y * H / 100) for x, y in p['points']]) for p in json.load(open('/home/user/myskiruns/src/data/resorts/okemo/linePolylines.json'))['polylines']}
out = sys.argv[1]; x0, y0, x1, y1 = map(int, sys.argv[2:6]); s = float(sys.argv[6])
which = sys.argv[7] if len(sys.argv) > 7 else 'none'
grid = int(sys.argv[8]) if len(sys.argv) > 8 else 0
trace = json.loads(sys.argv[9]) if len(sys.argv) > 9 else []
page = pymupdf.open(PDF)[1]
pix = page.get_pixmap(matrix=pymupdf.Matrix(3 * s, 3 * s), clip=pymupdf.Rect(x0 / 3, y0 / 3, x1 / 3, y1 / 3))
crop = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGBA')
ov = Image.new('RGBA', crop.size); d = ImageDraw.Draw(ov)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
if grid:
    for gx in range((x0 // grid + 1) * grid, x1, grid):
        X = (gx - x0) * s; d.line([(X, 0), (X, crop.size[1])], fill=(0, 160, 0, 90), width=1); d.text((X + 2, 2), str(gx), fill=(0, 120, 0, 255), font=font)
    for gy in range((y0 // grid + 1) * grid, y1, grid):
        Y = (gy - y0) * s; d.line([(0, Y), (crop.size[0], Y)], fill=(0, 160, 0, 90), width=1); d.text((2, Y + 2), str(gy), fill=(0, 120, 0, 255), font=font)
if which != 'none':
    ids = list(polys) if which == 'all' else [int(v) for v in which.split(',') if v]
    for i in ids:
        cls, pts = polys[i]
        q = [((x - x0) * s, (y - y0) * s) for x, y in pts]
        if not any(-50 < a < crop.size[0] + 50 and -50 < b < crop.size[1] + 50 for a, b in q): continue
        d.line(q, fill=(255, 0, 255, 140), width=2)
        vis = [p for p in q if 0 <= p[0] < crop.size[0] and 0 <= p[1] < crop.size[1]]
        if vis:
            m = vis[len(vis) // 2]; d.rectangle((m[0], m[1], m[0] + 28, m[1] + 15), fill=(255, 255, 255, 200)); d.text((m[0] + 2, m[1]), str(i), fill=(200, 0, 200, 255), font=font)
cols = [(255, 120, 0, 230), (0, 200, 255, 230), (0, 200, 0, 230), (255, 0, 0, 230)]
if trace:
    if isinstance(trace, dict): trace = list(trace.values())
    elif trace and isinstance(trace[0][0], (int, float)): trace = [trace]
    for ti, tr in enumerate(trace):
        q = [((x - x0) * s, (y - y0) * s) for x, y in tr]
        c = cols[ti % len(cols)]
        if len(q) > 1: d.line(q, fill=c, width=3)
        for a, b in q: d.ellipse((a - 4, b - 4, a + 4, b + 4), outline=c, width=2)
Image.alpha_composite(crop, ov).convert('RGB').save(out)
print(out, crop.size)
