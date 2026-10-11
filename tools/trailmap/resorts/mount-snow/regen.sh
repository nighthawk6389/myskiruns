#!/bin/bash
# Mount Snow: rebuild the app data (src/data/resorts/mount-snow/: trails.ts, linePolylines, trailProposals,
# trailReviews, trailPaths) from this season's map image, two older exports of the same artwork (the 2023-24 trail map
# PDF's lines, the 2024-25 uphill map's names), the map's reading (resort.py, report.json) and the naming decisions
# (decisions.py). Run from anywhere; working files go to $MOUNT_SNOW_WORK (default work/mount-snow, git-ignored).
#
#   tools/trailmap/resorts/mount-snow/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/mount-snow/regen.sh   # also rewrite public/maps/mount-snow.jpg
#   FORCE=1 ...                                           # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export MOUNT_SNOW_WORK=${MOUNT_SNOW_WORK:-$PWD/work/mount-snow}; W=$MOUNT_SNOW_WORK
mkdir -p "$W"

# 1. the sources (plain curl): the 2025-26 map image (Vail Resorts' CDN, scene7, the PNG at its full 3175 px; the
#    resort's PDF is the same page flattened at 72 dpi), the 2023-24 trail map PDF (skimap.org map 24777: its lines)
#    and the 2024-25 winter uphill-access map (skimap.org map 36693: its names as text)
[ -f "$W/mountsnow_2025-26.png" ] || curl -sSfL -o "$W/mountsnow_2025-26.png" \
  'https://scene7.vailresorts.com/is/image/vailresorts/20251103_SO_winter-trail_map_001?fmt=png-alpha&wid=3175&qlt=100'
[ -f "$W/mountsnow_2023-24.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/mountsnow_2023-24.pdf" \
  https://skimap.org/skimaps/view/24777
[ -f "$W/mountsnow_uphill_2024-25.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/mountsnow_uphill_2024-25.pdf" \
  https://skimap.org/skimaps/view/36693

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/mountsnow_2025-26.png" dfba504b40d55e78ab7a858a5ca95c16e6abaeea97bdb4701615a98742c77502  # 3495808 bytes
check "$W/mountsnow_2023-24.pdf" 58bbfb096444683ff6a9a6fd11de35806dee92263103faa0d0e338a5d370e9c7  # 15107448 bytes
check "$W/mountsnow_uphill_2024-25.pdf" 2d505ab886b5d8937353c30baa360488717554569bd1a9bcf08d9dc64b52c6d2  # 4245813 bytes

# 2. the map image, the line pieces and the names (prepare.py)
python3 $T/resorts/mount-snow/prepare.py
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.MAX_IMAGE_PIXELS = None; Image.open('$W/map.png').convert('RGB').save('public/maps/mount-snow.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py mount-snow
