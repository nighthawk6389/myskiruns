import sys, json, pymupdf
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap/resorts/heavenly')
import prepare as P
R = P.top()
panel = sys.argv[1]
pg = pymupdf.open('/home/user/myskiruns/work/heavenly/heavenly_2022.pdf')[0]
A, box = R.AFFINE[panel], R.BOX[panel]
L = P.line_outlines(pg, P.SETUP[panel])
for cls, seq, pts, n in sorted(L, key=lambda l: l[1]):
    a = P.to_px(A, box, pts[0]); b = P.to_px(A, box, pts[-1])
    print(seq, cls, round(n * 3.125), (round(a[0]), round(a[1])), (round(b[0]), round(b[1])))
