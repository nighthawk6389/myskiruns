#!/bin/bash
# Winter Park: rebuild the app data (src/data/resorts/winter-park/) from the 2025-26 trail-map PDF, whose trail
# lines are vector strokes and whose names are text in a font with no Unicode map (pdf_labels.py decodes them),
# the reading scripts in this folder and the name of every line piece settled on crops (decisions.py; header.txt:
# the trails.ts header). Run from anywhere; working files go to $WINTER_PARK_WORK (default work/winter-park,
# git-ignored).
#
#   tools/trailmap/resorts/winter-park/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/winter-park/regen.sh   # also rewrite public/maps/winter-park.jpg
#   FORCE=1 tools/trailmap/resorts/winter-park/regen.sh    # run on a PDF whose SHA-256 is not the 2025-26 one
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap; R=$T/resorts/winter-park; D=src/data/resorts/winter-park
export WINTER_PARK_WORK=${WINTER_PARK_WORK:-$PWD/work/winter-park}; W=$WINTER_PARK_WORK
mkdir -p "$W/tiles" "$D"

# 1. the PDF: skimap.org's copy of the resort's 2025-26 map (map 36019, "2025-2026 Downhill Ski Map" by James
#    Niehues; the page redirects to https://files.skimap.org/be74hf0apl2iydiexnnzcz095xgm.pdf; plain curl works).
#    A copy put at $W/winterpark.pdf by hand is used as is.
PDF=$W/winterpark.pdf
SHA=2323f3d992472b223f5dd354b0eff72049b514334ffdba8179950e040da08e94  # 34,921,233 bytes, fetched 2026-10-01
if [ ! -f "$PDF" ]; then
  curl -sSfL -A 'Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0' -o "$PDF.part" https://skimap.org/skimaps/view/36019
  mv "$PDF.part" "$PDF"
fi
GOT=$(python3 -c "import hashlib, sys; print(hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest())" "$PDF")
if [ "$GOT" != "$SHA" ]; then
  echo "winterpark.pdf is not the 2025-26 edition this data was built from (SHA-256 $GOT, expected $SHA)." >&2
  [ -n "$FORCE" ] || { echo "A new edition needs its decisions redone (README, \"A new season's map\"); FORCE=1 runs anyway." >&2; exit 1; }
fi

# 2. the map image: the page inside the map's frame (no logo band, legend panel or sponsor strip) at 3.2 px/pt,
#    4224x3152; the pieces, stretches and markers are on the same grid
CLIP=40,165,1360,1150
if [ -n "$IMAGES" ] || [ ! -f "$W/wp_source.png" ] || [ "$PDF" -nt "$W/wp_source.png" ]; then
  python3 -c "
import pymupdf
p = pymupdf.open('$PDF')[0]
p.get_pixmap(matrix=pymupdf.Matrix(3.2, 3.2), clip=pymupdf.Rect($CLIP)).save('$W/wp_source.png')"
fi
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/wp_source.png').convert('RGB').save('public/maps/winter-park.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. the line pieces: the 1.25 pt strokes in the three trail colours (lifts are red 1.0 pt strokes, the boundary and
#    two base-area paths black 1.0 and 1.32 pt ones, the CLOSED hatching a dark grey, the green 'easiest route'
#    bands 6 pt), then the four blue trails drawn at 1.0 pt (ids 221-231). Then the pieces' description and the
#    connectors with no printed name (decisions.py's UNNAMED).
python3 $T/extract_pdf_vectors.py "$PDF" --clip $CLIP --scale 3.2 --color blue=0.09,0.54,0.79 \
  --color green=0.09,0.63,0.29 --color black=0.01,0.02,0.02 --min-width 1.2 --max-width 1.3 --out "$W/pieces.json"
python3 $T/extract_pdf_vectors.py "$PDF" --clip $CLIP --scale 3.2 --color blue=0.09,0.54,0.79 \
  --min-width 0.95 --max-width 1.05 --append --out "$W/pieces.json"
python3 - "$W/pieces.json" $D/linePolylines.json <<'PY'
import json, sys
sys.path.insert(0, 'tools/trailmap/resorts/winter-park')
from decisions import UNNAMED
d = json.load(open(sys.argv[1]))
d['_source'] = ("PDF vector strokes (tools/trailmap/extract_pdf_vectors.py): the 1.25 pt green, blue and black strokes of "
                "Winter Park's 2025-26 map, plus White Rabbit, Lower Parkway, Lonesome Whistle and Jabberwocky's blue "
                "strokes, drawn at 1.0 pt (ids 221-231). Lifts are red; the wide green 'Easiest Route to WP Base' "
                "bands are 6 pt strokes under green lines and are not extracted")
d['_unnamed'] = {str(k): v for k, v in UNNAMED.items()}
json.dump(d, open(sys.argv[2], 'w'))
print(len(d['polylines']), 'pieces,', len(UNNAMED), 'unnamed')
PY

# 4. the printed text (glyph ids decoded through the subset's CFF charset; the two glyphs outside the usual order,
#    a hyphen and an opening quote, read on rendered labels), the symbols, and each name with its symbol
python3 $T/pdf_labels.py "$PDF" --glyph 316=- --glyph '63=‘' --out "$W/wp_labels.json" > "$W/labels.log"
python3 $R/symbols.py
python3 $R/names.py > "$W/names.log"; head -1 "$W/names.log"

# 5. the first-pass auto-match (wp_assign.json: the tags on checks/zoom.py's crops) and a check of the decisions
#    against the pieces that run on from a label's own text line (both only report: the decisions are final)
python3 $R/automatch.py > "$W/automatch.log"; head -1 "$W/automatch.log"
python3 $R/checks/collinear.py > "$W/collinear.log"; head -1 "$W/collinear.log"

# 6. the reading (every printed name with its symbol and place, the Cirque key's runs, every piece's checked name)
#    and the stretches along names printed in a gap of their line or at its end
python3 $R/reading.py > "$W/reading.log"; head -2 "$W/reading.log"

# 7. the trail list, with this folder's header
python3 $T/seed_roster.py --readings "$W/tiles/result_winterpark.json" --areas 'winter-park=Winter Park Resort=12060' \
  --trails $D/trails.ts --labels "$W/labels.json" > "$W/seed.log"; head -1 "$W/seed.log"
python3 - $D/trails.ts $R/header.txt <<'PY'
import sys
f, header = sys.argv[1], sys.argv[2]
s = open(f).read()
old = s[s.index('// Seeded'):s.index('export const peaks')]
open(f, 'w').write(s.replace(old, open(header).read()))
PY

# 8. the proposals (each piece's name; the tile index gives aggregate_readings.py the image size), Claude's reviews
#    (each stretch with its trail's pieces; markers for the names with no line) and the overlays
python3 $T/render_tiles.py --image "$W/wp_source.png" --polylines $D/linePolylines.json --out "$W/tiles" > /dev/null
python3 $T/aggregate_readings.py --tiles "$W/tiles" --readings "$W/tiles/result_*.json" --roster $D/trails.ts \
  --polylines $D/linePolylines.json --proposals $D/trailProposals.json --review-data "$W/review_data.json" \
  --labels "$W/labels.json" | tail -1
python3 $R/traces.py "$W"
rm -f "$W/recheck.json"
python3 $T/traces_to_reviews.py --replace-claude --traces "$W/trace_gaps.json" --reviews $D/trailReviews.json \
  --recheck "$W/recheck.json" --labels "$W/labels.json" --image "$W/wp_source.png" | cut -c1-60
npm run -s trails:apply -- --resort winter-park
