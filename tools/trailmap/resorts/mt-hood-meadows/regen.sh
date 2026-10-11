#!/bin/bash
# Mt. Hood Meadows: rebuild the app data (src/data/resorts/mt-hood-meadows/) from the resort's 2025-26 trail map PDF,
# the map's reading (resort.py, letters.json) and the naming decisions (decisions.py). Run from anywhere; working
# files go to $MT_HOOD_MEADOWS_WORK (default work/mt-hood-meadows, git-ignored).
#
#   tools/trailmap/resorts/mt-hood-meadows/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/mt-hood-meadows/regen.sh   # also rewrite public/maps/mt-hood-meadows.jpg
#   FORCE=1 ...                                                # go on although the PDF's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export MT_HOOD_MEADOWS_WORK=${MT_HOOD_MEADOWS_WORK:-$PWD/work/mt-hood-meadows}; W=$MT_HOOD_MEADOWS_WORK
mkdir -p "$W"

# 1. the source (plain curl): the winter trail map PDF skihood.com links (its CMS's uploads)
[ -f "$W/hood_2025-26.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/hood_2025-26.pdf" \
  https://cms.skihood.com/uploads/Trail_Map_20x17_2025_26_a721cd471e.pdf

# the file this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/hood_2025-26.pdf" d57cd5c0f3ad27aa955707dfd3160d0663479a2bfd8805608ccc74ed9d795a51  # 41070726 bytes

# 2. the map image, the line pieces, the names and the symbols (prepare.py)
python3 $T/resorts/mt-hood-meadows/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/mt-hood-meadows.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py mt-hood-meadows
