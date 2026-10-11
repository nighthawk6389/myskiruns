#!/bin/bash
# Loon: rebuild the app data (src/data/resorts/loon/) from the resort's winter trail map (an image in a PDF) and its
# interactive map's SVG, the map's reading (resort.py, report.json) and the naming decisions (decisions.py). Run from
# anywhere; working files go to $LOON_WORK (default work/loon, git-ignored).
#
#   tools/trailmap/resorts/loon/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/loon/regen.sh   # also rewrite public/maps/loon.jpg
#   FORCE=1 ...                                     # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export LOON_WORK=${LOON_WORK:-$PWD/work/loon}; W=$LOON_WORK
mkdir -p "$W/vicomap"

# 1. the sources (plain curl): the winter trail map PDF loonmtn.com's mountain-maps page links (its Sanity CDN), and
#    the interactive map's SVG and API (resorts-interactive.com map 14: its trail lines, names and symbols grouped by
#    trail)
[ -f "$W/loon_winter.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/loon_winter.pdf" \
  https://cdn.sanity.io/files/k8yfdmw9/loon/eefd64da1beb25f588c0365dd97c52c217f8b781.pdf
[ -f "$W/vicomap/map.svg" ] || curl -sSfL -o "$W/vicomap/map.svg" https://vicomap-cdn.resorts-interactive.com/map/14/svg
[ -f "$W/vicomap/api.json" ] || curl -sSfL -o "$W/vicomap/api.json" https://vicomap-cdn.resorts-interactive.com/api/maps/14

# the files this data was built from: another file (a new edition, or the interactive map redrawn) stops the rebuild
# until its decisions are checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/loon_winter.pdf" e36914fc2f0a70a107a4d73b1365460731d9f03fb82a1c359e8d110043332e79  # 8536494 bytes
check "$W/vicomap/map.svg" b3f51d65a52df18caa1be13063bd8baf01733bbc61a65e19dbd031b56e1b230f  # 7657654 bytes

# 2. the map image, the line pieces (the SVG's lines), names and symbols (prepare.py)
python3 $T/resorts/loon/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/loon.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py loon
