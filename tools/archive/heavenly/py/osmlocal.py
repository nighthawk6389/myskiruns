"""Draw OSM runs over a crop of the main map, through an affine fitted on nearby lifts' end stations (each lift's
direction chosen to fit best). osmlocal.py OUT x0,y0,x1,y1 zoom lift1,lift2,... [extra map=osm pairs]"""
import json, math, sys, itertools
import numpy as np
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad'
out, box, zoom, names = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], float(sys.argv[3]), sys.argv[4].split(',')
d = json.load(open(f'{S}/hv/osm/hv.json'))
lat0 = 38.93
def m(lat, lon):
    return np.array([lon * math.cos(math.radians(lat0)) * 111320, -lat * 110540])
lifts = {e['tags']['name']: [m(g['lat'], g['lon']) for g in e['geometry']] for e in d['elements']
         if e['type'] == 'way' and 'aerialway' in e.get('tags', {}) and e['tags'].get('name')}
MAP = {
    'Sky Express': ((2027, 428), (2266, 1511)), 'Canyon Express': ((2506, 687), (2362, 1547)),
    'Dipper Express': ((1098, 772), (1000, 1600)), 'Comet Express': ((1345, 1107), (1011, 1629)),
    'Tamarack Express': ((1431, 955), (1738, 1476)), 'Olympic Express': ((1539, 1517), (1081, 1989)),
    'Stagecoach Express': ((870, 1685), (632, 2556)), 'North Bowl Express': ((986, 1790), (983, 2392)),
    'Galaxy': ((828, 1384), (290, 2098)), 'Mott Canyon': ((805, 1096), (303, 1666)),
    'Powderbowl Express': ((2810, 1188), (2836, 1674)), 'Gunbarrel Express': ((3038, 1676), (3335, 2327)),
    'Aerial Tramway': ((3002, 1708), (3256, 2398)), 'World Cup': ((3034, 2132), (3180, 2371)),
    'First Ride': ((3525, 2141), (3367, 2333)), 'Boulder': ((1052, 2390), (973, 2641)),
    'Groove': ((3019, 1677), (2866, 1652)), "Patsy's": ((2834, 1693), (2984, 1701)),
    'Big Easy': ((1705, 1543), (1558, 1485)),
}
best = None
for flips in itertools.product((0, 1), repeat=len(names)):
    src, dst = [], []
    for nm, f in zip(names, flips):
        top, bot = MAP[nm]
        a, b = lifts[nm][0], lifts[nm][-1]
        if f:
            a, b = b, a
        src += [a, b]; dst += [bot, top]
    src, dst = np.array(src), np.array(dst, float)
    X = np.hstack([src, np.ones((len(src), 1))])
    M, *_ = np.linalg.lstsq(X, dst, rcond=None)
    r = np.linalg.norm(X @ M - dst, axis=1)
    if best is None or r.mean() < best[0]:
        best = (r.mean(), M, flips, r)
print('mean residual', round(best[0]), 'flips', best[2], [round(v) for v in best[3]])
M = best[1]
im = Image.open('/home/user/myskiruns/work/heavenly/main/map.png').convert('RGB').crop(box)
im = im.resize((int(im.width * zoom), int(im.height * zoom)))
dr = ImageDraw.Draw(im)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
def T(p):
    q = np.append(p, 1) @ M
    return ((q[0] - box[0]) * zoom, (q[1] - box[1]) * zoom)
cols = [(255, 0, 255), (255, 120, 0), (0, 200, 255), (255, 255, 0), (0, 255, 0), (255, 60, 60)]
k = 0
for e in d['elements']:
    t = e.get('tags', {})
    if e['type'] != 'way':
        continue
    pts = [T(m(g['lat'], g['lon'])) for g in e['geometry']]
    if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in pts):
        continue
    if 'aerialway' in t:
        dr.line(pts, fill=(255, 255, 255), width=1)
        continue
    if t.get('piste:type') != 'downhill':
        continue
    c = cols[k % len(cols)]; k += 1
    dr.line(pts, fill=c, width=3)
    nm = t.get('name', '') or f'({e["id"]})'
    mid = pts[len(pts) // 2]
    dr.text((mid[0] + 3, mid[1]), nm, fill=c, font=F, stroke_width=2, stroke_fill=(0, 0, 0))
    dr.ellipse((pts[0][0] - 4, pts[0][1] - 4, pts[0][0] + 4, pts[0][1] + 4), outline=c, width=2)
im.save(out)
print(out, im.size)
