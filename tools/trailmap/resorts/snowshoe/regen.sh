#!/bin/bash
# Snowshoe: rebuild the app data (src/data/resorts/snowshoe/) from the resort's 2025-26 trail map image, its
# interactive map's SVG (the map's vector layer drawn again), the map's reading (resort.py, report.json) and the
# naming decisions (decisions.py). Run from anywhere; working files go to $SNOWSHOE_WORK (default work/snowshoe,
# git-ignored).
#
#   tools/trailmap/resorts/snowshoe/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/snowshoe/regen.sh   # also rewrite public/maps/snowshoe.jpg
#   FORCE=1 ...                                         # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export SNOWSHOE_WORK=${SNOWSHOE_WORK:-$PWD/work/snowshoe}; W=$SNOWSHOE_WORK
mkdir -p "$W/vicomap"

# 1. the sources (plain curl): the winter trail map image snowshoemtn.com's maps page links (no PDF this season), and
#    the interactive map's SVG and API (resorts-interactive.com map 1814: its trail lines, names and symbols grouped by
#    trail)
[ -f "$W/snowshoe_2025-26.jpg" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/snowshoe_2025-26.jpg" \
  'https://www.snowshoemtn.com/-/media/snowshoe/maps/winter-2526/wintermap.jpg?rev=7754624877b140d7a93950bd95f894b1'
[ -f "$W/vicomap/map.svg" ] || curl -sSfL -o "$W/vicomap/map.svg" https://vicomap-cdn.resorts-interactive.com/map/1814/svg
[ -f "$W/vicomap/api.json" ] || curl -sSfL -o "$W/vicomap/api.json" https://vicomap-cdn.resorts-interactive.com/api/maps/1814

# the files this data was built from: another file (a new edition, or the interactive map redrawn) stops the rebuild
# until its decisions are checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/snowshoe_2025-26.jpg" b32c99d2e0fbccdd7cbc8a47914f7f59a4d793aac7a1302fe1f75c1d9d7808a5  # 1215272 bytes
check "$W/vicomap/map.svg" 4bbea0789e68aff700da66de29cbde48d4ee0024325dbf0f286a86784a2f78dc  # 9047066 bytes

# 2. the map image, the line pieces (the SVG's lines routed onto the print's), names and symbols (prepare.py)
python3 $T/resorts/snowshoe/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/snowshoe.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py snowshoe
