import json,sys
# usage: pc.py panel x0,y0,x1,y1  -> list pieces (pieces_cut.json) crossing box, with assigned name (names.json)
panel=sys.argv[1]; x0,y0,x1,y1=map(float,sys.argv[2].split(','))
sizes={'main':(4320,2103),'symphony':(1704,1022),'glacier':(1114,1008)}
W,H=sizes[panel]
base=f'/home/user/myskiruns/work/whistler-blackcomb/{panel}/'
P=json.load(open(base+'pieces_cut.json'))['polylines']
names=json.load(open(base+'names.json'))
show=set(sys.argv[3:])
for p in P:
    pts=[(round(a*W/100),round(b*H/100)) for a,b in p['points']]
    if any(x0<=x<=x1 and y0<=y<=y1 for x,y in pts) or str(p['id']) in show:
        s=pts if (len(pts)<=14 or str(p['id']) in show) else pts[:6]+['...']+pts[-6:]
        print(p['id'], p['cls'], p.get('lengthPx'), repr(names.get(str(p['id']))), s)
