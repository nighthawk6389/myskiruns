"""A trail-map PDF page's stroke classes (colour x width), or its fill colours, each drawn alone on grey, as one
contact sheet: which class is the trails, the lifts, the boundary, the hatching, the legend? Read the trail
colours and widths off it for extract_pdf_vectors.py (--color, --min-width/--max-width).

    python3 tools/trailmap/pdf_classes.py work/<id>/map.pdf --page 0 --out work/<id>/inspect [--n 12] [--fills]
"""
import argparse
import collections
import io
import os

import pymupdf
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
ap.add_argument('pdf')
ap.add_argument('--page', type=int, default=0)
ap.add_argument('--out', default='.')
ap.add_argument('--n', type=int, default=12, help='the n most common classes')
ap.add_argument('--fills', action='store_true', help='fill colours instead of stroke classes')
a = ap.parse_args()
pdf, pno, n, fills, OUT = a.pdf, a.page, a.n, a.fills, a.out
tag = os.path.splitext(os.path.basename(pdf))[0]
os.makedirs(OUT, exist_ok=True)
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
