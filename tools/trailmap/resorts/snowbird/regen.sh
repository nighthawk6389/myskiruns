#!/bin/bash
# Snowbird: rebuild the app data (src/data/resorts/snowbird/) from the resort's 2025-26 trail map image, the
# map's reading (names.py, resort.py, report.json) and the naming decisions (decisions.py). Run from
# anywhere; working files go to $SNOWBIRD_WORK (default work/snowbird, git-ignored).
#
#   tools/trailmap/resorts/snowbird/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/snowbird/regen.sh   # also rewrite public/maps/snowbird.jpg
#   FORCE=1 ...                                         # go on although the source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export SNOWBIRD_WORK=${SNOWBIRD_WORK:-$PWD/work/snowbird}; W=$SNOWBIRD_WORK
mkdir -p "$W"

# 1. the source (plain curl): the 2025-26 winter trail map the resort's winter trail map page shows
#    (snowbird.com/the-mountain/maps/winter-trail-map: its CMS's JPEG, 1920x2318; the page's PDF holds the same image)
[ -f "$W/trailmap_2025-26.jpg" ] || curl -sSfL -o "$W/trailmap_2025-26.jpg" \
  'https://cms.snowbird.com/sites/default/files/2025-11/snowbird_trailmap_winter_2526.jpg'

# the file this data was built from: another file (a new edition) stops the rebuild until its reading is checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its reading" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/trailmap_2025-26.jpg" 612073449c40140083930de53cc7e17c8176122ee73e73343553452809ba64db

# 2. the map image, the lines routed along the painted ones, the labels on their letters (prepare.py)
python3 -I $T/resorts/snowbird/prepare.py
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/snowbird.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece and label, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py snowbird
