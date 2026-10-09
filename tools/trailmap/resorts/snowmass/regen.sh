#!/bin/bash
# Snowmass: rebuild the app data (src/data/resorts/snowmass/) from the resort's 2025-26 trail map PDF, the map's
# reading (resort.py, panels/<panel>/resort.py, report.json) and the naming decisions (panels/<panel>/decisions.py).
# Run from anywhere; working files go to $SNOWMASS_WORK (default work/snowmass, git-ignored).
#
#   tools/trailmap/resorts/snowmass/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/snowmass/regen.sh   # also rewrite public/maps/snowmass-<panel>.jpg
#   FORCE=1 ...                                         # go on although the source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export SNOWMASS_WORK=${SNOWMASS_WORK:-$PWD/work/snowmass}; W=$SNOWMASS_WORK
mkdir -p "$W"

# 1. the source (plain curl): the trail map PDF aspensnowmass.com's Snowmass trail-map page links ("layered")
[ -f "$W/snowmass_2025-26.pdf" ] || curl -sSfL -o "$W/snowmass_2025-26.pdf" \
  "https://www.aspensnowmass.com/-/media/aspen-snowmass/documents/pdfs/25-26/2526-mountain-maps/2526snowmass-map-layeredwebsite.pdf"

# the file this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/snowmass_2025-26.pdf" c3245eb5c9cc25aa603fbc02ca4b1146d8c6476e4def4fbe02334943592c0231

# 2. per panel the map image, the line pieces, the names and their ratings (prepare.py)
python3 $T/resorts/snowmass/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  for p in main hanging-valley; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/snowmass-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays of both panels
python3 $T/pdf_resort.py snowmass
