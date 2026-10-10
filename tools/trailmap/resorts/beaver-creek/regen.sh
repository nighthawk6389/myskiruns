#!/bin/bash
# Beaver Creek: rebuild the app data (src/data/resorts/beaver-creek/) from the 2025-26 trail map image on Vail
# Resorts' CDN and the 2023 vector export of its artwork on skimap.org, the map's reading (resort.py, letters.json,
# report.json) and the naming decisions (decisions.py). Run from anywhere; working files go to $BEAVER_CREEK_WORK
# (default work/beaver-creek, git-ignored).
#
#   tools/trailmap/resorts/beaver-creek/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/beaver-creek/regen.sh   # also rewrite public/maps/beaver-creek.jpg
#   FORCE=1 ...                                             # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export BEAVER_CREEK_WORK=${BEAVER_CREEK_WORK:-$PWD/work/beaver-creek}; W=$BEAVER_CREEK_WORK
mkdir -p "$W"

# 1. the sources (plain curl): the 2025-26 map image (scene7, the PNG at its full 4990 px) and the 2023 PDF
#    (skimap.org map 25267, 2023-10-04: lines, names, symbols)
[ -f "$W/beavercreek_2025-26.png" ] || curl -sSfL -o "$W/beavercreek_2025-26.png" \
  'https://scene7.vailresorts.com/is/image/vailresorts/20251006_BC_winter-trail_map_001?fmt=png-alpha&wid=4990&qlt=100'
[ -f "$W/beavercreek_2023.pdf" ] || curl -sSfL -o "$W/beavercreek_2023.pdf" https://skimap.org/skimaps/view/25267

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are
# checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/beavercreek_2025-26.png" b678a70bb7cdce3208c130129c246582b2c919c57d6279a11e4edbc73b067e53
check "$W/beavercreek_2023.pdf" 1fee7bfe161df4e2e3496061134f8a8ffe016624131b8899edec510ef1bd6bf0

# 2. the map image (the 2025-26 image above its partners' band), the line pieces, names and symbols (prepare.py)
python3 -I $T/resorts/beaver-creek/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.MAX_IMAGE_PIXELS = None; Image.open('$W/map.png').convert('RGB').save('public/maps/beaver-creek.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py beaver-creek
