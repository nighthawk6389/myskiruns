import json,sys
panel=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2].split(','))
d=json.load(open(f'/home/user/myskiruns/work/whistler-blackcomb/{panel}/labels.json'))
for k,v in d.items():
    for p in v['positions']:
        if x0<=p[0]<=x1 and y0<=p[1]<=y1:
            print('LABEL',k, v['mapName'], p, v['symbols'], v['colors'])
info=json.load(open('/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/sheets/trails_info.json'))[panel]
for k,v in info.items():
    bb=v.get('overlay_bbox')
    if bb and not (bb[2]<x0 or bb[0]>x1 or bb[3]<y0 or bb[1]>y1):
        print('OVERLAY',k,v['name'],v['difficulty'],bb,[(p['from'],p['to']) for p in v['overlay_parts']])
    m=v.get('marker_at')
    if m and x0<=m[0]<=x1 and y0<=m[1]<=y1: print('MARKER',k,v['name'],m)
