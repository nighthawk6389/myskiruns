#!/bin/bash
# usage: crop.sh name x0,y0,x1,y1 [zoom]
S=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/answers/scratch_rB_3; M=/home/user/myskiruns/work/whistler-blackcomb/main
Z=${3:-3}
python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image $M/map.png --box $2 --zoom $Z --grid 50 --out $S/$1_plain.png >/dev/null
python3 /home/user/myskiruns/tools/trailmap/grid_crop.py --image $M/map.png --box $2 --zoom $Z --grid 50 --out $S/$1_pieces.png --pieces $M/pieces_cut.json --names $M/names.json >/dev/null
echo done $1
