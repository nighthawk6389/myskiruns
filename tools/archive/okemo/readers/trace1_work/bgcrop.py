"""bgcrop.py out.png x0 y0 x1 y1 zoom [grid] [pieces|none] [traces json]: background raster only (no vectors), in source px."""
import sys, json
from PIL import Image, ImageDraw, ImageFont
bg = Image.open('/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/okemo/trace1_work/bg.png').convert('RGB')
ox, oy, sw, sh = -19.302, -57.425, 1486.425 / 1485, 996.139 / 995
out = sys.argv[1]; x0, y0, x1, y1 = map(int, sys.argv[2:6]); s = float(sys.argv[6]); grid = int(sys.argv[7]) if len(sys.argv) > 7 else 0
which = sys.argv[8] if len(sys.argv) > 8 else 'none'
trace = json.loads(sys.argv[9]) if len(sys.argv) > 9 else []
def to_raster(x, y): return ((x / 3 - ox) / sw, (y / 3 - oy) / sh)
u0, v0 = to_raster(x0, y0); u1, v1 = to_raster(x1, y1)
im = bg.transform((int((x1 - x0) * s), int((y1 - y0) * s)), Image.EXTENT, (u0, v0, u1, v1), Image.BICUBIC).convert('RGBA')
ov = Image.new('RGBA', im.size); d = ImageDraw.Draw(ov); font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
if grid:
    for gx in range((x0 // grid + 1) * grid, x1, grid):
        X = (gx - x0) * s; d.line([(X, 0), (X, im.size[1])], fill=(255, 255, 0, 110)); d.text((X + 2, 2), str(gx), fill=(255, 255, 0, 255), font=font)
    for gy in range((y0 // grid + 1) * grid, y1, grid):
        Y = (gy - y0) * s; d.line([(0, Y), (im.size[0], Y)], fill=(255, 255, 0, 110)); d.text((2, Y + 2), str(gy), fill=(255, 255, 0, 255), font=font)
if which != 'none':
    W, H = 4374, 2739
    polys = {p['id']: [(x * W / 100, y * H / 100) for x, y in p['points']] for p in json.load(open('/home/user/myskiruns/src/data/resorts/okemo/linePolylines.json'))['polylines']}
    ids = list(polys) if which == 'all' else [int(v) for v in which.split(',')]
    for i in ids:
        q = [((x - x0) * s, (y - y0) * s) for x, y in polys[i]]
        if not any(-50 < a < im.size[0] + 50 and -50 < b < im.size[1] + 50 for a, b in q): continue
        d.line(q, fill=(255, 0, 255, 120), width=1)
        vis = [p for p in q if 0 <= p[0] < im.size[0] and 0 <= p[1] < im.size[1]]
        if vis: m = vis[len(vis) // 2]; d.text((m[0] + 2, m[1]), str(i), fill=(255, 0, 255, 255), font=font)
cols = [(255, 120, 0, 230), (0, 200, 255, 230), (0, 255, 0, 230), (255, 0, 0, 230)]
if trace:
    if isinstance(trace, dict): trace = list(trace.values())
    elif isinstance(trace[0][0], (int, float)): trace = [trace]
    for ti, tr in enumerate(trace):
        q = [((x - x0) * s, (y - y0) * s) for x, y in tr]; c = cols[ti % 4]
        if len(q) > 1: d.line(q, fill=c, width=2)
        for a, b in q: d.ellipse((a - 3, b - 3, a + 3, b + 3), outline=c, width=2)
Image.alpha_composite(im, ov).convert('RGB').save(out); print(out, im.size)
