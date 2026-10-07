#!/bin/bash
# crop.sh name x0,y0,x1,y1 zoom [ids...]  -> crop with only given pieces (or all if 'all', or none if none given)
S=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/answers/scratch_rA_3
name=$1; box=$2; zoom=$3; shift 3
if [ $# -eq 0 ]; then
  python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image /home/user/myskiruns/work/whistler-blackcomb/main/map.png --box $box --zoom $zoom --grid 50 --out $S/$name.png
elif [ "$1" == "all" ]; then
  python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image /home/user/myskiruns/work/whistler-blackcomb/main/map.png --box $box --zoom $zoom --grid 50 --out $S/$name.png --pieces /home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json --names /home/user/myskiruns/work/whistler-blackcomb/main/names.json
else
  python3 - "$S/sel_$name.json" "$@" <<'PY'
import json, sys
P = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))
ids = set(int(x) for x in sys.argv[2:])
P['polylines'] = [p for p in P['polylines'] if p['id'] in ids]
json.dump(P, open(sys.argv[1], 'w'))
PY
  python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image /home/user/myskiruns/work/whistler-blackcomb/main/map.png --box $box --zoom $zoom --grid 50 --out $S/$name.png --pieces $S/sel_$name.json --names /home/user/myskiruns/work/whistler-blackcomb/main/names.json
fi
echo $S/$name.png
