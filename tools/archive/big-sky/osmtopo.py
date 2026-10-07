"""osmtopo.py OUT name[,name..]: plot OSM runs with these names (and every run within 150 m, grey) in metres,
north up, each labelled at both ends with its name and way id; prints where each way starts and ends and which
named ways it touches (within 8 m)."""
import json, math, sys
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad'
out, names = sys.argv[1], sys.argv[2].split(',')
d = json.load(open(f'{S}/bs/osm/bs.json'))
els = d['elements'] if isinstance(d, dict) else d
nodes = {e['id']: (e['lon'], e['lat']) for e in els if e['type'] == 'node'}
lat0 = 45.27
def xy(lon, lat):
    return (lon * math.cos(math.radians(lat0)) * 111320, -lat * 110540)
ways = []
for e in els:
    if e['type'] != 'way' or e.get('tags', {}).get('piste:type') != 'downhill':
        continue
    if 'geometry' in e:
        pts = [xy(g['lon'], g['lat']) for g in e['geometry']]
    else:
        pts = [xy(*nodes[n]) for n in e['nodes'] if n in nodes]
    if len(pts) > 1:
        ways.append((e['id'], e['tags'].get('name', ''), pts))
sel = [w for w in ways if w[1] in names]
if not sel:
    sys.exit('none')
xs = [p[0] for w in sel for p in w[2]]; ys = [p[1] for w in sel for p in w[2]]
x0, x1, y0, y1 = min(xs) - 150, max(xs) + 150, min(ys) - 150, max(ys) + 150
sc = 900 / max(x1 - x0, y1 - y0)
im = Image.new('RGB', (int((x1 - x0) * sc), int((y1 - y0) * sc)), 'white'); dr = ImageDraw.Draw(im)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
T = lambda p: ((p[0] - x0) * sc, (p[1] - y0) * sc)  # noqa: E731
cols = ['red', 'blue', 'green', 'magenta', 'orange', 'purple', 'brown', 'teal', 'olive', 'navy']
for wid, nm, pts in ways:
    if any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in pts) and nm not in names:
        dr.line([T(p) for p in pts], fill=(190, 190, 190), width=1)
        dr.text(T(pts[len(pts) // 2]), nm, fill=(150, 150, 150), font=F)
for k, (wid, nm, pts) in enumerate(sel):
    c = cols[names.index(nm) % len(cols)]
    dr.line([T(p) for p in pts], fill=c, width=3)
    dr.text(T(pts[0]), f'{nm} {wid} start', fill=c, font=F)
    dr.text(T(pts[-1]), f'end {wid}', fill=c, font=F)
    touch = set()
    for w2, n2, p2 in ways:
        if w2 != wid and n2 and min(math.dist(a, b) for a in (pts[0], pts[-1]) for b in p2) < 8:
            touch.add(n2)
    print(f'{nm} {wid}: {len(pts)} pts, {sum(math.dist(a, b) for a, b in zip(pts, pts[1:])):.0f} m; ends touch {sorted(touch)}')
im.save(out)
