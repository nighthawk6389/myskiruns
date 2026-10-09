import json, numpy as np, cv2, sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
A=(1.3888948, 0.0000021, -27.5124, 0.0000022, 1.3888649, 573.8250)
nov=np.asarray(Image.open('work/deer-valley/src/nov4.png').convert('L'))
oc=np.asarray(Image.open('work/deer-valley/src/oct_on_nov.png').convert('L'))
d=json.load(open('work/deer-valley/printed.json'))
def px(p): return (A[0]*p[0]+A[1]*p[1]+A[2], A[3]*p[0]+A[4]*p[1]+A[5])
k=np.ones((3,3),np.uint8)
rows=[]
for l in d['labels']:
    P=[px(p) for p in l['pts']]
    xs=[p[0] for p in P]; ys=[p[1] for p in P]
    x0,y0,x1,y1=int(min(xs))-9,int(min(ys))-9,int(max(xs))+10,int(max(ys))+10
    a=nov[y0:y1,x0:x1]<100; b=oc[y0:y1,x0:x1]<100
    if b.sum()==0: continue
    da=cv2.dilate(a.astype(np.uint8),k).astype(bool); db=cv2.dilate(b.astype(np.uint8),k).astype(bool)
    miss=(b & ~da).sum()+(a & ~db).sum()
    rows.append((miss/max(1,(a|b).sum()), l['text'], l['seq'], (x0,y0,x1-x0,y1-y0)))
rows.sort(reverse=True)
for r in rows[:int(sys.argv[1])]: print(round(r[0],3), r[1], r[2], ','.join(map(str,r[3])))
