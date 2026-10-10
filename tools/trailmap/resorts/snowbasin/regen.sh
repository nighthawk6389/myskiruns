#!/bin/bash
# Snowbasin: rebuild the app data (src/data/resorts/snowbasin/) from the resort's 2025-26 trail map PDF, the map's
# reading (resort.py, report.json) and the naming decisions (decisions.py). Run from anywhere; working files go to
# $SNOWBASIN_WORK (default work/snowbasin, git-ignored).
#
#   tools/trailmap/resorts/snowbasin/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/snowbasin/regen.sh   # also rewrite public/maps/snowbasin.jpg
#   FORCE=1 ...                                          # go on although the PDF's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export SNOWBASIN_WORK=${SNOWBASIN_WORK:-$PWD/work/snowbasin}; W=$SNOWBASIN_WORK
mkdir -p "$W"

# 1. the source (plain curl): the winter trail map PDF snowbasin.com's trail-maps page links ("for Ikon, reduced";
#    skimap.org's map 34864 is the same file)
[ -f "$W/snowbasin_2025-26.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/snowbasin_2025-26.pdf" \
  "https://www.snowbasin.com/getmedia/969afd05-b39b-4ecd-b123-6c0669d41d77/Winter-Trail-Map-2025-26-(22-5in-x-12in)-for-Ikon-reduced.pdf"

# the file this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/snowbasin_2025-26.pdf" 2361cc87b5f9d9ff89a9a717462df303dd4c4837167050bb7aaa53cd06fe875e  # 1911443 bytes

# 2. the map image, the line pieces, the names and the symbols (prepare.py)
python3 $T/resorts/snowbasin/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/snowbasin.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py snowbasin
