#!/bin/bash
# Breckenridge: rebuild the app data (src/data/resorts/breckenridge/) from the 2025-26 trail-map PDF, the sharper
# copy of its painting on Vail Resorts' image CDN, and this folder's hand-made inputs: the pieces settled on crops
# (decisions.py), the trails.ts header (header.txt) and the map's reading in the scripts (symbols.py, names.py,
# match.py, reading.py, traces.py, matte.py). Run from anywhere; working files go to $BRECKENRIDGE_WORK (default
# work/breckenridge, git-ignored).
#
#   tools/trailmap/resorts/breckenridge/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/breckenridge/regen.sh   # also rewrite public/maps/breckenridge.jpg
#   FORCE=1 ...                                             # go on although a source's SHA-256 differs
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap; R=$T/resorts/breckenridge; D=src/data/resorts/breckenridge
export BRECKENRIDGE_WORK=${BRECKENRIDGE_WORK:-$PWD/work/breckenridge}; W=$BRECKENRIDGE_WORK
mkdir -p "$W" $D

# stop if a source is not the edition this folder was built from (a new season's map needs its pieces and names
# checked again: README.md, "A new season's map")
check() {
  local got; got=$(sha256sum "$1" | cut -d' ' -f1)
  [ "$got" = "$2" ] && return
  echo "$1: SHA-256 $got, expected $2 (the 2025-26 edition)." >&2
  if [ -z "$FORCE" ]; then
    echo "A different edition: see README.md, \"A new season's map\". To build from it anyway: FORCE=1 $0" >&2
    exit 1
  fi
  echo "FORCE=1: going on with it." >&2
}

# 1. sources (a copy placed in $W by hand is used as it is, after the same check)
#  - the PDF: breckenridge.com returns an error page to curl, so it is fetched from inside its trail-map page in
#    headless Chromium (fetch_pdf.cjs; behind this sandbox's agent proxy it works out the proxy CA's pin). The
#    same file is skimap.org's map 39900 (https://skimap.org/skimaps/view/39900).
[ -f "$W/breckenridge.pdf" ] || PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-$(npm root -g)/playwright} node $T/fetch_pdf.cjs \
  https://www.breckenridge.com/the-mountain/about-the-mountain/trail-map.aspx \
  https://www.breckenridge.com/-/aemasset/sitecore/breckenridge/maps/winter-2025-2026/20250926_BR_winter-trail_map_001.pdf \
  "$W/breckenridge.pdf"
check "$W/breckenridge.pdf" cb6793d2aff7f98bae1049eb6d35ec4d1da898fd8012432cbf9cb1c44cdbe31c
#  - the painting, from Vail Resorts' image CDN (scene7; plain curl works): its full size, 3037x2166
#    (?req=imageprops), as the CDN's JPEG
if [ ! -f "$W/scene7.jpg" ]; then
  curl -sSf -A 'Mozilla/5.0' -o "$W/scene7.jpg.part" \
    "https://scene7.vailresorts.com/is/image/vailresorts/20250926_BR_winter-trail_map_001?wid=3037&hei=2166&fit=constrain,1&qlt=95"
  mv "$W/scene7.jpg.part" "$W/scene7.jpg"
fi
check "$W/scene7.jpg" 13bf2b96ce88ffee81b16f99e44a8a72b74757cf75b4d16854e8a31fa999fa5e

# 2. the names (PDF text) and the symbols (PDF fills), in PDF points
python3 $T/pdf_labels.py "$W/breckenridge.pdf" --out "$W/printed.json" > /dev/null
python3 $R/symbols.py
python3 $R/names.py > "$W/names.log"; head -1 "$W/names.log"

# 3. the line pieces: the 0.99 pt green, blue and black strokes (solid, and dashed for catwalks) on the map clip at
#    3 px/pt, except inside the legend, lift-stats, Epic and emergency panels printed on the map; then piece 250
#    cut where Lowest 4 O'Clock leaves it, and the connectors with no printed name recorded (decisions.py)
python3 $T/extract_pdf_vectors.py "$W/breckenridge.pdf" --clip 0,80,1458,925 --scale 3 --color black=0,0,0 \
  --color blue=0.01,0.28,0.82 --color green=0.02,0.53,0.02 --min-width 0.95 --max-width 1.05 \
  --exclude 1326,400,1458,925 --exclude 1094,520,1326,925 --exclude 964,685,1086,915 --exclude 8,735,168,925 \
  --out "$W/pieces.json"
