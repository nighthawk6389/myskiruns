#!/bin/bash
# usage: crop.sh x0,y0,x1,y1 zoom outname [ids...|all]
S=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/answers/scratch_rB_1
M=/home/user/myskiruns/work/whistler-blackcomb/main
box=$1; z=$2; out=$3; shift 3
if [ $# -eq 0 ]; then
  python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image $M/map.png --box $box --zoom $z --grid 50 --out $S/$out.png
elif [ "$1" == "all" ]; then
  python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image $M/map.png --box $box --zoom $z --grid 50 --pieces $M/pieces_cut.json --names $M/names.json --out $S/$out.png
else
  python3 - "$@" <<PY
import json,sys
d=json.load(open('$M/pieces_cut.json'))
ids=set(int(a) for a in sys.argv[1:])
d['polylines']=[p for p in d['polylines'] if p['id'] in ids]
json.dump(d,open('$S/_sel.json','w'))
PY
  python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image $M/map.png --box $box --zoom $z --grid 50 --pieces $S/_sel.json --names $M/names.json --out $S/$out.png
fi
echo $S/$out.png
