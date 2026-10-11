"""Tally a big page's strokes and small fills by colour once (get_drawings), save the tally, and draw the
trail-coloured strokes and fills alone over a faded render."""
import collections, json, pickle, sys
import pymupdf
from PIL import Image, ImageDraw
pdf, page, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
d = pymupdf.open(pdf); p = d[page]
dr = p.get_drawings()
pickle.dump(dr, open(out + '.pkl', 'wb'))
cs = collections.Counter(); cf = collections.Counter()
for x in dr:
    if x.get('color') is not None and x['type'] in ('s', 'fs'):
        cs[(tuple(round(v, 2) for v in x['color']), round(x.get('width') or 0, 2))] += 1
    if x.get('fill') is not None and x['type'] in ('f', 'fs'):
        r = x['rect']
        cf[(tuple(round(v, 2) for v in x['fill']), 'small' if max(r.width, r.height) < 12 else 'big')] += 1
print('strokes'); [print(' ', k, v) for k, v in cs.most_common(30)]
print('fills'); [print(' ', k, v) for k, v in cf.most_common(40)]
