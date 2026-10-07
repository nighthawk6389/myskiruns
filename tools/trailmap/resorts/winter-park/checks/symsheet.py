"""Contact sheets: every label with its symbol, rendered from the PDF, captioned with the roster difficulty.
Was the scratch wp_symsheet.py.

    python3 tools/trailmap/resorts/winter-park/checks/symsheet.py double-black sym_dbl.jpg   # from the repo root
    python3 tools/trailmap/resorts/winter-park/checks/symsheet.py black sym_blk.jpg

Reads $WINTER_PARK_WORK (default work/winter-park)/winterpark.pdf, wp_names.json and the trail list
(src/data/resorts/winter-park/trails.ts); writes the sheet (labels whose trail has one of the comma-separated
difficulties) in the work folder.
"""
import json, math, os, re, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
WORK = os.environ.get('WINTER_PARK_WORK', 'work/winter-park')
p = pymupdf.open(os.path.join(WORK, 'winterpark.pdf'))[0]
N = json.load(open(os.path.join(WORK, 'wp_names.json')))
ts = open('src/data/resorts/winter-park/trails.ts').read()
diff = {m.group(2).strip('"\'').upper().replace("'", '’'): m.group(3) for m in re.finditer(
    r"id: '([^']+)', name: (\"[^\"]+\"|'[^']+'), difficulty: '([^']+)'", ts)}
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
want = sys.argv[1].split(',')
cells = []
for o in N['labels']:
    key = o['text'].replace('‘', '’')
    d = diff.get(key) or diff.get(o['text'])
    if d not in want:
        continue
    xs = [q[0] for q in o['pts']] + [s['c'][0] for s in N['syms'] if s.get('label') == o['text'] and min(math.dist(s['c'], q) for q in o['pts']) < 25]
    ys = [q[1] for q in o['pts']] + [s['c'][1] for s in N['syms'] if s.get('label') == o['text'] and min(math.dist(s['c'], q) for q in o['pts']) < 25]
    r = pymupdf.Rect(min(xs) - 9, min(ys) - 9, max(xs) + 9, max(ys) + 9)
    pix = p.get_pixmap(clip=r, matrix=pymupdf.Matrix(4, 4))
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    im.thumbnail((300, 170))
    cells.append((o['text'], d, o['syms'], im))
cols = 5
W, H = 310, 205
sheet = Image.new('RGB', (cols * W, ((len(cells) + cols - 1) // cols) * H), 'white')
dr = ImageDraw.Draw(sheet)
for i, (t, d, syms, im) in enumerate(cells):
    x, y = (i % cols) * W, (i // cols) * H
    sheet.paste(im, (x + 5, y + 5))
    dr.text((x + 5, y + 178), f'{t[:20]} = {d} {"/".join(syms) or "-"}', fill=(200, 0, 0), font=f)
sheet.save(os.path.join(WORK, sys.argv[2]), quality=88)
print(len(cells), 'cells', sheet.size)
