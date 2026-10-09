"""Run pdf_outline_lines' subpath tests on one drawing (by seqno) and print why each subpath passes or fails."""
import sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pymupdf
import pdf_outline_lines as pol
pdf, seq = sys.argv[1], int(sys.argv[2])
page = pymupdf.open(pdf)[0]
for d in page.get_drawings():
    if d['seqno'] != seq:
        continue
    print('drawing', seq, d['type'], d['rect'], len(d['items']))
    for sp in pol.subpaths(d):
        k = ''.join(it[0] for it in sp)
        c, w = pol.centre(sp)
        L = pol.length(c) if c else None
        print(' subpath', len(sp), k[:30], 'centre pts', len(c) if c else None, 'w', w and round(w, 2), 'len', L and round(L, 1),
              'area', round(pol.area(pol.outline(sp)), 1))
