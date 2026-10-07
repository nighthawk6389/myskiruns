"""vl_rev.py panel prefix x0,y0,x1,y1 ... [--z 1.25] [--final f.json]: review tiles. Pieces drawn in bright colours
with 'id:name' (auto names from assign_<panel>.json, or the final {id: name} map), symbols tagged '#i NAME'."""
import json, sys, colorsys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
Image.MAX_IMAGE_PIXELS = None
exec(open('vl_symnames.py').read())
args = sys.argv[1:]
z = float(args[args.index('--z') + 1]) if '--z' in args else 1.25
final = json.load(open(args[args.index('--final') + 1])) if '--final' in args else None
boxes = [a for a in args[2:] if ',' in a and not a.endswith('.json')]
panel, prefix = args[0], args[1]
src = Image.open(f'{panel}.png').convert('RGB')
W, H = src.size
P = json.load(open(f'pieces_{panel}.json'))['polylines']
A = json.load(open(f'assign_{panel}.json'))['assign']
S = json.load(open(f'syms_{panel}.json'))
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
for k, b in enumerate(boxes):
    x0, y0, x1, y1 = map(int, b.split(','))
    im = src.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * z), int((y1 - y0) * z)), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.35)
    im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.3)
    d = ImageDraw.Draw(im)
    tags = []
    for p in P:
        pts = [((u / 100 * W - x0) * z, (v / 100 * H - y0) * z) for u, v in p['points']]
        ins = [q for q in pts if 0 <= q[0] < im.width and 0 <= q[1] < im.height]
        if not ins:
            continue
        col = tuple(int(255 * c) for c in colorsys.hsv_to_rgb((p['id'] * 0.618) % 1, 1, 0.85))
        d.line(pts, fill=col, width=3)
        for e in (pts[0], pts[-1]):
            d.ellipse((e[0] - 3, e[1] - 3, e[0] + 3, e[1] + 3), outline=col, width=2)
        if final is not None:
            nm = final.get(str(p['id']))
            t = f"{p['id']}:{nm[:16]}" if nm else f"{p['id']}?"
        else:
            nm = A.get(str(p['id']), [])
            t = f"{p['id']}" + (f":{nm[0][:14]}" if len(nm) == 1 else ('?' if not nm else '!'))
        tags.append((ins[len(ins) // 2], t, col))
    for s in S:
        X, Y = (s['c'][0] - x0) * z, (s['c'][1] - y0) * z
        if 0 <= X < im.width and 0 <= Y < im.height:
            n = NAMES.get(panel, {}).get(s['i'])
            d.text((X - 10, Y - 22), f"#{s['i']}" + (f" {n[:12]}" if n else ''), fill=(120, 0, 120), font=fs,
                   stroke_width=2, stroke_fill='white')
    for (x, y), t, col in tags:
        w = d.textlength(t, font=f)
        d.rectangle((x + 3, y - 8, x + w + 7, y + 8), fill=(255, 255, 160))
        d.text((x + 5, y - 8), t, fill=col if sum(col) < 500 else (0, 0, 0), font=f)
    im.save(f'{prefix}_{k}.jpg', quality=90)
print(len(boxes), 'tiles')
