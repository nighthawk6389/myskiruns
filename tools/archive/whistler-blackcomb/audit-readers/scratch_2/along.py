import json,sys,math
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
# usage: along.py panel piece_id|x,y;x,y;... [step]
panel=sys.argv[1]; spec=sys.argv[2]; step=float(sys.argv[3]) if len(sys.argv)>3 else 4
sizes={'main':(4320,2103),'symphony':(1704,1022),'glacier':(1114,1008)}
W,H=sizes[panel]
im=Image.open(f'/home/user/myskiruns/work/whistler-blackcomb/{panel}/map.png').convert('RGB'); px=im.load()
if ';' in spec or ',' in spec:
    pts=[tuple(map(float,p.split(','))) for p in spec.split(';')]
else:
    P=json.load(open(f'/home/user/myskiruns/work/whistler-blackcomb/{panel}/pieces_cut.json'))['polylines']
    p=[q for q in P if str(q['id'])==spec][0]
    pts=[(a*W/100,b*H/100) for a,b in p['points']]
def cls(c):
    r,g,b=c
    if r>200 and g<80 and b<80: return 'R'
    if g>120 and r<90 and b<120 and g>r+40: return 'G'
    if b>150 and r<100 and b>g+15: return 'B'
    if b>90 and r<60 and g<80: return 'N'
    if r<70 and g<70 and b<70: return 'K'
    if r>225 and g>225 and b>225: return 'w'
    if r>200 and g>200 and b<120: return 'Y'
    if r>200 and 100<g<190 and b<80: return 'O'
    if r>100 and b>120 and g<90: return 'P'
    return '.'
out=[]
for i in range(len(pts)-1):
    (x0,y0),(x1,y1)=pts[i],pts[i+1]
    L=math.hypot(x1-x0,y1-y0); n=max(1,int(L/step))
    for k in range(n):
        x=x0+(x1-x0)*k/n; y=y0+(y1-y0)*k/n
        # best class within radius 2
        best=[]
        for dx in range(-2,3):
            for dy in range(-2,3):
                xx,yy=int(round(x+dx)),int(round(y+dy))
                if 0<=xx<W and 0<=yy<H: best.append(cls(px[xx,yy]))
        s=''.join(sorted(set(best)))
        out.append(f'({int(x)},{int(y)}):{s}')
print(' '.join(out))
