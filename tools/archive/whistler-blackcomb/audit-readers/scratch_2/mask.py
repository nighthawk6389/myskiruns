import json,sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
# usage: mask.py panel x0,y0,x1,y1 zoom out.png colorclass piece_ids...
panel=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2].split(',')); z=float(sys.argv[3]); out=sys.argv[4]; cc=sys.argv[5]; ids=sys.argv[6:]
sizes={'main':(4320,2103),'symphony':(1704,1022),'glacier':(1114,1008)}
W,H=sizes[panel]
im=Image.open(f'/home/user/myskiruns/work/whistler-blackcomb/{panel}/map.png').convert('RGB').crop((x0,y0,x1,y1))
px=im.load()
def ok(c):
    r,g,b=c
    if cc=='B': return b>150 and r<110 and b>g+15
    if cc=='G': return g>110 and r<100 and g>r+40 and g>b+10
    if cc=='K': return r<80 and g<80 and b<90
    if cc=='P': return r>90 and b>110 and g<90
    return False
m=Image.new('RGB',im.size,(255,255,255)); mp=m.load()
for y in range(im.size[1]):
    for x in range(im.size[0]):
        c=px[x,y]
        if ok(c): mp[x,y]=(0,0,0)
        elif c[0]>225 and c[1]>225 and c[2]>225: mp[x,y]=(235,235,235)
        else: mp[x,y]=(255,255,255)
m=m.resize((int(m.size[0]*z),int(m.size[1]*z)),Image.NEAREST)
d=ImageDraw.Draw(m)
P=json.load(open(f'/home/user/myskiruns/work/whistler-blackcomb/{panel}/pieces_cut.json'))['polylines']
cols=[(255,0,0),(0,160,255),(0,170,0),(255,140,0),(200,0,200),(0,200,200),(120,80,0)]
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',12)
for i,pid in enumerate(ids):
    p=[q for q in P if str(q['id'])==pid][0]
    pts=[((a*W/100-x0)*z,(b*H/100-y0)*z) for a,b in p['points']]
    d.line(pts,fill=cols[i%len(cols)],width=1)
    d.text(pts[len(pts)//2],pid,fill=cols[i%len(cols)],font=f)
# grid
for gx in range((x0//10+1)*10,x1,10):
    X=(gx-x0)*z; d.line((X,0,X,4),fill=(255,0,255))
    if gx%50==0: d.text((X+1,5),str(gx),fill=(200,0,200),font=f)
for gy in range((y0//10+1)*10,y1,10):
    Y=(gy-y0)*z; d.line((0,Y,4,Y),fill=(255,0,255))
    if gy%50==0: d.text((5,Y+1),str(gy),fill=(200,0,200),font=f)
m.save(out); print(out,m.size)