cp "$W/pieces.json" "$W/linePolylines.json"
python3 $T/split_pieces.py --polylines "$W/linePolylines.json" --image-size 4374x2535 \
  --split "250@1898.7,2028.3=Lower 4 O’Clock/Gondola Ski Back" --reading "$W/reading_splits.json"
#    then the lead-in stubs the first pass drops as under 4 pt (2.8 to 4 pt, drawn into or out of a label: Y-Chute,
#    Deja Vu, Stampede, Tom's Mom, Frosty's Freeway's two, Sawmill, King's Way), appended as pieces 352-359 so
#    every earlier id stays put
python3 $T/extract_pdf_vectors.py "$W/breckenridge.pdf" --clip 0,80,1458,925 --scale 3 --color black=0,0,0 \
  --color blue=0.01,0.28,0.82 --color green=0.02,0.53,0.02 --min-width 0.95 --max-width 1.05 \
  --exclude 1326,400,1458,925 --exclude 1094,520,1326,925 --exclude 964,685,1086,915 --exclude 8,735,168,925 \
  --min-length 2.5 --max-length 4 --append --out "$W/linePolylines.json" | cut -c1-60
python3 - "$W/linePolylines.json" $D/linePolylines.json <<'PY'
import json, sys
sys.path.insert(0, 'tools/trailmap/resorts/breckenridge')
from decisions import UNNAMED
d = json.load(open(sys.argv[1]))
d['_source'] = ("PDF vector strokes (tools/trailmap/extract_pdf_vectors.py): the 0.99 pt green, blue and black strokes "
                "of Breckenridge's 2025-26 map, solid and dashed (catwalks), outside the legend and stats panels; "
                "piece 250 cut where Lowest 4 O'Clock leaves it; the lead-in stubs under 4 pt appended as 352-359")
d['_unnamed'] = {str(k): v for k, v in sorted(UNNAMED.items())}
json.dump(d, open(sys.argv[2], 'w'))
PY

# 4. the map image: the vector layer matted over the scene7 painting (4374x2535, the pieces' grid)
if [ -n "$IMAGES" ] || [ ! -f "$W/map.png" ]; then
  python3 $R/matte.py ${IMAGES:+--jpg public/maps/breckenridge.jpg}
fi

# 5. each piece's name (match.py, then decisions.py), as a reading; stretches along names printed in a gap of
#    their line, and markers for names with no line
python3 $R/match.py > "$W/match.log"
python3 $R/reading.py | tail -3

# 6. the trail list (seed_roster.py) with its header
python3 $T/seed_roster.py --readings "$W/tiles/result_breck.json" --areas 'breckenridge=Breckenridge=13005' \
  --trails $D/trails.ts --labels "$W/labels.json" > "$W/seed.log"; head -1 "$W/seed.log"
python3 - $D/trails.ts $R/header.txt <<'PY'
import sys
f, header = sys.argv[1], open(sys.argv[2]).read()
s = open(f).read()
open(f, 'w').write(s.replace(s[s.index('// Seeded'):s.index('export const peaks')], header))
PY

# 7. proposals (aggregate_readings.py, which takes the image size from the tiles' index), Claude's reviews
#    (stretches and markers: traces.py, traces_to_reviews.py) and the overlays
python3 $T/render_tiles.py --image "$W/map.png" --polylines $D/linePolylines.json --out "$W/tiles" > /dev/null
python3 $T/aggregate_readings.py --tiles "$W/tiles" --readings "$W/tiles/result_*.json" --roster $D/trails.ts \
  --polylines $D/linePolylines.json --proposals $D/trailProposals.json --review-data "$W/review_data.json" \
  --labels "$W/labels.json" | tail -1
python3 $R/traces.py
rm -f "$W/recheck.json"
python3 $T/traces_to_reviews.py --replace-claude --traces "$W/trace_gaps.json" --reviews $D/trailReviews.json \
  --recheck "$W/recheck.json" --labels "$W/labels.json" --image "$W/map.png" | cut -c1-60
npm run -s trails:apply -- --resort breckenridge
