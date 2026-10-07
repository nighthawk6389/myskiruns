#!/bin/bash
# usage: crop.sh name x0,y0,x1,y1 zoom [ids...]  (ids empty = all pieces; "none" = no pieces)
S=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/answers/scratch_rB_0
name=$1; box=$2; zoom=$3; shift 3
if [ "$1" == "none" ]; then
  python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image /home/user/myskiruns/work/whistler-blackcomb/main/map.png --box $box --zoom $zoom --grid 50 --out $S/$name.png
elif [ -z "$1" ]; then
  python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image /home/user/myskiruns/work/whistler-blackcomb/main/map.png --box $box --zoom $zoom --grid 50 --pieces /home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json --names /home/user/myskiruns/work/whistler-blackcomb/main/names.json --out $S/$name.png
else
  python3 - "$S/sel_$name.json" "$@" <<'PY'
import json, sys
P = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))
ids = set(int(x) for x in sys.argv[2:])
json.dump({'polylines': [p for p in P['polylines'] if p['id'] in ids]}, open(sys.argv[1], 'w'))
PY
  python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image /home/user/myskiruns/work/whistler-blackcomb/main/map.png --box $box --zoom $zoom --grid 50 --pieces $S/sel_$name.json --names /home/user/myskiruns/work/whistler-blackcomb/main/names.json --out $S/$name.png
fi
