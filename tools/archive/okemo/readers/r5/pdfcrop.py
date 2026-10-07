"""pdfcrop.py x0 y0 x1 y1 zoom out  -- render PDF page 1 region given in SOURCE px (3x) at zoom (px per source px)."""
import sys
import pymupdf
B = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/okemo/'
x0, y0, x1, y1 = map(float, sys.argv[1:5]); z = float(sys.argv[5]); out = sys.argv[6]
page = pymupdf.open(B + 'okemo.pdf')[1]
clip = pymupdf.Rect(x0 / 3, y0 / 3, x1 / 3, y1 / 3)
pix = page.get_pixmap(matrix=pymupdf.Matrix(3 * z, 3 * z), clip=clip)
pix.save(out)
print(out, pix.width, pix.height)
