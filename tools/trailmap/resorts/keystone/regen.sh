#!/bin/bash
# Keystone: rebuild the app data (src/data/resorts/keystone/) from the 2025-26 trail-map PDF, the names' glyph
# letters (letters.json) and the naming decisions (decisions.py). Run from anywhere; working files go to
# $KEYSTONE_WORK (default work/keystone, git-ignored). The map image is the PDF's vector layer matted over Vail
# Resorts' CDN raster of the whole map (2.08 px/pt; the PDF embeds its painting at about 1 px/pt).
#
#   tools/trailmap/resorts/keystone/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/keystone/regen.sh   # also rewrite public/maps/keystone.jpg
#   FORCE=1 ...                                         # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap; K=$T/resorts/keystone; D=src/data/resorts/keystone
export KEYSTONE_WORK=${KEYSTONE_WORK:-$PWD/work/keystone}; W=$KEYSTONE_WORK
mkdir -p "$W"

# the files this data was built from: another one (a new season's map, a re-exported painting) stops the rebuild
check() {
  local got; got=$(sha256sum "$1" | cut -d' ' -f1)
  [ "$got" = "$2" ] && return
  echo "$1: SHA-256 $got, not $2 (the file Keystone's data was built from): a new edition?" >&2
  echo "  Redo the checks (README.md, \"A new season's map\"), or run with FORCE=1 to go on anyway." >&2
  [ -n "$FORCE" ] || exit 1
}

# 1. the PDF (keystoneresort.com returns an error page to curl: fetch it from inside its trail-map page; skimap.org
#    map 35939 is the same file for plain curl), and the map's raster from Vail Resorts' image CDN (plain curl
#    works). A copy placed in $W by hand is used as it is, if its SHA-256 matches.
if [ ! -f "$W/keystone.pdf" ]; then
  # behind this sandbox's agent proxy, Chromium needs the proxy CA's public-key pin (the playbook, step 1)
  CA=/root/.ccr/agent-proxy-ca.crt
  [ -n "$PIN" ] || [ ! -f $CA ] || export PIN=$(openssl x509 -in $CA -pubkey -noout | openssl pkey -pubin -outform der |
    openssl dgst -sha256 -binary | base64)
  PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-$(npm root -g)/playwright} node $T/fetch_pdf.cjs \
    https://www.keystoneresort.com/the-mountain/about-the-mountain/trail-map.aspx \
    https://www.keystoneresort.com/-/aemasset/sitecore/keystone/maps/winter-2025-2026/20251028_KY_winter-trail_map_001.pdf \
    "$W/keystone.pdf"
fi
check "$W/keystone.pdf" 103978ffe2c7c576e33c9147eb09310e598f84a0072fe4e918353425438de243
[ -f "$W/scene7.jpg" ] || curl -sSf -o "$W/scene7.jpg" \
  "https://scene7.vailresorts.com/is/image/vailresorts/20251028_KY_winter-trail_map_001?wid=3187&hei=2569&fit=constrain,1&qlt=95"
check "$W/scene7.jpg" 8e836d78ff3d7cf6012ab81f6494ede4c7b376d8c7aa2fa6999e43f0edd20541

# 2. the map image: the vector layer (lines, names, symbols, icons) at 2.8 px/pt over the CDN's raster (3187x2569,
#    stretched to the page) in place of the PDF's 1610x1201 painting (xref 23), the map area only (0,90 to
#    1530,1080 pt: 4284x2772 px). The CDN raster is the whole map flattened, so the PDF's three translucent layers
#    (the 75% Multiply bands and slow zones, a 75% legend swatch, a 50% box) are left to it (--flattened)
if [ -n "$IMAGES" ] || [ ! -f "$W/map.png" ]; then
  python3 $T/matte_pdf_layer.py --pdf "$W/keystone.pdf" --out "$W/map.png" --scale 2.8 --clip 0,90,1530,1080 \
    --xref 23 --background "$W/scene7.jpg" --flattened
