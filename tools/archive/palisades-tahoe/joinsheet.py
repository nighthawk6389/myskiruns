"""joinsheet.py PANEL OUT: one cell per candidate JOIN (joins.py): the map around the parts, the first part's glyph
centres magenta, the next part's cyan, the third's yellow; caption: the report name."""
import importlib.util, itertools, json, math, re, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/pt'
p, out = sys.argv[1], sys.argv[2]
GAP = 14
F = json.load(open(f'{S}/truth/feed_trails.json'))
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower().replace('’', "'"))  # noqa: E731
feed = {norm(r['name']): r['name'] for r in F}
L = json.load(open(f'/home/user/myskiruns/work/palisades-tahoe/{p}/printed.json'))['labels']
pdf = {'palisades': 'palisades_main.pdf', 'alpine-front': 'alpine_front.pdf', 'alpine-back': 'alpine_back.pdf'}[p]
page = pymupdf.open(f'/home/user/myskiruns/work/palisades-tahoe/{pdf}')[0]
gap = lambda a, b: min(math.dist(x, y) for x in a['pts'] for y in b['pts'])  # noqa: E731
cands = []
for a, b in itertools.permutations(L, 2):
    if gap(a, b) > GAP:
        continue
    if norm(a['text'] + b['text']) in feed and norm(a['text']) not in feed:
        cands.append((feed[norm(a['text'] + b['text'])], [a, b]))
    for c in L:
        if c is a or c is b or gap(b, c) > GAP:
            continue
        if norm(a['text'] + b['text'] + c['text']) in feed:
            cands.append((feed[norm(a['text'] + b['text'] + c['text'])], [a, b, c]))
cands.sort(key=lambda x: x[0])
F2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
z = 5
cells = []
for name, parts in cands:
    xs = [q[0] for l in parts for q in l['pts']]; ys = [q[1] for l in parts for q in l['pts']]
    r = pymupdf.Rect(min(xs) - 14, min(ys) - 14, max(xs) + 14, max(ys) + 14)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=r)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    d = ImageDraw.Draw(im)
    for l, col in zip(parts, [(255, 0, 255), (0, 200, 255), (255, 200, 0)]):
        q = [((x - r.x0) * z, (y - r.y0) * z) for x, y in l['pts']]
        d.line(q, fill=col, width=3)
        for x, y in q:
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=col)
    im.thumbnail((380, 260))
    cell = Image.new('RGB', (380, 280), 'white'); cell.paste(im, (0, 20))
    ImageDraw.Draw(cell).text((3, 2), name + ' ' + ' + '.join(l['text'] for l in parts), fill='black', font=F2)
    cells.append(cell)
cols = 4
for k in range(0, len(cells), 16):
    grp = cells[k:k + 16]
    sheet = Image.new('RGB', (cols * 386, ((len(grp) + cols - 1) // cols) * 286), (90, 90, 90))
    for i, c in enumerate(grp):
        sheet.paste(c, ((i % cols) * 386, (i // cols) * 286))
    sheet.save(f'{out}_{k // 16}.png')
print(len(cells), 'candidates')
