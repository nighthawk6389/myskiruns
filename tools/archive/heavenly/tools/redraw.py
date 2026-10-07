"""redraw.py: redraw selected fills of a PDF page on a blank page (pymupdf Shape) and render it.
Used as a module: redraw(page, drawings, scale, clip) -> RGB numpy array."""
import numpy as np
import pymupdf


def redraw(page, drawings, scale, clip=None, colour=None):
    doc = pymupdf.open()
    out = doc.new_page(width=page.rect.width, height=page.rect.height)
    for d in drawings:
        sh = out.new_shape()
        for it in d['items']:
            if it[0] == 'l':
                sh.draw_line(it[1], it[2])
            elif it[0] == 'c':
                sh.draw_bezier(it[1], it[2], it[3], it[4])
            elif it[0] == 're':
                sh.draw_rect(it[1])
            elif it[0] == 'qu':
                sh.draw_quad(it[1])
        sh.finish(fill=colour or d.get('fill'), color=None, even_odd=d.get('even_odd', False),
                  closePath=d.get('closePath', True))
        sh.commit()
    pix = out.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=clip, alpha=False)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3].copy()
