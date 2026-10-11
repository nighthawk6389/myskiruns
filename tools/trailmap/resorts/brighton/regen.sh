#!/bin/bash
# Brighton: rebuild the app data (src/data/resorts/brighton/) from the resort's 2025-26 trail map PDF, the map's
# reading (resort.py, letters.json, report.json) and the naming decisions (decisions.py). Run from anywhere; working
# files go to $BRIGHTON_WORK (default work/brighton, git-ignored).
#
#   tools/trailmap/resorts/brighton/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/brighton/regen.sh   # also rewrite public/maps/brighton.jpg
#   FORCE=1 ...                                         # go on although the PDF's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export BRIGHTON_WORK=${BRIGHTON_WORK:-$PWD/work/brighton}; W=$BRIGHTON_WORK
mkdir -p "$W"

# 1. the source (plain curl): the winter trail map PDF brightonresort.com's trail-maps page links (its Sanity CDN)
[ -f "$W/brighton_2025-26.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/brighton_2025-26.pdf" \
  https://cdn.sanity.io/files/8ts88bij/brighton/f5251791e4be7a7700f556616794e9796b474d18.pdf

# the file this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/brighton_2025-26.pdf" 1b09d063483a22b8dcc7fb5e60b294450c4efa45e7d858a11941c06b8e5c259a  # 27479762 bytes

# 2. the map image, the line pieces, the names and the symbols (prepare.py)
python3 $T/resorts/brighton/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/brighton.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py brighton
