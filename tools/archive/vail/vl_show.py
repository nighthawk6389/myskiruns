"""vl_show.py panel out.png x0,y0,x1,y1 [zoom] [--ids a,b] [--names file]: the panel image (faded) with pieces
drawn in bright colours, numbered (or named from an assignment json {id: name})."""
import sys, json, colorsys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
Image.MAX_IMAGE_PIXELS = None
panel, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3].split(','))
z = float(sys.argv[4]) if len(sys.argv) > 4 and not sys.argv[4].startswith('--') else 1.0
only = {int(v) for v in sys.argv[sys.argv.index('--ids') + 1].split(',')} if '--ids' in sys.argv else None
names = json.load(open(sys.argv[sys.argv.index('--names') + 1])) if '--names' in sys.argv else None
lines = sys.argv[sys.argv.index('--lines') + 1] if '--lines' in sys.argv else f'pieces_{panel}.json'
src = Image.open(f'{panel}.png').convert('RGB')
W, H = src.size
im = src.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * z), int((y1 - y0) * z)), Image.LANCZOS)
im = ImageEnhance.Color(im).enhance(0.3)
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.35)
dr = ImageDraw.Draw(im)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
for q in json.load(open(lines))['polylines']:
    if only and q['id'] not in only:
        continue
    pts = [((u / 100 * W - x0) * z, (v / 100 * H - y0) * z) for u, v in q['points']]
    if not any(0 <= x < im.width and 0 <= y < im.height for x, y in pts):
        continue
    h = (q['id'] * 0.618) % 1
    col = tuple(int(255 * c) for c in colorsys.hsv_to_rgb(h, 1, 0.85))
    dr.line(pts, fill=col, width=3)
    for e in (pts[0], pts[-1]):
        dr.ellipse((e[0] - 3, e[1] - 3, e[0] + 3, e[1] + 3), outline=col, width=2)
    ins = [p for p in pts if 0 <= p[0] < im.width and 0 <= p[1] < im.height]
    m = ins[len(ins) // 2]
    t = str(q['id']) if names is None else f"{q['id']}:{names.get(str(q['id']), '?')[:14]}"
    dr.text((m[0] + 3, m[1] - 7), t, fill=col, font=font, stroke_width=2, stroke_fill='white')
im.save(out); print(im.size)
