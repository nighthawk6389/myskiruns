"""Markers vs labels: python3 tools/trailmap/resorts/jay-peak/checks/markers.py

For every marker in trailPaths.json (glades, parks, the inset name and the trails with no cut), its position and
the printed copies of its label from the PDF text, with the distance to the nearest (all 23 sit on one,
0 px). Reads $JAY_PEAK_WORK (default work/jay-peak, filled by regen.sh): labels.json and
reading_pdf.json; and src/data/resorts/jay-peak/trailPaths.json. Was inline code (2026-09-30 14:59).
"""
import json
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *['..'] * 5))
WORK = os.environ.get('JAY_PEAK_WORK', os.path.join(ROOT, 'work', 'jay-peak'))
L = json.load(open(os.path.join(WORK, 'labels.json')))
R = json.load(open(os.path.join(WORK, 'reading_pdf.json')))['labels']
P = json.load(open(os.path.join(ROOT, 'src/data/resorts/jay-peak/trailPaths.json')))['trails']
W, H = 4268, 2364
for tid, p in sorted(P.items()):
    if not p.get('label'):
        continue
    x, y = p['label'][0] * W / 100, p['label'][1] * H / 100
    raw = [l['labelSrc'] for l in R if l['mapName'] == L[tid]['mapName']]
    d = min(((x - a) ** 2 + (y - b) ** 2) ** 0.5 for a, b in raw)
    print(f"{tid:22} marker ({x:.0f},{y:.0f})  printed labels {raw}  nearest {d:.0f}px")
