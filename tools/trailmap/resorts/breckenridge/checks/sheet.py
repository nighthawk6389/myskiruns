"""sheet.py out.jpg name|name|...|@nosym  - context crops of labels from names.json, 4 per row.

Scratch: sheet.py. Reads work/breckenridge.pdf and work/names.json (names.py). @nosym: every label printed with no
symbol of its own (how the bowl and chute names that take their bowl's symbol, ZONE in reading.py, were found).
"""
import json, os, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import PDF, work  # noqa: E402
p = pymupdf.open(PDF)[0]
N = json.load(open(work('names.json')))['labels']
want = sys.argv[2]
sel = [o for o in N if (want == '@nosym' and not o['syms']) or o['text'] in want.split('|')]
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
cells = []
for o in sel:
    xs = [q[0] for q in o['pts']]; ys = [q[1] for q in o['pts']]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    r = pymupdf.Rect(cx - 45, cy - 30, cx + 45, cy + 30)
    pix = p.get_pixmap(clip=r, matrix=pymupdf.Matrix(4, 4))
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    cells.append((o['text'], im))
cols = 4; W, H = 370, 265
sheet = Image.new('RGB', (cols * W, max(1, (len(cells) + cols - 1) // cols) * H), 'white')
d = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(cells):
    x, y = (i % cols) * W, (i // cols) * H
    sheet.paste(im, (x + 5, y + 2)); d.text((x + 5, y + 245), t, fill=(200, 0, 0), font=f)
sheet.save(sys.argv[1], quality=85); print(len(cells), sheet.size)
