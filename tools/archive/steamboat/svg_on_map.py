"""Draw the interactive map's trail lines (trails.json, SVG units) on a map image through an affine; crop boxes."""
import json, sys
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
img, tj, aff, out = sys.argv[1], sys.argv[2], [float(v) for v in sys.argv[3].split(',')], sys.argv[4]
boxes = [tuple(int(v) for v in b.split(',')) for b in sys.argv[5:]]
a, b, c, d, e, f = aff
im = Image.open(img).convert('RGB')
dr = ImageDraw.Draw(im)
T = json.load(open(tj))
col = {'green': (0, 200, 0), 'blue': (0, 80, 255), 'black': (0, 0, 0), 'double-black': (0, 0, 0)}
for t in T['trails']:
    for pl in t['lines']:
        pts = [(a * x + b * y + c, d * x + e * y + f) for x, y in pl]
        if len(pts) > 1:
            dr.line(pts, fill=(255, 0, 255), width=1)
    if t['lines']:
        x, y = t['lines'][0][len(t['lines'][0]) // 2]
        dr.text((a * x + b * y + c + 3, d * x + e * y + f), t['name'], fill=(255, 0, 255))
for k, bx in enumerate(boxes):
    cr = im.crop(bx)
    cr.resize((cr.width * 3, cr.height * 3), Image.LANCZOS).save(f'{out}_{k}.png')
if not boxes:
    im.save(out + '.png')
