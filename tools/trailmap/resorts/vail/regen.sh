#!/bin/bash
# Vail: rebuild the app data (src/data/resorts/vail/) from the readings (names.py) and the naming decisions
# (decisions.py). Run from anywhere; working files go to $VAIL_WORK (default work/vail, git-ignored).
#
#   tools/trailmap/resorts/vail/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/vail/regen.sh   # also rewrite public/maps/vail-<panel>.jpg
#   FRESH=1 ...                                     # re-run line and symbol detection (cached otherwise)
#
# Human decisions in panels/<panel>/trailReviews.json are kept; Claude's ("by": "claude") are rebuilt from the
# traces, keeping their timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap; V=$T/resorts/vail
export VAIL_WORK=${VAIL_WORK:-$PWD/work/vail}; W=$VAIL_WORK
mkdir -p "$W"
PANELS="front-side back-bowls blue-sky"

# 1. the three panels from Vail's image CDN (plain curl works; vail.com pages need headless Chromium)
for p in $PANELS; do
  [ -f "$W/$p.png" ] || curl -sSf -o "$W/$p.png" \
    "https://scene7.vailresorts.com/is/image/vailresorts/20251001_VL_winter-$p-trail_map_001?fmt=png-alpha&wid=4990&qlt=100"
done

# 2. line pieces and symbols. --exclude blanks the legend, info boxes, the Game Creek inset's frame, logos and
# the header band; --k scales mark sizes (Back Bowls and Blue Sky are drawn bigger).
declare -A LINES SYMS
LINES[front-side]="--k 1 --text-max 36 --exclude 0,0,4990,70 --exclude 60,2085,1260,2594 --exclude 690,1935,1236,2055
  --exclude 1260,2100,1608,2594 --exclude 4335,876,4734,1008 --exclude 2100,2295,3000,2430 --exclude 4350,2145,4740,2310
  --exclude 3294,114,3900,204 --exclude 3600,2280,4990,2594 --exclude 3120,430,3250,660 --exclude 500,290,780,440
  --exclude 2875,280,3150,360 --exclude 3180,40,3262,700 --exclude 3180,684,4990,704 --exclude 4935,40,4990,704
  --exclude 3540,480,3740,540 --exclude 4330,870,4745,1020 --exclude 685,1925,1245,2060 --exclude 2210,1450,2390,1500"
LINES[back-bowls]="--k 1.75 --text-max 75 --exclude 0,0,4990,40 --exclude 1686,84,2295,330 --exclude 45,1620,990,1980"
LINES[blue-sky]="--k 2.7 --text-max 80 --exclude 0,0,4990,40 --exclude 105,2790,600,3180 --exclude 300,1100,1110,1300
  --exclude 1100,600,1700,760 --exclude 1720,830,2250,1000 --exclude 4500,1180,5000,1320 --exclude 4800,2620,4990,2900
  --exclude 4000,2780,4500,3050"
SYMS[front-side]="--size 13,24 --double-area 150,330 --exclude 0,2050,1700,2594 --exclude 3600,2250,4990,2594 --exclude 4335,876,4734,1008"
SYMS[back-bowls]="--size 19,30 --double-area 240,560 --exclude 45,1620,990,1980"
SYMS[blue-sky]="--size 40,62 --double-area 1150,2700 --exclude 105,2790,600,3180"
for p in $PANELS; do
  if [ -n "$FRESH" ] || [ ! -f "$W/lines_$p.json" ]; then
    python3 $T/raster_lines.py --image "$W/$p.png" --out "$W/lines_$p.json" ${LINES[$p]}
  fi
  if [ -n "$FRESH" ] || [ ! -f "$W/syms_$p.json" ]; then
    python3 $T/raster_symbols.py --image "$W/$p.png" --out "$W/syms_$p.json" ${SYMS[$p]}
  fi
done

# 3. each piece's name (auto-match + decisions), then the per-panel readings
python3 $V/build.py
python3 $V/reading.py | grep -v '(no name printed)'
[ -n "$IMAGES" ] && python3 $V/images.py

# 4. the trail list (one for all panels) with its header
python3 $T/seed_roster.py --readings "$W/tiles/result_*.json" \
  --areas 'front-side=Front Side=11250,back-bowls=Back Bowls=11455,blue-sky=Blue Sky Basin=11570' \
  --trails src/data/resorts/vail/trails.ts --labels "$W/labels.json" > "$W/seed.log"; head -1 "$W/seed.log"
python3 - <<PY
f = 'src/data/resorts/vail/trails.ts'
s = open(f).read()
old = s[s.index('// Seeded'):s.index('export const peaks')]
open(f, 'w').write(s.replace(old, open('$V/header.txt').read()))
PY

# 5. per panel: pieces, proposals, Claude's reviews (stretches are pieces; markers for names with no line), paths
for p in $PANELS; do
  D=src/data/resorts/vail/panels/$p
  mkdir -p $D
  cp "$W/linePolylines_$p.json" $D/linePolylines.json
  python3 $T/aggregate_readings.py --tiles "$W/tiles_$p" --readings "$W/tiles/result_$p.json" \
    --roster src/data/resorts/vail/trails.ts --polylines $D/linePolylines.json --proposals $D/trailProposals.json \
    --review-data "$W/review_$p.json" --labels "$W/labels_$p.json" | tail -1
  python3 - $D/trailReviews.json "$W/claude_reviews_$p.json" <<'PY'
import json, os, sys
f, keep = sys.argv[1], sys.argv[2]
d = json.load(open(f)) if os.path.exists(f) else {'reviews': {}}
json.dump({k: v for k, v in d['reviews'].items() if v.get('by') == 'claude'}, open(keep, 'w'))
d['reviews'] = {k: v for k, v in d['reviews'].items() if v.get('by') != 'claude'}  # human decisions stay
json.dump(d, open(f, 'w'), indent=1)
PY
  rm -f "$W/recheck_$p.json"
  python3 $T/traces_to_reviews.py --traces "$W/trace_$p.json" --reviews $D/trailReviews.json \
    --recheck "$W/recheck_$p.json" --labels "$W/labels_$p.json" --image "$W/$p.png" | cut -c1-60
  python3 - $D/trailReviews.json "$W/claude_reviews_$p.json" <<'PY'
import json, sys
f, old = sys.argv[1], json.load(open(sys.argv[2]))
d = json.load(open(f))
for k, v in d['reviews'].items():  # unchanged decisions keep their timestamp
    o = old.get(k)
    if v.get('by') == 'claude' and o and {**o, 'at': None} == {**v, 'at': None}:
        v['at'] = o['at']
json.dump(d, open(f, 'w'), indent=1)
PY
  npm run -s trails:apply -- --resort vail --panel $p
done
