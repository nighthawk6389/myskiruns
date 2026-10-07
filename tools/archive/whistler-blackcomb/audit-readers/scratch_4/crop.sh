#!/bin/bash
# usage: crop.sh PANEL x0,y0,x1,y1 ZOOM NAME [paths] [grid]
P=$1; B=$2; Z=$3; N=$4; W=$5; G=${6:-50}
S=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/sheets/scratch_4
R=/home/user/myskiruns
EXTRA=""
if [ "$W" = "paths" ]; then
  EXTRA="--paths $R/src/data/resorts/whistler-blackcomb/panels/$P/trailPaths.json --trails $R/src/data/resorts/whistler-blackcomb/trails.ts"
fi
python3 $R/tools/trailmap/grid_crop.py --image $R/work/whistler-blackcomb/$P/map.png --box $B --zoom $Z --grid $G $EXTRA --out $S/$N.png
