#!/bin/bash
# Okemo: rebuild the app data (src/data/resorts/okemo/) from the 2025-26 trail-map PDF, the readers' readings
# (readings/: six tile readers and five trace readers, Claude sub-agents, 2026-09-30) and Claude's hand-made
# decisions (decisions.py, applied by steps.py). Run from anywhere; working files go to $OKEMO_WORK (default
# work/okemo, git-ignored).
#
#   tools/trailmap/resorts/okemo/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/okemo/regen.sh   # also rewrite public/maps/okemo.jpg
#   FORCE=1 tools/trailmap/resorts/okemo/regen.sh    # run on a PDF other than the one the readings were made on
#   TILES=1 FORCE=1 tools/trailmap/resorts/okemo/regen.sh   # a new edition: stop after its pieces and tiles
#
# A person's reviews in trailReviews.json (Okemo's Trail Check review) are kept untouched, and checked to be;
# Claude's ("by": "claude") are rebuilt, keeping their timestamps when nothing changed. The file is never deleted.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
R=$T/resorts/okemo
D=src/data/resorts/okemo
export OKEMO_WORK=${OKEMO_WORK:-$PWD/work/okemo}; W=$OKEMO_WORK
mkdir -p "$W"

# 1. the PDF (3,047,541 bytes; page 2 is the map). okemo.com sends it to curl as it comes, and an error page ("The
#    system cannot process your request") to a browser's user agent without a browser's other headers; failing
#    curl, it is fetched from inside the trail-map page in headless Chromium. Or save it from a browser as
#    $W/okemo.pdf: it is checked the same way.
URL=https://www.okemo.com/-/aemasset/sitecore/okemo/maps/winter-2025-2026/20251120_OK_winter-trail_map_001.pdf
PAGE=https://www.okemo.com/the-mountain/about-the-mountain/trail-map.aspx
SHA256=82a8454dd34c58d4c5731905a7a44a079d9940899aeda85162f5fec8b1c839a1
if [ ! -f "$W/okemo.pdf" ]; then
  rm -f "$W/okemo.pdf.part"
  curl -sSfL -o "$W/okemo.pdf.part" "$URL" || true
  if [ "$(head -c 5 "$W/okemo.pdf.part" 2>/dev/null)" != "%PDF-" ]; then
    echo "curl got no PDF from okemo.com; fetching it from inside the trail-map page" >&2
    CA=/root/.ccr/agent-proxy-ca.crt  # behind this sandbox's agent proxy Chromium needs its CA's pin (playbook, Part 4)
    if [ -z "$PIN" ] && [ -f $CA ]; then
      PIN=$(openssl x509 -in $CA -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64)
    fi
    PIN=$PIN PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-$(npm root -g)/playwright} node $T/fetch_pdf.cjs "$PAGE" "$URL" \
      "$W/okemo.pdf.part" || true
  fi
  if [ "$(head -c 5 "$W/okemo.pdf.part" 2>/dev/null)" != "%PDF-" ]; then
    echo "okemo.com sent no PDF. Download $URL in a browser and save it as $W/okemo.pdf." >&2
    exit 1
  fi
  mv "$W/okemo.pdf.part" "$W/okemo.pdf"
fi
GOT=$(sha256sum "$W/okemo.pdf" | cut -d' ' -f1)
if [ "$GOT" != "$SHA256" ]; then
  echo "warning: $W/okemo.pdf is not the PDF Okemo's readings were made on (sha256 $GOT, expected $SHA256)." >&2
  if [ -z "$FORCE" ]; then
    echo "A new edition needs new readings (README.md, \"A new season's map\"). FORCE=1 runs on it anyway." >&2
    exit 1
  fi
fi

# 2. the line pieces, on a 3 px/pt grid of the map (page 2 down to its band of partner logos): 0.74 pt strokes in
#    the three trail colours (lifts are 1.11 pt red strokes and the legend's hatching 1.0 pt black, both over
#    --max-width), then the orange terrain-park strokes appended (ids 246-255). With IMAGES=1 the first pass also
#    writes the map.
CLIP=0,0,1458,913
IMG=; [ -n "$IMAGES" ] && IMG="--image public/maps/okemo.jpg"
python3 $T/extract_pdf_vectors.py "$W/okemo.pdf" --page 1 --clip $CLIP --scale 3 --color black=0.01,0.02,0.02 \
  --color blue=0.21,0.33,0.65 --color green=0.05,0.53,0.26 --max-width 0.8 $IMG --out "$W/pieces.json" > /dev/null
