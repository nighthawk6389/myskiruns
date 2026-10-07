#!/bin/bash
# Whiteface: rebuild the app data (src/data/resorts/whiteface/) from the 2025-26 trail-map PDF, whose trail lines
# are vector strokes and whose names are real text (labels.py, build.py), and the naming decisions settled on
# crops (decisions.py, and the four cuts in step 3). Run from anywhere; working files go to $WHITEFACE_WORK
# (default work/whiteface, git-ignored).
#
#   tools/trailmap/resorts/whiteface/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/whiteface/regen.sh   # also rewrite public/maps/whiteface.jpg
#   FORCE=1 tools/trailmap/resorts/whiteface/regen.sh    # run on a PDF whose SHA-256 is not the 2025-26 one
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap; R=$T/resorts/whiteface; D=src/data/resorts/whiteface
export WHITEFACE_WORK=${WHITEFACE_WORK:-$PWD/work/whiteface}; W=$WHITEFACE_WORK
mkdir -p "$W"

# 1. the PDF. whiteface.com's own (wp-content/uploads/sites/3/2025/12/Whiteface-Mountain-Trail-Map-2025-26.pdf)
#    answers scripts with a Cloudflare bot check, curl and headless Chromium alike; skimap.org has the 2025-26 map
#    (map 37629: https://skimap.org/skimaps/view/37629 redirects to the file below, plain curl works). A copy put
#    at $W/whiteface.pdf by hand is used as is; either way it must be the file this data was built from.
PDF_SHA256=16ec62c740f0b2acba7ac243b854ab86602ec8bf7558eca4711b3b4d311ed018  # 14473852 bytes
if [ ! -f "$W/whiteface.pdf" ]; then
  curl -sSfL -A 'Mozilla/5.0' -o "$W/whiteface.pdf.part" https://files.skimap.org/3zz4xytnhpior9rwxwsvb0erylv9.pdf
  mv "$W/whiteface.pdf.part" "$W/whiteface.pdf"
fi
sha=$(sha256sum "$W/whiteface.pdf" | cut -d' ' -f1)
if [ "$sha" != "$PDF_SHA256" ]; then
  echo "$W/whiteface.pdf has SHA-256 $sha, not $PDF_SHA256 (the 2025-26 map this data was built from)." >&2
  if [ -z "$FORCE" ]; then
    echo "Another edition needs its decisions redone ($R/README.md, \"A new season's map\")." >&2
    echo "To run on it anyway: FORCE=1 $R/regen.sh" >&2
    exit 1
  fi
fi

# 2. the map image (the page at 2.2 px/pt: 3795x3156) and the line pieces, on the same grid: the 1.43 and 1.5 pt
#    strokes in the three trail colours (--max-width 1.6: the default 1 pt would drop them all; the lifts are red
#    strokes of the same widths, left out by their colour)
CLIP=0,0,1724.88,1434.24
if [ ! -f "$W/map.png" ] || [ -n "$IMAGES" ]; then
  python3 -c "
import io, pymupdf
from PIL import Image
pix = pymupdf.open('$W/whiteface.pdf')[0].get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2), clip=pymupdf.Rect($CLIP))
Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB').save('$W/map.png')"
fi
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').save('public/maps/whiteface.jpg', quality=82, optimize=True, progressive=True)"
fi
python3 $T/extract_pdf_vectors.py "$W/whiteface.pdf" --clip $CLIP --scale 2.2 --color blue=0,0.46,0.74 \
  --color black=0.14,0.12,0.13 --color green=0,0.52,0.27 --max-width 1.6 --out $D/linePolylines.json

# 3. four strokes carry two trails each: cut where the second one starts (decided on crops; the lower part
#    becomes pieces 162-165, named in decisions.py). Then the names (text) and symbols (fills): each name onto
#    the pieces it is printed along or in a gap of, the crop decisions on top.
cp $D/linePolylines.json "$W/linePolylines_before_split.json"  # for checks/path_of.py
python3 $T/split_pieces.py --polylines $D/linePolylines.json --image-size 3795x3156 \
  --split '1@2201,855=CLOUDSPIN/NIAGARA' --split '34@2740,836=THE SLIDES/SLIDE OUT' \
  --split "51@2331,670=RIVA RIDGE/PARON'S RUN" --split "69@1818,946=ILMAR'S ALLEY/LOWER NORTHWAY" \
  --reading "$W/reading_splits.json"
python3 $R/labels.py > "$W/labels.log"
python3 $R/build.py > "$W/build.log"
python3 $R/reading.py > "$W/reading.log"; head -1 "$W/reading.log"

# 4. the trail list (with its header), the pieces' notes, proposals, Claude's reviews (label-gap stretches;
#    two glades are markers) and the overlays
python3 $T/seed_roster.py --readings "$W/tiles/result_whiteface.json" --areas 'whiteface=Whiteface Mountain=4867' \
  --trails $D/trails.ts --labels "$W/labels.json" > "$W/seed.log"; head -1 "$W/seed.log"
python3 - <<PY
f = '$D/trails.ts'
s = open(f).read()
old = s[s.index('// Seeded'):s.index('export const peaks')]
open(f, 'w').write(s.replace(old, open('$R/header.txt').read()))
PY
python3 $T/render_tiles.py --image "$W/map.png" --polylines $D/linePolylines.json --out "$W/tiles" > /dev/null
python3 $R/annotate.py
python3 $T/aggregate_readings.py --tiles "$W/tiles" --readings "$W/tiles/result_*.json" --roster $D/trails.ts \
  --polylines $D/linePolylines.json --proposals $D/trailProposals.json --review-data "$W/review_data.json" \
  --labels "$W/labels.json"
python3 $R/stretches.py | tail -1
python3 $T/traces_to_reviews.py --traces "$W/trace_gaps.json" --reviews $D/trailReviews.json \
  --recheck "$W/recheck.json" --replace-claude | cut -c1-60
npm run -s trails:apply -- --resort whiteface
