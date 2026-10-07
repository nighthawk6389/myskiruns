#!/bin/bash
# usage: crop.sh PANEL NAME x0,y0,x1,y1 ZOOM [paths] [grid]
S=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/sheets/scratch_3
P=$1; N=$2; B=$3; Z=${4:-3}; WP=$5; G=${6:-50}
EXTRA=""
if [ "$WP" = "paths" ]; then
  EXTRA="--paths /home/user/myskiruns/src/data/resorts/whistler-blackcomb/panels/$P/trailPaths.json --trails /home/user/myskiruns/src/data/resorts/whistler-blackcomb/trails.ts"
fi
python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image /home/user/myskiruns/work/whistler-blackcomb/$P/map.png --box $B --zoom $Z --grid $G $EXTRA --out $S/$N.png
echo $S/$N.png
