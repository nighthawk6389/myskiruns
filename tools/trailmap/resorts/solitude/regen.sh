#!/bin/bash
# Solitude: rebuild the app data (src/data/resorts/solitude/) from the resort's 2025-26 trail map PDF (one flattened
# image), its interactive map's SVG (the map's vector layer drawn again), the map's reading (resort.py, report.json)
# and the naming decisions (decisions.py). Run from anywhere; working files go to $SOLITUDE_WORK (default
# work/solitude, git-ignored).
#
#   tools/trailmap/resorts/solitude/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/solitude/regen.sh   # also rewrite public/maps/solitude.jpg
#   FORCE=1 ...                                         # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export SOLITUDE_WORK=${SOLITUDE_WORK:-$PWD/work/solitude}; W=$SOLITUDE_WORK
mkdir -p "$W/vicomap"

# 1. the sources (plain curl): the winter trail map PDF solitudemountain.com's conditions-and-maps page links, and the
#    interactive map's SVG and API (resorts-interactive.com map 1811: its trail lines, names and symbols grouped by
#    trail)
[ -f "$W/solitude_2025-26.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/solitude_2025-26.pdf" \
  https://www.solitudemountain.com/-/media/Solitude/Trail-Map-PDFs/Solitude_Winter_Trail_Map_2526.pdf
[ -f "$W/vicomap/map.svg" ] || curl -sSfL -o "$W/vicomap/map.svg" https://vicomap-cdn.resorts-interactive.com/map/1811/svg
[ -f "$W/vicomap/api.json" ] || curl -sSfL -o "$W/vicomap/api.json" https://vicomap-cdn.resorts-interactive.com/api/maps/1811

# the files this data was built from: another file (a new edition, or the interactive map redrawn) stops the rebuild
# until its decisions are checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/solitude_2025-26.pdf" b0dd41541f5c34793cc5d92e229d04cc5afb80f6748dd141c93a735d476e1570  # 5438404 bytes
check "$W/vicomap/map.svg" 464aa5655d9da8a815095a352db386d6449d9473b98c38bc533c22bf77b7c993  # 7693499 bytes

# 2. the map image, the line pieces (the SVG's lines), names and symbols (prepare.py)
python3 $T/resorts/solitude/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.open('$W/map.png').convert('RGB').save('public/maps/solitude.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py solitude
