#!/bin/bash
# Jackson Hole Mountain Resort: rebuild the app data (src/data/resorts/jackson-hole/) from the resort's 2025-26 trail
# map image, the map's reading (names.py, resort.py, report.json) and the naming decisions (decisions.py). Run from
# anywhere; working files go to $JACKSON_HOLE_WORK (default work/jackson-hole, git-ignored).
#
#   tools/trailmap/resorts/jackson-hole/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/jackson-hole/regen.sh   # also rewrite public/maps/jackson-hole.jpg
#   FORCE=1 ...                                             # go on although the source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export JACKSON_HOLE_WORK=${JACKSON_HOLE_WORK:-$PWD/work/jackson-hole}; W=$JACKSON_HOLE_WORK
mkdir -p "$W"

# 1. the source (plain curl): the 2025-26 winter trail map the resort's winter trail map page shows and links for
#    download (jacksonhole.com/maps/mountain-winter: DatoCMS's asset, the PNG as uploaded, 3000x1900)
[ -f "$W/trailmap_2025-26.png" ] || curl -sSfL -o "$W/trailmap_2025-26.png" \
  'https://www.datocms-assets.com/50871/1764786024-2025-26trailmapresized.png'

# the file this data was built from: another file (a new edition) stops the rebuild until its reading is checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its reading" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/trailmap_2025-26.png" 9bcdd3eef456d3d8e4840e38e82b2e4fe101a6002cf5b7b265210361f286dc63

# 2. the map image, the lines routed along the painted ones, the labels on their letters (prepare.py)
python3 -I $T/resorts/jackson-hole/prepare.py
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/jackson-hole.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece and label, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py jackson-hole
