#!/bin/bash
# Re-render, into $WINTER_PARK_WORK (default work/winter-park; run regen.sh first), the crops Winter Park's piece
# names were settled on and the audit sheets every overlay was checked on, with the boxes the 2026-10-01 session
# used (zoom.py and crop.py take PDF points; region_audit.py map-image px, 3.2 px/pt from 40,165).
#
#   tools/trailmap/resorts/winter-park/checks/crops.sh      # about a minute
set -e
cd "$(dirname "$0")/../../../../.."
C=tools/trailmap/resorts/winter-park/checks; D=src/data/resorts/winter-park
export WINTER_PARK_WORK=${WINTER_PARK_WORK:-$PWD/work/winter-park}; W=$WINTER_PARK_WORK

# 1. the whole map in 18 tiles, every piece tagged id:auto-name (reg/r_*.jpg; reg/s_*.jpg repeats the lower nine),
#    then the closer crops of doubtful spots (reg/chutes_0.jpg, reg/z1_0.jpg ... z11_0.jpg)
python3 $C/zoom.py reg/r 140,220,410,425 370,220,650,425 610,220,890,425 850,220,1190,440 140,400,410,600 \
  370,400,650,600 610,380,900,600 860,380,1180,600 140,570,410,790 370,570,650,790 610,570,900,790 870,570,1210,800 \
  360,760,650,970 610,760,900,970 870,760,1230,960 320,930,610,1140 570,930,870,1140 830,900,1110,1080
python3 $C/zoom.py reg/s 370,570,650,790 610,570,900,790 870,570,1210,800 360,760,650,970 610,760,900,970 \
  870,760,1230,960 320,930,610,1140 570,930,870,1140 830,900,1110,1080
Z=2.6 python3 $C/zoom.py reg/chutes 335,505,425,590
Z=2.2 python3 $C/zoom.py reg/z1 470,500,640,700
Z=2.6 python3 $C/zoom.py reg/z2 395,500,470,640
Z=2.4 python3 $C/zoom.py reg/z3 700,700,800,790
Z=2.0 python3 $C/zoom.py reg/z4 840,590,960,720
Z=2.2 python3 $C/zoom.py reg/z5 340,650,450,840
Z=2.6 python3 $C/zoom.py reg/z6 880,765,1010,850
Z=2.6 python3 $C/zoom.py reg/z7 720,640,860,750
Z=1.9 python3 $C/zoom.py reg/z8 585,560,720,820
Z=2.4 python3 $C/zoom.py reg/z9 815,380,935,470
Z=1.6 python3 $C/zoom.py reg/z10 700,960,1020,1110
Z=4 python3 $C/zoom.py reg/z11 375,505,420,560

# 2. the same spots straight from the PDF, sharper and with nothing drawn on (c_*.png)
python3 $C/crop.py c_chutes.png 330,500,420,585 6
python3 $C/crop.py c_bb1.png 870,670,990,800 4
python3 $C/crop.py c_bb3.png 180,540,250,600 6
python3 $C/crop.py c_mj.png 590,540,680,700 6
python3 $C/crop.py c_dash.png 885,690,985,800 6
python3 $C/crop.py c_mjlow.png 370,740,560,900 4
python3 $C/crop.py c_rail.png 760,740,900,980 4
python3 $C/crop.py c_mh.png 880,765,1010,850 6
python3 $C/crop.py c_bottom.png 470,1040,780,1130 4
python3 $C/crop.py c_vista.png 870,820,1010,900 5
python3 $C/crop.py c_legend.png 1410,0,1728,330 3

# 3. the audit: every overlay in its own colour, tagged with its name, over the map in 18 boxes (audit/) and along
#    the bottom (audz/: Village Way); then every double-black and black label with its symbol (sym_dbl.jpg,
#    sym_blk.jpg), captioned with the trail list's difficulty
rm -rf "$W/audit" "$W/audz"
python3 tools/trailmap/region_audit.py --image "$W/wp_source.png" --paths $D/trailPaths.json --trails $D/trails.ts \
  --out "$W/audit" --zoom 1.25 --box 320,176,1184,832 --box 1056,176,1952,832 --box 1824,176,2720,832 \
  --box 2592,176,3680,880 --box 320,752,1184,1392 --box 1056,752,1952,1392 --box 1824,688,2752,1392 \
  --box 2624,688,3648,1392 --box 320,1296,1184,2000 --box 1056,1296,1952,2000 --box 1824,1296,2752,2000 \
  --box 2656,1296,3744,2016 --box 1024,1904,1952,2576 --box 1824,1904,2752,2576 --box 2656,1904,3808,2544 \
  --box 896,2448,1824,3120 --box 1696,2448,2656,3120 --box 2528,2352,3424,2928 > /dev/null
python3 tools/trailmap/region_audit.py --image "$W/wp_source.png" --paths $D/trailPaths.json --trails $D/trails.ts \
  --out "$W/audz" --zoom 1.5 --box 1350,2850,2500,3152 > /dev/null
python3 $C/symsheet.py double-black sym_dbl.jpg
python3 $C/symsheet.py black sym_blk.jpg
echo "crops in $W: reg/, c_*.png, audit/, audz/, sym_*.jpg"
