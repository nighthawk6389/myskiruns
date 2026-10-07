#!/bin/bash
# Sugarloaf: rebuild the app data (src/data/resorts/sugarloaf/) from the trail-map PDF, the map's reading
# (resort.py, letters.json) and the naming decisions (decisions.py). Run from anywhere; working files go to
# $SUGARLOAF_WORK (default work/sugarloaf, git-ignored).
#
#   tools/trailmap/resorts/sugarloaf/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/sugarloaf/regen.sh   # also rewrite public/maps/sugarloaf.jpg
#   FORCE=1 ...                                          # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export SUGARLOAF_WORK=${SUGARLOAF_WORK:-$PWD/work/sugarloaf}; W=$SUGARLOAF_WORK
mkdir -p "$W"

# 1. the 2025-26 PDF, linked from https://www.sugarloaf.com/the-mountain/trail-map (plain curl works)
[ -f "$W/sugarloaf.pdf" ] || curl -sSf -o "$W/sugarloaf.pdf" \
  https://cdn.sanity.io/files/k8yfdmw9/sugarloaf/dfcf8f514a7b5fd6c62814f5939fd7b6ea9d24c1.pdf

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are
# checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/sugarloaf.pdf" 0c40f78fdd202da89658fac855ac8f31ef5d59df38c5ced3322c11e617c77a91  # 4886389 bytes

# 2. the map image (the vector layer over the upscaled painting), the line pieces, names and symbols (prepare.py)
python3 $T/resorts/sugarloaf/prepare.py
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/sugarloaf.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py sugarloaf
