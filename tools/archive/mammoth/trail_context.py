"""trail_context.py <trail_id> <out.png> <margin_px> <scale> [x0 y0 x1 y1]: one trail's overlay (orange, its ends red) with every
other overlay (thin cyan) on public/maps/mammoth-main.jpg, cropped around it or to a box: a wider look at an
overlay_audit.py cell (the audit readers' helper; their other helpers did the same)."""
import sys, json
from PIL import Image, ImageDraw
R='/home/user/myskiruns/'
tid, out, margin, scale = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
im = Image.open(R+'public/maps/mammoth-main.jpg').convert('RGB')
W,H = im.size
d = json.load(open(R+'src/data/resorts/mammoth/panels/main/trailPaths.json'))['trails']
dr = ImageDraw.Draw(im)
def px(p): return (p[0]*W/100, p[1]*H/100)
for k,v in d.items():
    if k==tid: continue
    for s in v.get('segments',[]):
        pts=[px(p) for p in s]
        if len(pts)>1: dr.line(pts, fill=(0,200,230), width=1)
t = d[tid]
xs=[];ys=[]
for s in t.get('segments',[]):
    pts=[px(p) for p in s]; xs+= [p[0] for p in pts]; ys+=[p[1] for p in pts]
    if len(pts)>1: dr.line(pts, fill=(255,120,0), width=3)
    for e in (pts[0],pts[-1]): dr.ellipse((e[0]-3,e[1]-3,e[0]+3,e[1]+3), fill=(255,0,0))
print({k:v for k,v in t.items() if k!='segments'}, 'nseg', len(t.get('segments',[])))
if len(sys.argv)>5:
    box=tuple(map(int,sys.argv[5:9]))
else:
    box=(max(0,int(min(xs))-margin), max(0,int(min(ys))-margin), min(W,int(max(xs))+margin), min(H,int(max(ys))+margin))
print('box', box)
c = im.crop(box)
c = c.resize((int(c.width*scale), int(c.height*scale)), Image.LANCZOS)
c.save(out)
