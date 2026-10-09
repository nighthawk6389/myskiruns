#!/bin/bash
# Steamboat: rebuild the app data (src/data/resorts/steamboat/) from the resort's 2026-27 trail map image, its
# interactive map's SVG (the map's vector layer drawn again), the map's reading (resort.py, report.json) and the
# naming decisions (decisions.py). Run from anywhere; working files go to $STEAMBOAT_WORK (default work/steamboat,
# git-ignored).
#
#   tools/trailmap/resorts/steamboat/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/steamboat/regen.sh   # also rewrite public/maps/steamboat.jpg
#   FORCE=1 ...                                          # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export STEAMBOAT_WORK=${STEAMBOAT_WORK:-$PWD/work/steamboat}; W=$STEAMBOAT_WORK
mkdir -p "$W/vicomap"

# 1. the sources: the trail map image steamboat.com's trail map page links (its largest JPEG rendition: ?w=6000
#    returns the full 2400 px as JPEG; without it the CDN sends WebP), and the interactive map's SVG
#    (resorts-interactive.com map 1800: its trail lines, names and symbols grouped by trail; plain curl).
#    steamboat.com's bot check (Incapsula) answers with a 212-byte page instead, to curl now and then and to every
#    client for a while after many requests: then curl is tried in headless Chromium from the page; if that is
#    blocked too, wait and run again (nothing is kept from a failed download)
IMG="https://www.steamboat.com/-/media/steamboat/maps/winter-26-27/winter-trail-map-final-2026-2027.jpg?w=6000"
is_jpeg() { [ "$(head -c 2 "$1" | od -An -tx1 | tr -d ' ')" = "ffd8" ]; }
if [ ! -f "$W/steamboat_2026-27.jpg" ]; then
  curl -sSfL -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36" \
    -H "Accept: image/jpeg,image/*;q=0.8" -o "$W/image.part" "$IMG"
  is_jpeg "$W/image.part" || PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-$(npm root -g)/playwright} node $T/fetch_pdf.cjs \
    https://www.steamboat.com/the-mountain/trail-map "$IMG" "$W/image.part" > /dev/null
  is_jpeg "$W/image.part" || { rm -f "$W/image.part"; echo "steamboat.com's bot check blocked the image: run again later" >&2; exit 1; }
  mv "$W/image.part" "$W/steamboat_2026-27.jpg"
fi
[ -f "$W/vicomap/map.svg" ] || curl -sSfL -o "$W/vicomap/map.svg" https://vicomap-cdn.resorts-interactive.com/map/1800/svg

# the files this data was built from: another file (a new edition, or the interactive map redrawn) stops the rebuild
# until its decisions are checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/steamboat_2026-27.jpg" 0adb46f41a4145e16794d9cbc9f9f3490950d977daeb581c445b31c603ddc068
check "$W/vicomap/map.svg" e66f6c948720001403d4d6dae698def313a90d22579e24a08dc9c2aa914d3e18

# 2. the map image, the line pieces (the SVG's lines routed onto the print's), names and symbols (prepare.py)
python3 $T/resorts/steamboat/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  cp "$W/steamboat_2026-27.jpg" public/maps/steamboat.jpg  # the resort's JPEG as it is (no second compression)
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py steamboat
