#!/bin/bash
# Hunter Mountain: rebuild the app data (src/data/resorts/hunter/) from the 2025-26 trail-map PDF, the map's
# reading (resort.py) and the naming decisions (decisions.py). Run from anywhere; working files go to
# $HUNTER_WORK (default work/hunter, git-ignored).
#
#   tools/trailmap/resorts/hunter/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/hunter/regen.sh   # also rewrite public/maps/hunter.jpg
#   FORCE=1 ...                                       # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export HUNTER_WORK=${HUNTER_WORK:-$PWD/work/hunter}; W=$HUNTER_WORK
mkdir -p "$W"

# 1. the PDF (huntermtn.com returns an error page to curl: fetch it from inside the page)
[ -f "$W/hunter.pdf" ] || PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-$(npm root -g)/playwright} node $T/fetch_pdf.cjs \
  https://www.huntermtn.com/the-mountain/about-the-mountain/trail-map.aspx \
  https://www.huntermtn.com/-/aemasset/sitecore/hunter/maps/winter-2025-2026/20251122_HU_winter-trail_map_001.pdf \
  "$W/hunter.pdf"

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are
# checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/hunter.pdf" 3de2347a4bfafc454ccbc68ccc3d63a116bd69a33a7cfc42fa519cabc8a9045e  # 9950776 bytes

# 2. the trail lines (0.38 pt strokes in the three trail colours; lifts are thicker maroon strokes), the names
# (text) and the symbols (rounded fills), all on the same 5 px/pt grid as the map image
CLIP=34,13,1000,510
[ -f "$W/map.png" ] && [ -z "$IMAGES" ] || IMG="--image $W/map.png"
python3 $T/extract_pdf_vectors.py "$W/hunter.pdf" --clip $CLIP --scale 5 --color black=0.14,0.15,0.16 \
  --color blue=0.0,0.61,0.86 --color green=0.0,0.65,0.32 --max-width 0.5 --min-length 0.8 $IMG \
  --out "$W/pieces.json" | grep -v '^wrote.*png'
python3 $T/pdf_labels.py "$W/hunter.pdf" --out "$W/printed.json" > /dev/null
python3 $T/pdf_symbols.py "$W/hunter.pdf" --clip $CLIP --scale 5 --circle 0.0,0.65,0.32 --square 0.0,0.61,0.86 \
  --diamond 0.14,0.15,0.16 --rounded --max-diamond 3.6 --out "$W/symbols.json"
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/hunter.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py hunter
