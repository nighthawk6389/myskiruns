#!/bin/bash
# Arapahoe Basin: rebuild the app data (src/data/resorts/arapahoe-basin/: one trail list, and per map panel in
# panels/<panel>/ its pieces, proposals, reviews and overlays) from the 2025-26 trail map PDF, the map's reading
# (resort.py, panels/<panel>/resort.py, letters.json, report.json) and the naming decisions
# (panels/<panel>/decisions.py). Run from anywhere; working files go to $ARAPAHOE_BASIN_WORK (default
# work/arapahoe-basin, git-ignored).
#
#   tools/trailmap/resorts/arapahoe-basin/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/arapahoe-basin/regen.sh   # also rewrite public/maps/arapahoe-basin-*.jpg
#   FORCE=1 ...                                               # go on although the PDF's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export ARAPAHOE_BASIN_WORK=${ARAPAHOE_BASIN_WORK:-$PWD/work/arapahoe-basin}; W=$ARAPAHOE_BASIN_WORK
mkdir -p "$W"

# 1. the source (plain curl): the winter trail map PDF arapahoebasin.com's trail-maps page links (it redirects to the
# site's CDN)
[ -f "$W/abasin_2025-26.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/abasin_2025-26.pdf" \
  'https://www.arapahoebasin.com/uploaded/trailmaps/a%20basin%20map%202025.pdf'

# the file this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/abasin_2025-26.pdf" ca9934f960366d641ee741e0512a148f4caecfc5cdd773207e3b5208db4eaa5a  # 4545895 bytes

# 2. per panel: the map image, the line pieces, the names and the symbols (prepare.py)
python3 $T/resorts/arapahoe-basin/prepare.py
if [ -n "$IMAGES" ]; then
  for p in frontside zuma-bowl; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/arapahoe-basin-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece of every panel, then the trail list, and per panel the proposals, Claude's reviews and overlays
python3 $T/pdf_resort.py arapahoe-basin
