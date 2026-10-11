import pickle, sys
import pymupdf
from PIL import Image, ImageDraw
dr = pickle.load(open(sys.argv[1], 'rb'))
z = float(sys.argv[2]); out = sys.argv[3]
W, H = int(1440 * z), int(1224 * z)
im = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(im)
want = {((0.0, 0.61, 0.86), 0.69): (0, 120, 255), ((0.14, 0.12, 0.13), 0.69): (0, 0, 0), ((0.0, 0.65, 0.32), 0.69): (0, 170, 0),
        ((0.0, 0.65, 0.32), 2.78): (150, 255, 150), ((0.14, 0.12, 0.13), 2.78): (150, 150, 150)}
n = 0
for x in dr:
    if x.get('color') is None or x['type'] not in ('s', 'fs'): continue
    k = (tuple(round(v, 2) for v in x['color']), round(x.get('width') or 0, 2))
    if k not in want: continue
    for it in x['items']:
        if it[0] == 'l': pts = [it[1], it[2]]
        elif it[0] == 'c': pts = [it[1], it[2], it[3], it[4]]
        else: continue
        d.line([(p.x * z, p.y * z) for p in pts], fill=want[k], width=2 if k[1] < 1 else 5)
        n += 1
im.save(out); print(n, im.size)
