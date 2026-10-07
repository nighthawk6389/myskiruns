#!/bin/bash
# usage: pair.sh PANEL NAME x0,y0,x1,y1 ZOOM [grid]  -> side-by-side plain | overlays
S=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/sheets/scratch_3
P=$1; N=$2; B=$3; Z=${4:-3}; G=${5:-25}
python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image /home/user/myskiruns/work/whistler-blackcomb/$P/map.png --box $B --zoom $Z --grid $G --out $S/_a.png >/dev/null
python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image /home/user/myskiruns/work/whistler-blackcomb/$P/map.png --box $B --zoom $Z --grid $G --paths /home/user/myskiruns/src/data/resorts/whistler-blackcomb/panels/$P/trailPaths.json --trails /home/user/myskiruns/src/data/resorts/whistler-blackcomb/trails.ts --out $S/_b.png >/dev/null
python3 - "$S/_a.png" "$S/_b.png" "$S/$N.png" <<'PY'
import sys
from PIL import Image
a=Image.open(sys.argv[1]); b=Image.open(sys.argv[2])
w=a.width+b.width+8; h=max(a.height,b.height)
im=Image.new('RGB',(w,h),(60,60,60)); im.paste(a,(0,0)); im.paste(b,(a.width+8,0)); im.save(sys.argv[3])
print(sys.argv[3], im.size)
PY
