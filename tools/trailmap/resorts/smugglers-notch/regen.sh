#!/bin/bash
# Smugglers' Notch: rebuild the app data (src/data/resorts/smugglers-notch/) from the trail-map PDF, the map's
# reading (resort.py, letters.json) and the naming decisions (decisions.py). Run from anywhere; working files go to
# $SMUGGLERS_NOTCH_WORK (default work/smugglers-notch, git-ignored).
#
#   tools/trailmap/resorts/smugglers-notch/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/smugglers-notch/regen.sh   # also rewrite public/maps/smugglers-notch.jpg
#   FORCE=1 ...                                                # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export SMUGGLERS_NOTCH_WORK=${SMUGGLERS_NOTCH_WORK:-$PWD/work/smugglers-notch}; W=$SMUGGLERS_NOTCH_WORK
mkdir -p "$W"

# 1. the PDF, linked from https://www.smuggs.com/conditions-stats/trail-map/ (plain curl works)
[ -f "$W/smuggs.pdf" ] || curl -sSf -o "$W/smuggs.pdf" https://www.smuggs.com/wp-content/uploads/2024/11/trailmap_2425.pdf

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are
# checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/smuggs.pdf" 73ea287a0bdeddeffab0124c6272e2c25b1b0b8f6fb233a14db515c37d415a9c  # 1374705 bytes

# 2. the map image (the vector layer over the upscaled painting), the line pieces, names and symbols (prepare.py)
python3 $T/resorts/smugglers-notch/prepare.py
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/smugglers-notch.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py smugglers-notch