fi
if [ -n "$IMAGES" ]; then
  python3 -c "
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
Image.open('$W/map.png').convert('RGB').save('public/maps/keystone.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. the names: the outlined glyphs in the name colours (blue; two greens; black; a near-black, k14, that only icons
#    and the older copies under some road names use; the kids' zones' gold, in two shades; the parks' orange)
#    outside the legend and the bar under the map, each shape's letter from letters.json, word gaps measured along
#    the line (a condensed font); then the trail names among them, joined where set on two lines, each with its
#    symbol (names.py)
python3 $T/pdf_glyphs.py collect "$W/keystone.pdf" --out "$W/glyphs.json" --color blue=0,0.48,0.76 \
  --color green=0,0.61,0.4 --color green=0,0.6,0.4 --color black=0,0,0 --color k14=0.14,0.12,0.13 \
  --color kids=0.96,0.7,0.13 --color kids=0.96,0.7,0.14 --color park=1,0.32,0 \
  --exclude 1280,590,1530,1233 --exclude 0,1075,1530,1233 > "$W/glyphs.log"
python3 $T/pdf_glyphs.py labels "$W/keystone.pdf" --glyphs "$W/glyphs.json" --letters $K/letters.json \
  --out "$W/glyph_labels.json" --square blue --diamond black --circle green --space 0.75 > "$W/labels.log"
head -1 "$W/labels.log" | sed "s#$W/##"
python3 $K/names.py > "$W/names.log"; head -2 "$W/names.log"

# 4. the trail lines: the 1.5 pt green, blue and black strokes, then the two 1 pt black ones (Roulette, Black Jack),
#    on the map image's grid (the legend panel left out); piece 2 is cut where Brahma becomes Snake Pit, below the
#    Outpost Gondola; linePolylines.json records the cut and the pieces that carry no name (decisions.py)
python3 $T/extract_pdf_vectors.py "$W/keystone.pdf" --clip 0,90,1530,1080 --scale 2.8 --color black=0,0,0 \
  --color blue=0,0.48,0.76 --color green=0,0.61,0.4 --min-width 1.4 --max-width 1.6 --exclude 1280,590,1530,1080 \
  --out "$W/pieces.json" | sed "s#$W/##"
python3 $T/extract_pdf_vectors.py "$W/keystone.pdf" --clip 0,90,1530,1080 --scale 2.8 --color black=0,0,0 \
  --min-width 0.9 --max-width 1.1 --exclude 1280,590,1530,1080 --append --out "$W/pieces.json" | sed "s#$W/##"
python3 $T/split_pieces.py --polylines "$W/pieces.json" --image-size 4284x2772 \
  --split '2@2410.8,890.4=Brahma/Snake Pit' --reading "$W/splits_reading.json"
python3 - <<PY
import json, sys
sys.path.insert(0, '$K')
from decisions import UNNAMED
d = json.load(open('$W/pieces.json'))
d['_unnamed'] = {str(k): v for k, v in sorted(UNNAMED.items())}
d['_source'] = ('Keystone 2025-26 map PDF: its 1.5 pt green, blue and black trail strokes plus the two 1 pt ones '
                '(Roulette, Black Jack), tools/trailmap/extract_pdf_vectors.py; piece 2 cut where Brahma becomes '
                'Snake Pit; percent of the 4284x2772 map image')
json.dump(d, open('$D/linePolylines.json', 'w'))
PY

# 5. each piece's name: the label printed along it (build.py) or the decision settled on a crop (decisions.py), as
#    a reading in the readers' format, plus stretches along names printed in a gap of their line and markers for
#    names with no line (reading.py). The tiles' index tells aggregate_readings.py the image size.
python3 $K/build.py > "$W/build.log"
python3 $T/render_tiles.py --image "$W/map.png" --polylines $D/linePolylines.json --out "$W/tiles" |
  tail -1 | sed "s#$W/##"
python3 $K/reading.py | tail -3

# 6. the trail list (names as printed, difficulty from the symbol) with its header
python3 $T/seed_roster.py --readings "$W/tiles/result_keystone.json" --areas 'keystone=Keystone=12614' \
  --trails $D/trails.ts --labels "$W/labels.json" > "$W/seed.log"; head -1 "$W/seed.log"
python3 - <<PY
f = '$D/trails.ts'
s = open(f).read()
old = s[s.index('// Seeded'):s.index('export const peaks')]
open(f, 'w').write(s.replace(old, open('$K/header.txt').read()))
PY

# 7. the proposals (every named piece), Claude's reviews (stretches and markers: traces.py), then the overlays
python3 $T/aggregate_readings.py --tiles "$W/tiles" --readings "$W/tiles/result_*.json" --roster $D/trails.ts \
  --polylines $D/linePolylines.json --proposals $D/trailProposals.json --review-data "$W/review_data.json" \
  --labels "$W/labels.json" | tail -1
python3 $K/traces.py
rm -f "$W/recheck.json"
python3 $T/traces_to_reviews.py --replace-claude --traces "$W/trace_gaps.json" --reviews $D/trailReviews.json \
  --recheck "$W/recheck.json" --labels "$W/labels.json" --image "$W/map.png" | tail -1 | cut -c1-40
npm run -s trails:apply -- --resort keystone

# 8. the names shown: the trail report's spelling where the map prints a run otherwise (decisions.py's REPORT_NAMES,
#    from report.json); last, since the proposals match the reading's names to trails.ts's. The ids stay the map's.
python3 - $D/trails.ts <<'PY'
import re, sys
sys.path.insert(0, 'tools/trailmap/resorts/keystone')
from decisions import REPORT_NAMES
f = sys.argv[1]
s = open(f).read()
done = set()
def shown(m):
    old = m.group(2)
    if old not in REPORT_NAMES:
        return m.group(0)
    done.add(old)
    new = REPORT_NAMES[old]
    return 'name: ' + (f'"{new}"' if "'" in new else f"'{new}'")
s = re.sub(r"""name: (['"])(.*?)\1""", shown, s)
assert done == set(REPORT_NAMES), set(REPORT_NAMES) - done
open(f, 'w').write(s)
print(len(done), "names spelled as the trail report spells them")
PY
