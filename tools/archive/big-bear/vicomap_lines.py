import json, sys
from PIL import Image, ImageDraw, ImageFont
vdir, img, out = sys.argv[1], sys.argv[2], sys.argv[3]
A = tuple(float(v) for v in sys.argv[4].split(','))
d = json.load(open(f'{vdir}/trails.json'))
im = Image.open(img).convert('RGB'); dr = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
P = lambda u, v: (A[0] * u + A[1] * v + A[2], A[3] * u + A[4] * v + A[5])
col = {'green': (0, 200, 0), 'blue': (0, 90, 255), 'black': (255, 0, 255), 'double-black': (255, 0, 0)}
for t in d['trails']:
    c = col.get(t['rating'], (255, 255, 0))
    for ln in t['lines']:
        dr.line([P(*q) for q in ln], fill=c, width=2)
    if t['lines']:
        q = P(*t['lines'][0][len(t['lines'][0]) // 2])
        dr.text(q, t['name'], fill=c, font=f, stroke_width=2, stroke_fill='white')
for l in d['lifts']:
    for ln in l.get('lines', []):
        dr.line([P(*q) for q in ln], fill=(255, 128, 0), width=1)
im.save(out)
print(len(d['trails']), sorted((t['name'], t['rating'], len(t['lines']), len(t.get('fills', []))) for t in d['trails']))
