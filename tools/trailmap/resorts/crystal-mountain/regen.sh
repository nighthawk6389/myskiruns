#!/bin/bash
# Crystal Mountain: rebuild the app data (src/data/resorts/crystal-mountain/: trails.ts and, per panel in panels/<panel>/,
# linePolylines, trailProposals, trailReviews, trailPaths) from the 2025-26 trail map PDF (the main panel), the
# Northway inset image (the northway panel, read on crops: names.py), the map's reading (resort.py, panels/*/resort.py,
# report.json) and the naming decisions (panels/main/decisions.py). Run from anywhere; working files go to
# $CRYSTAL_MOUNTAIN_WORK (default work/crystal-mountain, git-ignored).
#
#   tools/trailmap/resorts/crystal-mountain/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/crystal-mountain/regen.sh   # also rewrite public/maps/crystal-mountain-<panel>.jpg
#   FORCE=1 ...                                                 # go on although a source's SHA-256 differs
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export CRYSTAL_MOUNTAIN_WORK=${CRYSTAL_MOUNTAIN_WORK:-$PWD/work/crystal-mountain}; W=$CRYSTAL_MOUNTAIN_WORK
mkdir -p "$W"

# 1. the sources, from inside the resort's trail-maps page (its site answers curl with a bot check: fetch_pdf.cjs
#    asks again until the bytes are the file): the 2025-26 trail map PDF and the Northway inset (served as a WebP)
PAGE=https://www.crystalmountainresort.com/the-mountain/trail-maps
MEDIA=https://www.crystalmountainresort.com/-/media/crystal
export PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-$(npm root -g)/playwright}
[ -f "$W/crystal_2025-26.pdf" ] || node $T/fetch_pdf.cjs $PAGE \
  "$MEDIA/pdf-files/trail-maps/2025-trail-maps/crystal-winter-2425-trail-map-with-key-and-partner-bar-(2).pdf?rev=416881ea32124e0da980b6c6951ca34a" \
  "$W/crystal_2025-26.pdf"
[ -f "$W/northway_2425.webp" ] || node $T/fetch_pdf.cjs $PAGE \
  "$MEDIA/images/2425-images/maps/winter-2425-northway-map.jpg?rev=aa7c0498f1db4682b8188c63e9711034" \
  "$W/northway_2425.webp"

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/crystal_2025-26.pdf" f3563891491cda67992122682d727d4ad242823a58a18b43cfb204655e33f9e6  # 10485746 bytes
check "$W/northway_2425.webp" 2e490cf98f142e735f297349a0e3acb4e594a4e9e31f2262d83c198719b30039  # 262504 bytes

# 2. each panel's map image, line pieces, names and symbols (prepare.py)
python3 $T/resorts/crystal-mountain/prepare.py
if [ -n "$IMAGES" ]; then
  for p in main northway; do
    python3 -c "from PIL import Image; Image.MAX_IMAGE_PIXELS = None; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/crystal-mountain-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py crystal-mountain
