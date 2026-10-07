"""symsheet.py difficulty[,difficulty] out.jpg  - contact sheets: every label with a given roster difficulty,
rendered from the PDF with its symbol, captioned with the difficulty and the symbol(s) the PDF fills gave it (or
the zone it inherits).

Scratch: br_symsheet.py. Reads work/breckenridge.pdf, work/names.json (names.py) and
src/data/resorts/breckenridge/trails.ts. Every single and double diamond was checked this way (sym_blk, sym_dbl).
"""
import json, math, os, re, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import DATA, PDF, work  # noqa: E402
p = pymupdf.open(PDF)[0]
N = json.load(open(work('names.json')))
ts = open(os.path.join(DATA, 'trails.ts')).read()
diff = {m.group(2).strip('"\'').replace("'", '’'): m.group(3) for m in re.finditer(
    r"id: '([^']+)', name: (\"[^\"]+\"|'[^']+'), difficulty: '([^']+)'", ts)}
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
want = sys.argv[1].split(',')
cells = []
for o in N['labels']:
    d = diff.get(o['text'])
    if d not in want:
        continue
    xs = [q[0] for q in o['pts']]; ys = [q[1] for q in o['pts']]
    for s in N['syms']:
        if s.get('label') == o['text'] and min(math.dist(s['c'], q) for q in o['pts']) < 25:
            xs.append(s['c'][0]); ys.append(s['c'][1])
    r = pymupdf.Rect(min(xs) - 7, min(ys) - 7, max(xs) + 7, max(ys) + 7)
    pix = p.get_pixmap(clip=r, matrix=pymupdf.Matrix(5, 5))
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    im.thumbnail((300, 165))
    cells.append((o['text'], d, o['syms'], im))
cols, W, H = 5, 310, 195
sheet = Image.new('RGB', (cols * W, ((len(cells) + cols - 1) // cols) * H), 'white')
dr = ImageDraw.Draw(sheet)
for i, (t, d, syms, im) in enumerate(cells):
    x, y = (i % cols) * W, (i // cols) * H
    sheet.paste(im, (x + 5, y + 5))
    dr.text((x + 5, y + 172), f'{t[:18]} = {d} {"/".join(syms) or "(zone)"}', fill=(200, 0, 0), font=f)
sheet.save(sys.argv[2], quality=85)
print(len(cells), 'cells', sheet.size)
