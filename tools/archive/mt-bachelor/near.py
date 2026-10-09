"""List the PDF drawings whose bbox holds a map-px point (Mt. Bachelor: px = 3 * (pt - (355, 0)))."""
import sys
import pymupdf
pdf, pts = sys.argv[1], [tuple(map(float, a.split(','))) for a in sys.argv[2:]]
page = pymupdf.open(pdf)[0]
dr = page.get_drawings(extended=False)
for (px, py) in pts:
    x, y = px / 3 + 355, py / 3
    print(f'== px {px:.0f},{py:.0f} -> pt {x:.1f},{y:.1f}')
    for i, d in enumerate(dr):
        r = d['rect']
        if r.x0 - 2 <= x <= r.x1 + 2 and r.y0 - 2 <= y <= r.y1 + 2 and r.width < 400:
            col = d.get('fill') or d.get('color')
            print(i, d['type'], 'seq', d.get('seqno'), 'fill', d.get('fill') and tuple(round(c, 2) for c in d['fill']),
                  'stroke', d.get('color') and tuple(round(c, 2) for c in d['color']), 'w', d.get('width'),
                  'rect', [round(v, 1) for v in r], 'items', len(d['items']))
