#!/bin/bash
# Jay Peak: rebuild the app data (src/data/resorts/jay-peak/) from the 2025-26 trail-map PDF (its own text gives
# every trail name and symbol: labels.py, reading.py), the trace readers' traces along the painted cuts
# (readings/) and the decisions taken on crops (decisions.py; header.txt: the trails.ts header). The map draws no
# trail lines, so there are no pieces: every overlay is a trace or a marker at the label. Run from anywhere;
# working files go to $JAY_PEAK_WORK (default work/jay-peak, git-ignored).
#
#   tools/trailmap/resorts/jay-peak/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/jay-peak/regen.sh   # also rewrite public/maps/jay-peak.jpg
#   FORCE=1 ...                                         # go on with a PDF whose SHA-256 differs
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt from the traces,
# keeping their timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap; R=$T/resorts/jay-peak; D=src/data/resorts/jay-peak
export JAY_PEAK_WORK=${JAY_PEAK_WORK:-$PWD/work/jay-peak}; W=$JAY_PEAK_WORK
mkdir -p "$W" "$D"

# 1. the PDF (plain curl works). The traces are of this edition: a different file (a new season's map) means
#    redoing them (README, "A new season's map").
URL='https://jaypeakresort.com/sites/default/files/2026-02/JPR_TrailMap_Winter_2025%2B2026_ToPRINT.pdf'
SHA=005f383ed84a05b05d4e0b381a73b0ad83360c5de071fb9e53b7062076b2f779  # 18,887,714 bytes, fetched 2026-09-30
PDF=$W/jay.pdf
if [ ! -f "$PDF" ]; then
  curl -sSfL --compressed -H 'Accept: application/pdf,*/*' \
    -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36' \
    -o "$PDF.part" "$URL"
  mv "$PDF.part" "$PDF"
fi
GOT=$(sha256sum "$PDF" | cut -d' ' -f1)
if [ "$GOT" != "$SHA" ]; then
  echo "jay.pdf is not the 2025-26 edition the traces are of (SHA-256 $GOT, expected $SHA)." >&2
  [ -n "$FORCE" ] || { echo "Re-trace it (README, \"A new season's map\"), or FORCE=1 to go on anyway." >&2; exit 1; }
fi

# 2. the map image: the page at 4 px/pt inside 9,66,1076,657 pt (the painting below the header band and above
#    the footer: 4268x2364), and the empty piece list that says why there are no pieces
python3 - "$PDF" "$W/jay_source.png" "$IMAGES" <<'PY'
import io, sys
import pymupdf
from PIL import Image
page = pymupdf.open(sys.argv[1])[0]
pix = page.get_pixmap(matrix=pymupdf.Matrix(4, 4), clip=pymupdf.Rect(9, 66, 1076, 657))
img = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
img.save(sys.argv[2])
if sys.argv[3]:
    img.save('public/maps/jay-peak.jpg', quality=88, optimize=True, progressive=True)
PY
python3 - $D/linePolylines.json <<'PY'
import json, sys
json.dump({'_source': "Jay Peak's 2025-26 map draws no trail lines (trails are painted cuts, named by PDF text with a "
           "symbol), so there are no pieces: every overlay is a trace along the painted cut (trailReviews.json) or a "
           "marker at the label. Image: the PDF page rendered at 4x inside 9,66,1076,657 pt.", 'polylines': []},
          open(sys.argv[1], 'w'))
PY
# the tiles the tracers read (the whole image, as there are no pieces; aggregate_readings.py takes the image
# size from their index)
python3 $T/render_tiles.py --image "$W/jay_source.png" --polylines $D/linePolylines.json --out "$W/tiles" > /dev/null

# 3. the trail list from the PDF's text and symbols (with no readers), the tracers' label list, the proposals
#    (markers for the named glades), then the glade flags settled on crops and the header
python3 $R/labels.py "$PDF" "$W/jay_label_spans.json" > "$W/labels.log"; head -1 "$W/labels.log" | cut -c1-40
python3 $R/reading.py "$W/jay_label_spans.json" "$W/reading_pdf.json"
python3 $T/seed_roster.py --readings "$W/reading_pdf.json" --areas 'jay-peak=Jay Peak=3862' \
  --trails $D/trails.ts --labels "$W/labels.json" > "$W/seed.log"; head -1 "$W/seed.log"
python3 $R/all_labels.py "$W/labels.json" $D/trails.ts "$W/all_labels.txt"
python3 $T/aggregate_readings.py --tiles "$W/tiles" --readings "$W/reading_pdf.json" --roster $D/trails.ts \
  --polylines $D/linePolylines.json --proposals $D/trailProposals.json --review-data "$W/review_data.json" \
  --labels "$W/labels.json"
python3 $R/decisions.py trails $D/trails.ts $R/header.txt

# 4. Claude's reviews from the traces (a trace with no points becomes a marker at the label), in the order they
#    came in; then the overlays
python3 $R/decisions.py traces $R/readings "$W/traces"
rm -f "$W/recheck.json"
python3 $T/traces_to_reviews.py --traces "$W/traces/*.json" --reviews $D/trailReviews.json --recheck "$W/recheck.json" \
  --labels "$W/labels.json" --image public/maps/jay-peak.jpg --replace-claude | cut -c1-60
npm run -s trails:apply -- --resort jay-peak
