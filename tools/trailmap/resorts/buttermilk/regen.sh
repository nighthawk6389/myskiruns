#!/bin/bash
# Buttermilk: rebuild the app data (src/data/resorts/buttermilk/) from the resort's 2025-26 trail map PDF, the map's
# reading (resort.py, report.json) and the naming decisions (decisions.py). Run from anywhere; working files go to
# $BUTTERMILK_WORK (default work/buttermilk, git-ignored).
#
#   tools/trailmap/resorts/buttermilk/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/buttermilk/regen.sh   # also rewrite public/maps/buttermilk.jpg
#   FORCE=1 ...                                           # go on although the source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export BUTTERMILK_WORK=${BUTTERMILK_WORK:-$PWD/work/buttermilk}; W=$BUTTERMILK_WORK
mkdir -p "$W"

# 1. the source (plain curl): the trail map PDF aspensnowmass.com's Buttermilk trail-map page links ("layered")
[ -f "$W/buttermilk_2025-26.pdf" ] || curl -sSfL -o "$W/buttermilk_2025-26.pdf" \
  "https://www.aspensnowmass.com/-/media/aspen-snowmass/documents/pdfs/25-26/2526-mountain-maps/2526buttermilk-map-layeredwebsite.pdf"

# the file this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/buttermilk_2025-26.pdf" 3b09dbefeb5bc165430d73e35bd150838d88dd3c0db60d5057e9764ffd0b0cfc

# 2. the map image, the line pieces, the names and their ratings (prepare.py)
python3 $T/resorts/buttermilk/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/buttermilk.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py buttermilk
