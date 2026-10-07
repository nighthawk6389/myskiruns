#!/bin/bash
# Vail: rebuild reading -> roster -> per-panel proposals -> reviews -> trailPaths from the scratch decisions.
set -e
B=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/vail
R=/home/user/myskiruns
cd $B
for p in front-side back-bowls blue-sky; do python3 vl_build.py $p > /dev/null; done
python3 vl_reading.py | tail -3
cd $R
python3 tools/trailmap/seed_roster.py --readings "$B/tiles/result_*.json" \
  --areas 'front-side=Front Side=11250,back-bowls=Back Bowls=11455,blue-sky=Blue Sky Basin=11570' \
  --trails src/data/resorts/vail/trails.ts --labels $B/labels.json > $B/seed.log; head -1 $B/seed.log; tail -1 $B/seed.log
python3 - <<PY
f = 'src/data/resorts/vail/trails.ts'
s = open(f).read()
old = s[s.index('// Seeded'):s.index('export const peaks')]
open(f, 'w').write(s.replace(old, open('$B/vl_header.txt').read()))
PY
for p in front-side back-bowls blue-sky; do
  D=src/data/resorts/vail/panels/$p
  cp $B/linePolylines_$p.json $D/linePolylines.json
  python3 tools/trailmap/aggregate_readings.py --tiles $B/tiles_$p --readings "$B/tiles/result_$p.json" \
    --roster src/data/resorts/vail/trails.ts --polylines $D/linePolylines.json --proposals $D/trailProposals.json \
    --review-data $B/review_$p.json --labels $B/labels_$p.json | tail -1
  rm -f $D/trailReviews.json $B/recheck_$p.json
  python3 tools/trailmap/traces_to_reviews.py --traces $B/trace_$p.json --reviews $D/trailReviews.json \
    --recheck $B/recheck_$p.json --labels $B/labels_$p.json --image $B/$p.png | tail -1 | cut -c1-40
  npm run -s trails:apply -- --resort vail --panel $p
done
