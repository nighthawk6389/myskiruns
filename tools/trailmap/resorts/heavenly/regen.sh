#!/bin/bash
# Heavenly: rebuild the app data (src/data/resorts/heavenly/: one trail list, and per map panel in panels/<panel>/
# its pieces, proposals, reviews and overlays) from the 2024-25 map image and the 2022-23 PDF of the same artwork,
# the map's reading (resort.py, report.json, panels/<panel>/resort.py) and the naming decisions
# (panels/<panel>/decisions.py). Run from anywhere; working files go to $HEAVENLY_WORK (default work/heavenly,
# git-ignored).
#
#   tools/trailmap/resorts/heavenly/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/heavenly/regen.sh   # also rewrite public/maps/heavenly-*.jpg
#   FORCE=1 ...                                         # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export HEAVENLY_WORK=${HEAVENLY_WORK:-$PWD/work/heavenly}; W=$HEAVENLY_WORK
mkdir -p "$W"

# 1. sources: the 2024-25 map as skiheavenly.com shows it, from Vail Resorts' CDN (plain curl works there), and the
#    2022-23 PDF of the same artwork, whose lines, names and symbols are vector (skimap.org map 23043)
[ -f "$W/scene7.png" ] || curl -sSf -o "$W/scene7.png" \
  "https://scene7.vailresorts.com/is/image/vailresorts/20241105_HV_winter-trail_map_001?fmt=png-alpha&wid=3652&qlt=100"
[ -f "$W/heavenly_2022.pdf" ] || curl -sSfL -o "$W/heavenly_2022.pdf" https://files.skimap.org/dw0w5c12z2d8tkpabt7s2hvjhfzg.pdf

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are
# checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/scene7.png" 0fd24afcc31fb9612cf255a510b12b52071763421bc5aa1af86f9713f41704f2  # 33991393 bytes
check "$W/heavenly_2022.pdf" 22af0dae9ce0c50292a5d21b4ce7920edb8d865a194703f3d4ddeff1c7fcc02e  # 5443336 bytes

# 2. per panel: the map image (its part of the scene7 image), line pieces, names and symbols, on the image's grid
python3 $T/resorts/heavenly/prepare.py
if [ -n "$IMAGES" ]; then
  for p in main top-of-gondola; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/heavenly-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece of every panel, then the trail list, and per panel the proposals, Claude's reviews and overlays
python3 $T/pdf_resort.py heavenly
