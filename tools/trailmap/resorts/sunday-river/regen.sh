#!/bin/bash
# Sunday River: rebuild the app data (src/data/resorts/sunday-river/) from the trail-map PDF, the map's reading
# (resort.py, letters.json) and the naming decisions (decisions.py). Run from anywhere; working files go to
# $SUNDAY_RIVER_WORK (default work/sunday-river, git-ignored).
#
#   tools/trailmap/resorts/sunday-river/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/sunday-river/regen.sh   # also rewrite public/maps/sunday-river.jpg
#   FORCE=1 ...                                             # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export SUNDAY_RIVER_WORK=${SUNDAY_RIVER_WORK:-$PWD/work/sunday-river}; W=$SUNDAY_RIVER_WORK
mkdir -p "$W"

# 1. the PDF, linked from https://www.sundayriver.com/resort-maps (plain curl works)
[ -f "$W/sundayriver.pdf" ] || curl -sSf -o "$W/sundayriver.pdf" \
  https://cdn.sanity.io/files/k8yfdmw9/sunday-river/78ea8affe8a94b5bcd3257e17f6f17db4adca4eb.pdf

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are
# checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/sundayriver.pdf" 17555851ba5ddeca8c5101ad495fffb71851a7def9c6601d9374cb50c632c196  # 44170282 bytes

# 2. the map image (the whole page at 2.5 px/pt), then the line pieces, names and symbols (prepare.py)
if [ -n "$IMAGES" ] || [ ! -f "$W/map.png" ]; then
  python3 -c "
import pymupdf
pix = pymupdf.open('$W/sundayriver.pdf')[0].get_pixmap(matrix=pymupdf.Matrix(2.5, 2.5))
pix.save('$W/map.png')"
fi
python3 $T/resorts/sunday-river/prepare.py
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/sunday-river.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py sunday-river
