#!/bin/bash
# Re-render every crop and sheet decisions.py cites, and the final overlay audit, into $BRECKENRIDGE_WORK (default
# work/breckenridge): the commands of the 2026-10-01 session, in order. Run regen.sh first (it fills the work folder).
#
#   tools/trailmap/resorts/breckenridge/checks/crops.sh
#
# reg/<name>_<k>.jpg: zoom.py, pieces tagged id:auto-name (boxes.txt is the first pass over the map, prob_boxes.txt
# the windows round the pieces match.py left unnamed or doubly named, as of the first match); f_*.png: fine.py, the
# listed pieces numbered at both ends; c_*.png: crop.py, the PDF alone; nosym*.jpg, sym_*.jpg: label sheets; audit/:
# region_audit.py, every overlay on the map image. The zoom tags and the map image are today's (then: the first
# match's names, and the PDF render before the matte), so a few tags read differently from the cited crops.
set -e
cd "$(dirname "$0")/../../../../.."
C=tools/trailmap/resorts/breckenridge/checks
export BRECKENRIDGE_WORK=${BRECKENRIDGE_WORK:-$PWD/work/breckenridge}; W=$BRECKENRIDGE_WORK
mkdir -p "$W/reg"
z() { Z=$1 python3 $C/zoom.py "$W/reg/$2" "${@:3}" > /dev/null; }
fine() { python3 $C/fine.py "$W/$1" "${@:2}" > /dev/null; }
crop() { python3 $C/crop.py "$W/$1" "${@:2}" > /dev/null; }

crop legend.png 1320,390,1458,640 5
crop c_p6chutes.png 1080,170,1270,260 5
crop c_p8bowl.png 600,280,760,380 5
python3 $C/sheet.py "$W/nosym.jpg" @nosym > /dev/null
crop c_p6zones.png 1070,165,1290,285 4.5
z 1.4 g $(cat $C/boxes.txt)
crop c_p10.png 10,370,200,620 4.2
z 2.6 p10 10,370,200,620
z 3 z_corsair 180,330,290,440
z 3 z_sizzler 270,320,400,420
z 2.3 pb $(cat $C/prob_boxes.txt)
crop c_chutes9.png 470,240,600,345 6.5
z 4 zz_chutes9 470,240,600,345
crop c_echair.png 360,340,520,470 6
z 4.2 zz_echair 375,370,510,460
fine f_echair.png 375,335,500,450 7 76 75 67 78 77 274 74 72 73 69 71 68 70 79
fine f_pb7.png 730,350,930,480 5 350 231 232 257 256 258 265 261 224 225 53 54
fine f_cuke.png 700,300,840,500 5 350 342 265 258 262
z 1.7 z_p9mid 330,480,480,700
fine f_114.png 395,455,475,515 8 114 119 127 113 117
fine f_lsund.png 300,700,380,800 6
crop c_boxes.png 1060,500,1340,600 3
z 1.6 q 170,560,370,760 240,680,420,880 420,600,560,720 560,580,740,820 840,520,1040,640 490,420,560,490 340,290,420,350
fine f_p9base_a.png 170,580,300,760 5 155 157 161 162 160 159 158 167 151 166 168 169 154 163
fine f_p9base_b.png 280,560,380,760 5 153 152 154 145 170 172 137 136 3 171 146 164 165 167 151 166
fine f_snow.png 425,650,545,760 5 235 271 272 233 250 254
fine f_p8base.png 640,560,740,640 7 0 270 243 244 238 239 241 242 237 236
fine f_wire.png 920,440,1030,630 4 219 220 221 215 213 214 216 217 218
fine f_rdv.png 480,400,600,500 6 31 30 35 36 33 32 29 16
fine f_140.png 180,560,240,610 8 140 141
crop c_kids.png 200,610,260,700 6
z 1.3 bc 840,250,960,340
crop c_bc.png 840,250,960,340 6
fine f_swing.png 575,440,720,560 6 236 237 238 239 240 241 242 268 269
fine f_cresc.png 600,430,770,640 4.5 266 267 268 269 240 236
crop c_vista.png 560,375,660,500 6
fine f_vista.png 560,375,660,500 6 240 269 275 276 237 239
crop c_cashier.png 270,540,370,700 6
python3 $C/symsheet.py double-black "$W/sym_dbl.jpg" > /dev/null
python3 $C/symsheet.py black "$W/sym_blk.jpg" > /dev/null

# the overlay audit: every trail's overlay in its own colour, tagged with its name (the playbook's Part 4)
rm -rf "$W/audit"
python3 tools/trailmap/region_audit.py --image "$W/map.png" --paths src/data/resorts/breckenridge/trailPaths.json \
  --trails src/data/resorts/breckenridge/trails.ts --out "$W/audit" --zoom 1.4 --grid 6x4 --area 0,330,4374,2535 > /dev/null
echo "crops in $W (reg/, f_*.png, c_*.png, nosym.jpg, sym_*.jpg) and the audit in $W/audit"
