"""OSM runs drawn on the main map through a thin-plate-spline warp fitted on the lifts' end stations (each lift's
direction picked to agree with a robust affine fit). osmwarp.py OUT x0,y0,x1,y1 zoom [name filter substrings...]"""
import json, math, sys, itertools
import numpy as np
from scipy.interpolate import RBFInterpolator
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad'
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
    'Groove': ((3019, 1677), (2866, 1652)), "Patsy's": ((2984, 1701), (2834, 1693)),
    'Big Easy': ((1705, 1543), (1558, 1485)),
}
names = list(MAP)
def fit(pairs):
    X = np.array([p for p, q in pairs]); Y = np.array([q for p, q in pairs], float)
    Xh = np.hstack([X, np.ones((len(X), 1))])
    M, *_ = np.linalg.lstsq(Xh, Y, rcond=None)
    return M, np.linalg.norm(Xh @ M - Y, axis=1)
# direction: start from the lifts whose way runs bottom -> top (checked: Gunbarrel, Tram), iterate
flip = {n: 0 for n in names}
for it in range(6):
    pairs = []
    for n in names:
        top, bot = MAP[n]
        a, b = lifts[n][0], lifts[n][-1]
        if flip[n]:
            a, b = b, a
        pairs += [(a, bot), (b, top)]
    M, r = fit(pairs)
    # re-pick each lift's direction under M
    for n in names:
        top, bot = MAP[n]
        a, b = lifts[n][0], lifts[n][-1]
        P = lambda p: np.append(p, 1) @ M  # noqa: E731
        e0 = np.linalg.norm(P(a) - bot) + np.linalg.norm(P(b) - top)
        e1 = np.linalg.norm(P(b) - bot) + np.linalg.norm(P(a) - top)
        flip[n] = int(e1 < e0)
pairs = []
for n in names:
    top, bot = MAP[n]
    a, b = lifts[n][0], lifts[n][-1]
    if flip[n]:
        a, b = b, a
    pairs += [(a, bot), (b, top)]
M, r = fit(pairs)
if __name__ == '__main__' and len(sys.argv) < 2:
    print('affine residuals', [round(v) for v in r], 'median', np.median(r))
X = np.array([p for p, q in pairs]); Y = np.array([q for p, q in pairs], float)
o = X.mean(0)
tps = RBFInterpolator(X - o, Y, kernel='thin_plate_spline', smoothing=1.0)
def warp(pts):
    return tps(np.array(pts) - o)
if __name__ == '__main__' and len(sys.argv) >= 4:
    out, box, zoom = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], float(sys.argv[3])
    filt = sys.argv[4:]
    im = Image.open('/home/user/myskiruns/work/heavenly/main/map.png').convert('RGB').crop(box)
    im = im.resize((int(im.width * zoom), int(im.height * zoom)))
    dr = ImageDraw.Draw(im)
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
    cols = [(255, 0, 255), (255, 120, 0), (0, 220, 255), (255, 255, 0), (0, 255, 0), (255, 60, 60), (160, 100, 255)]
    k = 0
    for e in d['elements']:
        t = e.get('tags', {})
        if e['type'] != 'way' or t.get('piste:type') != 'downhill':
            continue
        nm = t.get('name', '') or f'({e["id"]})'
        if filt and not any(f.lower() in nm.lower() for f in filt):
            continue
        W = warp([m(g['lat'], g['lon']) for g in e['geometry']])
        pts = [((x - box[0]) * zoom, (y - box[1]) * zoom) for x, y in W]
        if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in pts):
            continue
        c = cols[k % len(cols)]; k += 1
        dr.line(pts, fill=c, width=3)
        mid = pts[len(pts) // 2]
        dr.text((mid[0] + 4, mid[1]), nm, fill=c, font=F, stroke_width=2, stroke_fill=(0, 0, 0))
        dr.ellipse((pts[0][0] - 5, pts[0][1] - 5, pts[0][0] + 5, pts[0][1] + 5), outline=c, width=2)
    im.save(out)
    print(out, im.size)
