"""overview.py PANEL x0,y0,x1,y1 scale out.png : pieces over the map, red = undecided (with id), green = named,
blue = stretch along a name, grey = not a trail."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
W = f'/home/user/myskiruns/work/whistler-blackcomb/{sys.argv[1]}'
x0, y0, x1, y1 = map(int, sys.argv[2].split(',')); s = float(sys.argv[3]); out = sys.argv[4]
im = Image.open(f'{W}/map.png').convert('RGB').crop((x0, y0, x1, y1))
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.35)
im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
dr = ImageDraw.Draw(im)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
P = json.load(open(f'{W}/pieces_cut.json'))['polylines']
N = json.load(open(f'{W}/names.json'))
WW, HH = Image.open(f'{W}/map.png').size
for p in P:
    tag = N.get(str(p['id']), '?')
    col = (220, 0, 0) if tag == '?' else (130, 130, 130) if tag == '-' else (0, 90, 255) if tag.endswith('~') else (0, 160, 0)
    pts = [((x * WW / 100 - x0) * s, (y * HH / 100 - y0) * s) for x, y in p['points']]
    if len(pts) > 1: dr.line(pts, fill=col, width=3)
    if tag == '?':
        m = pts[len(pts) // 2]
        dr.text((m[0] + 3, m[1] - 6), str(p['id']), fill=(200, 0, 0), font=F, stroke_width=2, stroke_fill='white')
im.save(out); print(out, im.size)
