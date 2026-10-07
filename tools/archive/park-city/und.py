"""und.py x0,y0,x1,y1 zoom out: the map crop (map px) with named pieces thin (their colour), undecided ones thick
red with their ids, names' labels as in names.json."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
W = '/home/user/myskiruns/work/park-city'
box = tuple(map(int, sys.argv[1].split(','))); z = float(sys.argv[2]); out = sys.argv[3]
im = Image.open(f'{W}/map.png').convert('RGB').crop(box)
im = im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.35)
d = ImageDraw.Draw(im)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
P = json.load(open(f'{W}/pieces_cut.json'))['polylines']; N = json.load(open(f'{W}/names.json'))
WW, HH = Image.open(f'{W}/map.png').size
col = {'green': (0, 150, 60), 'blue': (0, 120, 220), 'black': (0, 0, 0), 'freestyle': (240, 140, 0)}
for p in P:
    pts = [((x * WW / 100 - box[0]) * z, (y * HH / 100 - box[1]) * z) for x, y in p['points']]
    if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in pts):
        continue
    nm = N.get(str(p['id']), '?')
    if nm == '?':
        d.line(pts, fill=(255, 0, 0), width=4)
        m = pts[len(pts) // 2]
        d.text((m[0] + 3, m[1] - 7), str(p['id']), fill=(200, 0, 0), font=F)
    else:
        d.line(pts, fill=col.get(p['cls'], (128, 0, 128)), width=1)
im.save(out); print(out, im.size)
