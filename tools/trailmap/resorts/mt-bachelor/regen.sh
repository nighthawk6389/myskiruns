#!/bin/bash
# Mt. Bachelor: rebuild the app data (src/data/resorts/mt-bachelor/) from the resort's 2025-26 trail map PDF, the
# map's reading (resort.py, letters.json, report.json) and the naming decisions (decisions.py). Run from anywhere;
# working files go to $MT_BACHELOR_WORK (default work/mt-bachelor, git-ignored).
#
#   tools/trailmap/resorts/mt-bachelor/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/mt-bachelor/regen.sh   # also rewrite public/maps/mt-bachelor.jpg
#   FORCE=1 ...                                            # go on although the PDF's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export MT_BACHELOR_WORK=${MT_BACHELOR_WORK:-$PWD/work/mt-bachelor}; W=$MT_BACHELOR_WORK
mkdir -p "$W"

# 1. the source: the winter trail map PDF linked from mtbachelor.com's trail map page (plain curl)
[ -f "$W/mtbachelor_2025-26.pdf" ] || curl -sSfL -o "$W/mtbachelor_2025-26.pdf" \
  https://cms.mtbachelor.com/sites/default/files/2025-11/FINAL_W2526_TrailMap_WithKey.pdf

# the file this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/mtbachelor_2025-26.pdf" e1003c0c2b544f19743643dbc7badea7a01e4b8bea76aaa243bb96942b50cb9c

# 2. the map image, the line pieces, names and symbols (prepare.py)
python3 $T/resorts/mt-bachelor/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.MAX_IMAGE_PIXELS = None; Image.open('$W/map.png').convert('RGB').save('public/maps/mt-bachelor.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py mt-bachelor
