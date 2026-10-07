import json, math, sys
from PIL import Image, ImageDraw, ImageFont
F=[json.loads(l.strip().rstrip(',')) for l in open('okemo_runs.jsonl')]
lat0, lon0 = 43.405, -72.745
kx = 111320*math.cos(math.radians(lat0)); ky = 110540
# map-like frame: X = north (m), Y = east (m)
bbox = [float(v) for v in sys.argv[2:6]]  # Xmin Xmax Ymin Ymax in m
out = sys.argv[1]; S = float(sys.argv[6])
hl = sys.argv[7].split(',') if len(sys.argv) > 7 else []
Wd, Hd = int((bbox[1]-bbox[0])*S), int((bbox[3]-bbox[2])*S)
im = Image.new('RGB', (Wd, Hd), 'white'); d = ImageDraw.Draw(im)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
col = {'novice':(0,160,0),'easy':(0,160,0),'intermediate':(0,0,220),'advanced':(0,0,0),'expert':(0,0,0),'freeride':(255,120,0)}
for f in F:
    p = f['properties']; g = f['geometry']
    rings = [g['coordinates']] if g['type']=='LineString' else g['coordinates']
    for c in rings:
        pts = []
        for lon, lat, *_ in c:
            X = (lat-lat0)*ky; Y = (lon-lon0)*kx
            pts.append(((X-bbox[0])*S, (Y-bbox[2])*S))
        name = p.get('name') or ''
        w = 4 if name in hl else 2
        d.line(pts, fill=(255,0,0) if name in hl else col.get(p.get('difficulty'),(128,128,128)), width=w)
        if name:
            vis=[q for q in pts if 0<=q[0]<Wd and 0<=q[1]<Hd]
            if vis:
                m=vis[len(vis)//2]; d.text((m[0]+3,m[1]), name, fill=(200,0,0) if name in hl else (90,0,90), font=font)
im.save(out); print(out, im.size)
