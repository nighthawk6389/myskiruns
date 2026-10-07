"""Crops of Breckenridge's short lead-in stubs (pieces under 4 pt, appended after the first extraction pass): each
stub in magenta over the PDF rendered at 10 px/pt, the other pieces thin in their colour tagged id:name, and the
current overlays (trailPaths.json) in orange. Writes work/breckenridge/stubs/<id>.png.

    python3 tools/trailmap/resorts/breckenridge/checks/stubs.py [ids ...]   # default: every piece from 352 on
"""
import json, os, sys
import pymupdf
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from common import DATA, PDF, work  # noqa: E402

Z, R = 10, 28  # px per pt, half box size in pt
pl = json.load(open(os.path.join(DATA, 'linePolylines.json')))['polylines']
paths = json.load(open(os.path.join(DATA, 'trailPaths.json')))['trails']
reading = json.load(open(work('tiles/result_breck.json')))
name_of = {l['id']: l['mapName'] for l in reading['lines']}
COL = {'black': (0, 0, 0), 'blue': (0, 70, 220), 'green': (0, 140, 0)}


def pt(p):  # percent of the map clip (0,80-1458,925 pt) -> PDF pt
    return 14.58 * p[0], 80 + 8.45 * p[1]


ids = [int(i) for i in sys.argv[1:]] or [p['id'] for p in pl if p['id'] >= 352]
page = pymupdf.open(PDF)[0]
os.makedirs(work('stubs'), exist_ok=True)
for sid in ids:
    s = next(p for p in pl if p['id'] == sid)
    P = [pt(q) for q in s['points']]
    cx, cy = sum(x for x, _ in P) / len(P), sum(y for _, y in P) / len(P)
    box = pymupdf.Rect(cx - R, cy - R, cx + R, cy + R)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), clip=box)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    d = ImageDraw.Draw(im)
    f = lambda x, y: ((x - box.x0) * Z, (y - box.y0) * Z)  # noqa: E731
    for tid, t in paths.items():  # current overlays, orange
        for seg in t.get('segments', []):
            Q = [f(*pt(q)) for q in seg]
            if any(0 <= x <= im.width and 0 <= y <= im.height for x, y in Q):
                d.line(Q, fill=(255, 140, 0), width=3)
    for p in pl:
        Q = [f(*pt(q)) for q in p['points']]
        if p['id'] == sid or not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in Q):
            continue
        d.line(Q, fill=COL.get(p['cls'], (90, 90, 90)), width=1)
        mx, my = Q[len(Q) // 2]
        d.text((mx + 3, my + 3), f"{p['id']}:{name_of.get(p['id'], '?')}", fill=(200, 0, 0))
    Q = [f(*q) for q in P]
    d.line(Q, fill=(255, 0, 255), width=4)
    for q in (Q[0], Q[-1]):
        d.ellipse((q[0] - 5, q[1] - 5, q[0] + 5, q[1] + 5), outline=(255, 0, 255), width=2)
    d.text((6, 6), f'stub {sid} ({s["cls"]}): {name_of.get(sid, "unnamed")}', fill=(255, 0, 255))
    im.save(work(f'stubs/{sid}.png'))
    print(work(f'stubs/{sid}.png'))
