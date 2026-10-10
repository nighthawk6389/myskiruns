#!/bin/bash
# Northstar: rebuild the app data (src/data/resorts/northstar/) from the resort's 2025-26 trail map PDF, the map's
# reading (resort.py, letters.json, report.json) and the naming decisions (decisions.py). Run from anywhere; working
# files go to $NORTHSTAR_WORK (default work/northstar, git-ignored).
#
#   tools/trailmap/resorts/northstar/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/northstar/regen.sh   # also rewrite public/maps/northstar.jpg
#   FORCE=1 ...                                          # go on although the PDF's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export NORTHSTAR_WORK=${NORTHSTAR_WORK:-$PWD/work/northstar}; W=$NORTHSTAR_WORK
mkdir -p "$W"

# 1. the PDF (northstarcalifornia.com returns an error page to curl: fetch it from inside its trail-map page;
#    skimap.org's map 36907 is the same file)
[ -f "$W/northstar_2025-26.pdf" ] || PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-$(npm root -g)/playwright} node $T/fetch_pdf.cjs \
  https://www.northstarcalifornia.com/the-mountain/about-the-mountain/trail-map.aspx \
  https://www.northstarcalifornia.com/-/aemasset/sitecore/northstar/maps/winter-2025-2026/20251022_NS_winter-trail_map_001.pdf \
  "$W/northstar_2025-26.pdf"

# the file this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/northstar_2025-26.pdf" 5632990b15b2ca633eae5b452d261d527057f91f0de722aafb68cf7a4f7e1b35  # 4746329 bytes

# 2. the map image, the line pieces, the names and the symbols (prepare.py)
python3 $T/resorts/northstar/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/northstar.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py northstar
