import pymupdf, sys
f, pn, z = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
src = pymupdf.open(f)[pn]
doc = pymupdf.open(); page = doc.new_page(width=src.rect.width, height=src.rect.height)
n = 0
for g in src.get_drawings():
    sh = page.new_shape()
    for it in g['items']:
        k = it[0]
        if k == 'l': sh.draw_line(it[1], it[2])
        elif k == 'c': sh.draw_bezier(it[1], it[2], it[3], it[4])
        elif k == 're': sh.draw_rect(it[1])
        elif k == 'qu': sh.draw_quad(it[1])
    sh.finish(color=g.get('color'), fill=g.get('fill'), width=g.get('width') or 0, closePath=g.get('closePath', False), even_odd=g.get('even_odd', False))
    sh.commit(); n += 1
pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z)); out = f'vec_{f[:-4]}_{pn}.png'; pix.save(out); print(out, n, pix.width, pix.height)
