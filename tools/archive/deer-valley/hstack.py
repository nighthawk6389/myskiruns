import sys
from PIL import Image
ims=[Image.open(f) for f in sys.argv[2:]]
W=sum(i.width for i in ims)+10*(len(ims)-1); H=max(i.height for i in ims)
o=Image.new('RGB',(W,H),'white'); x=0
for i in ims: o.paste(i,(x,0)); x+=i.width+10
o.save(sys.argv[1])
