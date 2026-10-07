"""classes.py map.pdf page tag [n] [--fills]: contact sheet of the top-n stroke classes (colour, width) drawn alone, each on grey."""
import sys, collections, os, io
import pymupdf
from PIL import Image, ImageDraw
pdf, pno, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3]
n = int(sys.argv[4]) if len(sys.argv) > 4 and not sys.argv[4].startswith('-') else 12
fills = '--fills' in sys.argv
OUT = os.path.dirname(os.path.abspath(__file__))
d = pymupdf.open(pdf); p = d[pno]
dr = p.get_drawings()
def col(c): return tuple(round(v, 2) for v in c) if c else None
cls = collections.defaultdict(list)
for x in dr:
    if fills:
        if 'f' in x['type'] and x.get('fill') is not None:
            cls[(col(x['fill']), 'f')].append(x)
    elif 's' in x['type'] and x.get('color') is not None:
        cls[(col(x['color']), round(x.get('width') or 0, 2))].append(x)
top = sorted(cls.items(), key=lambda kv: -len(kv[1]))[:n]
W = 700
sc = W / p.rect.width
tiles = []
for k, xs in top:
    q = pymupdf.open(); np_ = q.new_page(width=p.rect.width, height=p.rect.height)
    np_.draw_rect(np_.rect, color=None, fill=(0.6, 0.6, 0.6))
    sh = np_.new_shape()
    for x in xs:
        for it in x['items']:
            if it[0] == 'l': sh.draw_line(it[1], it[2])
            elif it[0] == 'c': sh.draw_bezier(it[1], it[2], it[3], it[4])
            elif it[0] == 're': sh.draw_rect(it[1])
            elif it[0] == 'qu': sh.draw_quad(it[1])
        if fills:
            sh.finish(color=None, fill=x['fill'], closePath=True, even_odd=x.get('even_odd', False))
        else:
            sh.finish(color=x['color'], width=max(x.get('width') or 0.5, 2.0 / sc), closePath=x.get('closePath', False))
    sh.commit()
    pm = np_.get_pixmap(matrix=pymupdf.Matrix(sc, sc))
    im = Image.open(io.BytesIO(pm.tobytes('png'))).convert('RGB')
    dd = ImageDraw.Draw(im); dd.rectangle([0, 0, W, 14], fill=(255, 255, 255)); dd.text((3, 1), f'{k} n={len(xs)}', fill=(0, 0, 0))
    tiles.append(im)
cols = 3
h = tiles[0].height
sheet = Image.new('RGB', (W * cols, h * ((len(tiles) + cols - 1) // cols)), (255, 255, 255))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * W, (i // cols) * h))
fn = f'{OUT}/{tag}_classes{"_fills" if fills else ""}_p{pno}.png'
sheet.save(fn); print(fn, sheet.size)
