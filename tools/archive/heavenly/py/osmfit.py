"""Fit OSM (lat/lon) -> main map px from lift end stations; save the fit; report residuals."""
import json, math, sys
import numpy as np, cv2
S = sys.argv[1]
d = json.load(open(f'{S}/hv/osm/hv.json'))
lifts = {e['tags']['name']: [(g['lat'], g['lon']) for g in e['geometry']] for e in d['elements']
         if e['type'] == 'way' and 'aerialway' in e.get('tags', {}) and e['tags'].get('name')}
MAP = {  # map px: (top, bottom)
    'Sky Express': ((2027, 428), (2266, 1511)), 'Canyon Express': ((2506, 687), (2362, 1547)),
    'Dipper Express': ((1098, 772), (1000, 1600)), 'Comet Express': ((1345, 1107), (1011, 1629)),
    'Tamarack Express': ((1431, 955), (1738, 1476)), 'Olympic Express': ((1539, 1517), (1081, 1989)),
    'Stagecoach Express': ((870, 1685), (632, 2556)), 'North Bowl Express': ((986, 1790), (983, 2392)),
    'Galaxy': ((828, 1384), (290, 2098)), 'Mott Canyon': ((805, 1096), (303, 1666)),
    'Powderbowl Express': ((2810, 1188), (2836, 1674)), 'Gunbarrel Express': ((3038, 1676), (3335, 2327)),
    'Aerial Tramway': ((3002, 1708), (3256, 2398)), 'World Cup': ((3034, 2132), (3180, 2371)),
    'First Ride': ((3525, 2141), (3367, 2333)), 'Boulder': ((1052, 2390), (973, 2641)),
}
lat0 = 38.93
def m(lat, lon):
    return (lon * math.cos(math.radians(lat0)) * 111320, -lat * 110540)
src, dst, tag = [], [], []
for nm, (top, bot) in MAP.items():
    g = lifts[nm]
    a, b = m(*g[0]), m(*g[-1])
    src += [a, b]; dst += [bot, top]; tag += [nm + ' first', nm + ' last']
src, dst = np.float64(src), np.float64(dst)
o = src.mean(0)
H, inl = cv2.findHomography(src - o, dst, cv2.RANSAC, 60)
pr = cv2.perspectiveTransform((src - o).reshape(-1, 1, 2), H).reshape(-1, 2)
res = np.linalg.norm(pr - dst, axis=1)
for t, r, i in zip(tag, res, inl.ravel()):
    print(f'{t:28s} {r:6.0f} {"" if i else "OUTLIER"}')
print('median', np.median(res), 'inliers', inl.sum(), '/', len(res))
json.dump({'H': H.tolist(), 'o': o.tolist(), 'lat0': lat0}, open(f'{S}/hv/osm/fit.json', 'w'))
