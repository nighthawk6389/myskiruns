"""Stroke and fill tally: python3 tools/trailmap/resorts/sugarbush/checks/stroke_tally.py [map.pdf]

Counts the PDF's stroked paths by (colour, width, dashes) and its filled paths by colour (with their summed
bounding-box area): how the trail colours (0.75 pt blue 0.08,0.51,0.78, black 0.14,0.12,0.13, green
0.08,0.65,0.32) and their odd ones (pure black, 1.0 pt black) were found before choosing the
extract_pdf_vectors.py passes in regen.sh. Default PDF: $SUGARBUSH_WORK/sugarbush.pdf (work/sugarbush).
Was inline code (2026-09-30 11:39, run on the Sugarbush and Jay Peak PDFs at once).
"""
import collections
import os
import sys

import pymupdf

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *['..'] * 5))
WORK = os.environ.get('SUGARBUSH_WORK', os.path.join(ROOT, 'work', 'sugarbush'))
name = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, 'sugarbush.pdf')
page = pymupdf.open(name)[0]
dr = page.get_drawings()
s = collections.Counter(); f = collections.Counter(); farea = collections.Counter()
for d in dr:
    if d['type'] in ('s', 'fs') and d.get('color'):
        s[(tuple(round(v, 2) for v in d['color']), round(d.get('width') or 0, 2),
           tuple(d.get('dashes') or '')[:12] if d.get('dashes') else '')] += 1
    if d['type'] in ('f', 'fs') and d.get('fill'):
        k = tuple(round(v, 2) for v in d['fill']); f[k] += 1; farea[k] += d['rect'].width * d['rect'].height
print('=====', name)
print(' strokes (color, width, dashes):')
for k, n in s.most_common(25):
    print('   ', n, k)
print(' fills (color: count, bbox area):')
for k, n in f.most_common(20):
    print('   ', n, k, round(farea[k]))
