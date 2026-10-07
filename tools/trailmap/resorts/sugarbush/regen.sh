#!/bin/bash
# Sugarbush: rebuild the app data (src/data/resorts/sugarbush/) from the 2025-26 trail-map PDF, the five tile
# readers' readings (readings/) and the decisions taken on crops (decisions.py: three split pieces, two unnamed
# connectors; header.txt: the trails.ts header). Run from anywhere; working files go to $SUGARBUSH_WORK
# (default work/sugarbush, git-ignored).
#
#   tools/trailmap/resorts/sugarbush/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/sugarbush/regen.sh   # also rewrite public/maps/sugarbush.jpg
#   FORCE=1 ...                                          # go on with a PDF whose SHA-256 differs
#
# Sugarbush has no trailReviews.json: nobody reviewed it on the Trail Check page and no trail needed a traced
# stretch. A person's review added later (see the playbook, "To fix one trail") is read by trails:apply and
# kept: this script never writes that file.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap; R=$T/resorts/sugarbush; D=src/data/resorts/sugarbush
export SUGARBUSH_WORK=${SUGARBUSH_WORK:-$PWD/work/sugarbush}; W=$SUGARBUSH_WORK
mkdir -p "$W/tiles" "$D"

# 1. the PDF (plain curl works). The readings are of this edition: a different file (a new season's map) means
#    redoing the readers (README, "A new season's map").
URL=https://links.imagerelay.com/cdn/1980/ql/7d66b14e89414d4cb778d19f33660efc/2025-26-Sugarbush_Trail_Map.pdf
SHA=75452599716a0d2d616e94566a5bc476db185d3e28589a686bd081c7d53e0f50  # 15,554,442 bytes, fetched 2026-09-30
PDF=$W/sugarbush.pdf
if [ ! -f "$PDF" ]; then
  curl -sSfL -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36' \
    -o "$PDF.part" "$URL"
  mv "$PDF.part" "$PDF"
fi
GOT=$(sha256sum "$PDF" | cut -d' ' -f1)
if [ "$GOT" != "$SHA" ]; then
  echo "sugarbush.pdf is not the 2025-26 edition the readings are of (SHA-256 $GOT, expected $SHA)." >&2
  [ -n "$FORCE" ] || { echo "Re-read it (README, \"A new season's map\"), or FORCE=1 to go on anyway." >&2; exit 1; }
fi

# 2. the line pieces, all on the map image's grid (the whole page at 3.5 px/pt: 4333x2981):
#    0.75 pt strokes in the three trail colours (lifts and the boundary are red; Out Road is a green-filled path
#    with a blue stroke edge: --filled), then Lwr Exterminator and Black Diamond Rush (pure black) and Hi & Lo
#    Road (1.0 pt). Those 114 pieces are what the readers saw on their tiles.
GRID="--page 0 --clip 0,0,1237.77,851.46 --scale 3.5"
P=$W/linePolylines.json
IMG=; [ -n "$IMAGES" ] && IMG="--image public/maps/sugarbush.jpg"
python3 $T/extract_pdf_vectors.py "$PDF" $GRID --color blue=0.08,0.51,0.78 --color black=0.14,0.12,0.13 \
  --color green=0.08,0.65,0.32 --max-width 0.8 --filled $IMG --out "$P" | grep -v '^wrote.*jpg'
python3 $T/extract_pdf_vectors.py "$PDF" $GRID --color black=0.0,0.0,0.0 --max-width 0.8 --append --out "$P" > /dev/null
python3 $T/extract_pdf_vectors.py "$PDF" $GRID --color black=0.14,0.12,0.13 --min-width 0.9 --max-width 1.1 \
  --append --out "$P" > /dev/null
python3 - "$PDF" "$W/sugarbush_source.png" <<'PY'
# the lossless render of the same clip and scale (the readers' tiles and every crop check are drawn on it)
import io, sys
import pymupdf
from PIL import Image
page = pymupdf.open(sys.argv[1])[0]
pix = page.get_pixmap(matrix=pymupdf.Matrix(3.5, 3.5), clip=pymupdf.Rect(0, 0, 1237.77, 851.46))
Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB').save(sys.argv[2])
PY

# 3. the readers' tiles (the index gives aggregate_readings.py the image size and each tile's box; the images
#    are for re-reading, tools/trailmap/runs/sugarbush-readers.json), and the readings
python3 $T/render_tiles.py --image "$W/sugarbush_source.png" --polylines "$P" --out "$W/tiles" > /dev/null
rm -f "$W"/tiles/result_*.json
cp $R/readings/result_*.json "$W/tiles/"

# 4. what the readers caught that the strokes miss: Snowball is drawn as a filled outline (piece 114; its name is
#    readings/result_extra.json), then the three splits and two unnamed connectors (decisions.py)
python3 $T/extract_pdf_vectors.py "$PDF" --clip 0,0,1237.77,851.46 --scale 3.5 --color blue=0.08,0.51,0.78 \
  --color green=0.08,0.65,0.32 --append --outlined --min-length 30 --out "$P" > /dev/null
python3 $R/decisions.py "$P" "$W/tiles/result_splits.json"
cp "$P" $D/linePolylines.json

# 5. the trail list from the printed labels (with its header), the proposals, the overlays
python3 $T/seed_roster.py --readings "$W/tiles/result_*.json" \
  --areas 'lincoln-peak=Lincoln Peak=3975,mt-ellen=Mt. Ellen=4083' \
  --trails $D/trails.ts --labels "$W/labels.json" > "$W/seed.log"; head -1 "$W/seed.log"
python3 - $D/trails.ts $R/header.txt <<'PY'
import sys
f, header = sys.argv[1], open(sys.argv[2]).read()
s = open(f).read()
open(f, 'w').write(s.replace(s[s.index('// Seeded'):s.index('export const peaks')], header))
PY
python3 $T/aggregate_readings.py --tiles "$W/tiles" --readings "$W/tiles/result_*.json" --roster $D/trails.ts \
  --polylines $D/linePolylines.json --proposals $D/trailProposals.json --review-data "$W/review_data.json" \
  --labels "$W/labels.json"
npm run -s trails:apply -- --resort sugarbush
