#!/bin/bash
# pair.sh RID x0,y0,x1,y1 zoom out.png : plain crop | crop with pieces and names, side by side
set -e
cd /home/user/myskiruns
RID=$1; BOX=$2; Z=$3; OUT=$4
T=$(mktemp -d)
python3 tools/trailmap/grid_crop.py --image work/$RID/map.png --box $BOX --zoom $Z --out $T/a.png --grid 50 >/dev/null
python3 tools/trailmap/grid_crop.py --image work/$RID/map.png --box $BOX --zoom $Z --out $T/b.png --grid 50 --pieces work/$RID/pieces_cut.json --names work/$RID/names.json >/dev/null
python3 -c "
from PIL import Image
a=Image.open('$T/a.png'); b=Image.open('$T/b.png')
im=Image.new('RGB',(a.width+b.width+10,a.height),'white'); im.paste(a,(0,0)); im.paste(b,(a.width+10,0)); im.save('$OUT')
print('$OUT', im.size)"
rm -rf "${T:?}"