python3 $T/extract_pdf_vectors.py "$W/okemo.pdf" --page 1 --clip $CLIP --scale 3 --color freestyle=0.96,0.51,0.12 \
  --max-width 0.8 --append --out "$W/pieces.json"

# 3. the lossless render on the same grid (crops, tiles) and the numbered tiles the readers named the pieces on
python3 -c "
import io, pymupdf
from PIL import Image
pix = pymupdf.open('$W/okemo.pdf')[1].get_pixmap(matrix=pymupdf.Matrix(3, 3), clip=pymupdf.Rect($CLIP))
Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB').save('$W/okemo_source.png')"
python3 $T/render_tiles.py --image "$W/okemo_source.png" --polylines "$W/pieces.json" --out "$W/tiles" > /dev/null
if [ -n "$TILES" ]; then echo "pieces in $W/pieces.json, tiles in $W/tiles; stopped before the data (TILES=1)"; exit 0; fi

# 4. the trail list from the labels the six tile readers saw printed, then the by-hand changes (Tomahawk Park,
#    Tree Tap a park). Only the readers' files: the overrides and the split came after the list.
python3 $T/seed_roster.py --readings "$R/readings/result_[0-9].json" \
  --areas 'okemo-mountain=Okemo Mountain=3344,jackson-gore=Jackson Gore=2725' \
  --trails $D/trails.ts --labels "$W/labels.json" > "$W/seed_roster.log"
head -1 "$W/seed_roster.log"
python3 $R/steps.py trails

# 5. the pieces as the app's line pieces: one unlabelled spur recorded, 210 cut where Turkey Shoot leaves
#    Challenger (its names become the reading result_splits.json, next to the readers')
rm -rf "$W/readings" && mkdir -p "$W/readings" && cp $R/readings/result_*.json "$W/readings/"
cp "$W/pieces.json" $D/linePolylines.json
python3 $R/steps.py unnamed
python3 $R/steps.py split

# 6. every piece's name from the readers' votes (plus the overrides and the split): the proposals
mkdir -p "$W/review"
python3 $T/aggregate_readings.py --tiles "$W/tiles" --readings "$W/readings/result_*.json" --roster $D/trails.ts \
  --polylines $D/linePolylines.json --proposals $D/trailProposals.json --review-data "$W/review/data.json" \
  --labels "$W/labels.json"

# 7. Claude's reviews: the trace readers' traces (Turkey Shoot's on the cut piece), the markers and Challenger,
#    for trails no person has decided. Every trail Okemo's reviewer decided keeps their decision.
# (copies in $W/traces: $W/trace is where the trailmap-trace workflow writes, tools/trailmap/runs/okemo-trace.json)
rm -rf "$W/traces" && mkdir -p "$W/traces" && cp $R/readings/trace_*.json "$W/traces/"
python3 $R/steps.py trace
rm -f "$W/reviews_before.json" "$W/recheck.json"
if [ -f $D/trailReviews.json ]; then cp $D/trailReviews.json "$W/reviews_before.json"; fi
python3 $T/traces_to_reviews.py --traces "$W/traces/trace_*.json" --reviews $D/trailReviews.json \
  --recheck "$W/recheck.json" --replace-claude > /dev/null
python3 $R/steps.py reviews --before "$W/reviews_before.json"
python3 $R/steps.py person --before "$W/reviews_before.json"

# 8. the review page (tools/trailmap/review/) in $W/review: data.json with the recheck flags and label hints,
#    the page and the map, ready to publish (playbook, Part 4)
python3 $T/refresh_review_data.py --review-data "$W/review/data.json" --roster $D/trails.ts \
  --reviews $D/trailReviews.json --recheck "$W/recheck.json" > /dev/null
python3 $R/steps.py hints
sed 's#<title>Trail Map Check</title>#<title>Okemo Trail Check</title>#' $T/review/index.html > "$W/review/index.html"
cp public/maps/okemo.jpg "$W/review/map.jpg"

# 9. the overlays
npm run -s trails:apply -- --resort okemo

# 10. check the difficulties against the symbols drawn in the PDF (120 of 127 labels; README, "Checks done")
python3 $T/pdf_symbols.py "$W/okemo.pdf" --page 1 --clip $CLIP --scale 3 --circle 0.05,0.53,0.26 \
  --square 0.21,0.33,0.65 --diamond 0.01,0.02,0.02 --exclude 0,480,140,913 --out "$W/symbols.json" \
  --check "$W/labels.json" --trails $D/trails.ts > "$W/symbols.log"
tail -1 "$W/symbols.log"
