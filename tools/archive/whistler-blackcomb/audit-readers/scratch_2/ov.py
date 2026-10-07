import json,sys
# usage: ov.py panel x0,y0,x1,y1 [trail-id to print fully]
panel=sys.argv[1]; x0,y0,x1,y1=map(float,sys.argv[2].split(','))
sizes={'main':(4320,2103),'symphony':(1704,1022),'glacier':(1114,1008)}
W,H=sizes[panel]
d=json.load(open(f'/home/user/myskiruns/src/data/resorts/whistler-blackcomb/panels/{panel}/trailPaths.json'))['trails']
full=set(sys.argv[3:])
for k,v in d.items():
    segs=[[(round(p[0]*W/100),round(p[1]*H/100)) for p in s] for s in v.get('segments',[])]
    hit=False
    for s in segs:
        # check points and interpolated points
        for i in range(len(s)):
            a=s[i]; b=s[i+1] if i+1<len(s) else s[i]
            for t in range(11):
                x=a[0]+(b[0]-a[0])*t/10; y=a[1]+(b[1]-a[1])*t/10
                if x0<=x<=x1 and y0<=y<=y1: hit=True;break
            if hit: break
        if hit: break
    extra={kk:vv for kk,vv in v.items() if kk not in('segments',)}
    if hit or k in full:
        print(k, extra)
        for s in segs:
            print('   seg', len(s), s if (k in full or len(s)<=60) else s[:5]+['...']+s[-5:])
