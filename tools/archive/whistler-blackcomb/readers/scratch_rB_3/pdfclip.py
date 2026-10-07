import pymupdf, sys
# usage: pdfclip.py x0 y0 x1 y1 zoom out.png   (map px box; zoom = output px per map px)
x0,y0,x1,y1,z = [float(v) for v in sys.argv[1:6]]
out = sys.argv[6]
S = 2.5
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf')
pg = doc[1]
clip = pymupdf.Rect(x0/S, y0/S, x1/S, y1/S)
pix = pg.get_pixmap(matrix=pymupdf.Matrix(S*z, S*z), clip=clip)
pix.save(out)
print(out, pix.width, pix.height)
