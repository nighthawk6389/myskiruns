import numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
d=np.asarray(Image.open('work/deer-valley/src/diff.png'),np.uint8)//2*2
m=(d>=200).astype(np.uint8)
m=cv2.dilate(m,np.ones((9,9),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
rows=[]
for i in range(1,n):
    x,y,w,h,a=st[i]
    if y<700: continue
    if a<150: continue
    rows.append((a,x,y,w,h))
rows.sort(reverse=True)
print(len(rows))
for r in rows[:80]: print(r)
