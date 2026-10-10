#!/bin/bash
# Big Bear Mountain Resort: rebuild the app data (src/data/resorts/big-bear/) from the resort's 2025-26 trail map
# images and its interactive maps, the maps' reading (resort.py, names.py, report.json, each panel's resort.py) and
# the naming decisions (each panel's decisions.py). Run from anywhere; working files go to $BIG_BEAR_WORK (default
# work/big-bear, git-ignored).
#
#   tools/trailmap/resorts/big-bear/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/big-bear/regen.sh   # also rewrite public/maps/big-bear-<panel>.jpg
#   FORCE=1 ...                                          # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export BIG_BEAR_WORK=${BIG_BEAR_WORK:-$PWD/work/big-bear}; W=$BIG_BEAR_WORK
mkdir -p "$W"

# 1. the sources (plain curl): the three 2025-26 winter trail map images the resort's trail-maps page links, and
#    the interactive maps (resorts-interactive.com maps 1818 Snow Summit, 1808 Bear Mountain, 1825 Snow Valley)
M=https://www.bigbearmountainresort.com/-/media/big-bear-mountain-resort-media/brand-assets/maps/winter-trail-maps
# (Snow Summit's: its CDN, Imperva, answers one request with its own WebP, the file this data was built from, and the
# next with the origin's JPEG of the same painting: fetched again, up to five times, until the WebP comes)
SS=2b055bd0628928a1230f591c5e67cb87fe4bf122162f55dbaba46879e1c8a238
for i in 1 2 3 4 5; do
  [ -f "$W/snow-summit_2025-26.webp" ] && [ "$(sha256sum "$W/snow-summit_2025-26.webp" | cut -d' ' -f1)" = $SS ] && break
  curl -sSfL -o "$W/snow-summit_2025-26.webp" \
    "$M/snow-summit-winter-trail-map-2500x1859-v2.jpg?rev=35eae3a350464524aeb238cc1646b932"
  sleep 2
done
[ -f "$W/bear-mountain_2025-26.jpg" ] || curl -sSfL -o "$W/bear-mountain_2025-26.jpg" \
  "$M/bear-mountain-winter-trail-map-2500x1770-v2.jpg?rev=36fddebfdcc24c288a0e1167515dba1f"
[ -f "$W/snow-valley_2025-26.png" ] || curl -sSfL -o "$W/snow-valley_2025-26.png" \
  "$M/2026-snow-valley-winter-trail-map-2400x1965-v3.png?rev=171029da93774f918650f9d14dd14c5a"
for id in 1818 1808 1825; do
  mkdir -p "$W/vicomap-$id"
  [ -f "$W/vicomap-$id/map.svg" ] || curl -sSfL -o "$W/vicomap-$id/map.svg" "https://vicomap-cdn.resorts-interactive.com/map/$id/svg"
  [ -f "$W/vicomap-$id/api.json" ] || curl -sSfL -o "$W/vicomap-$id/api.json" "https://vicomap-cdn.resorts-interactive.com/api/maps/$id"
done

# the files this data was built from: another file (a new edition) stops the rebuild until its readings are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its readings" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/snow-summit_2025-26.webp" $SS
check "$W/bear-mountain_2025-26.jpg" f01b1e24b3964b5b0a411e8f83bfca06122c035bf275fc3f216ec71a0c931d8c
check "$W/snow-valley_2025-26.png" 3c5a148db02d1ea48b5f757d60fe7727121fa9db991f52af5fcadf6c9bec2277
check "$W/vicomap-1818/map.svg" addcbc2e97774d8e140e54aeb4021afc1175fd4641998af1bb537a85180a1b01
check "$W/vicomap-1808/map.svg" f809eb39e026aedc9651b51dd822c92985b49f8d64e3168039fc792b3c3642b4
check "$W/vicomap-1825/map.svg" d04005844960a89331db7a231112b01f8070d16e00dd4dce5a407c02a8f527cd

# 2. each panel's map image, its labels and symbols, its line pieces (prepare.py)
python3 -I $T/resorts/big-bear/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  for p in snow-summit bear-mountain snow-valley; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/big-bear-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece and label, then the trail list, proposals, Claude's reviews and the overlays, per panel
python3 $T/pdf_resort.py big-bear
