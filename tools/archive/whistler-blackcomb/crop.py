"""crop.py PAGE x0 y0 x1 y1 ZOOM OUT [--vec-only]: render a page region of the Whistler PDF."""
import sys, pymupdf
pdf = '/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf'
pg, x0, y0, x1, y1, z = int(sys.argv[1]), *map(float, sys.argv[2:7])
out = sys.argv[7]
doc = pymupdf.open(pdf)
p = doc[pg]
pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(x0, y0, x1, y1))
pix.save(out)
print(out, pix.width, pix.height)
