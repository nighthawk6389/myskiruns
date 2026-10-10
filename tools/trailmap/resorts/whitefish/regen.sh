#!/bin/bash
# Whitefish Mountain Resort: rebuild the app data (src/data/resorts/whitefish/) from the resort's trail-map JPEGs, the
# map's reading (names.py: every name, its symbol and its run's line as points read on crops), the trail report
# (report.json) and the panels' decisions. Run from anywhere; working files go to $WHITEFISH_WORK (default
# work/whitefish, git-ignored).
#
#   tools/trailmap/resorts/whitefish/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/whitefish/regen.sh   # also rewrite public/maps/whitefish-<panel>.jpg
#   FORCE=1 ...                                          # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export WHITEFISH_WORK=${WHITEFISH_WORK:-$PWD/work/whitefish}; W=$WHITEFISH_WORK
mkdir -p "$W"

# 1. the sources (plain curl): the JPEGs skiwhitefish.com's trail-maps page shows (no PDF is published)
U=https://skiwhitefish.com/wp-content/uploads
for f in 2025/11/W2526_FrontSide_Web.jpg 2024/11/W2425_NorthSide.jpg 2024/11/W2425_OtherSides.jpg; do
  [ -f "$W/$(basename $f)" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/$(basename $f)" "$U/$f"
done

# the files this data was built from: another file (a new edition) stops the rebuild until its reading is checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its reading" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/W2526_FrontSide_Web.jpg" 2023e084c6c82b89513090c0ec84548ada7382caf934b8ce13cebb3834e1babb  # 384155 bytes
check "$W/W2425_NorthSide.jpg" c6c0881bc5f56256a157f8c3d687add68d21b92ec63ffb26f8adb1b6c675f9ca  # 557607 bytes
check "$W/W2425_OtherSides.jpg" d44f499dfb12c740403fbf3234c140a9e7f6f503c70d2d741ea1da0b275b3f4d  # 492194 bytes

# 2. each panel's map image (the JPEG at 2x) and its line pieces (names.py's lines routed on the painted ones)
python3 $T/resorts/whitefish/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  for p in front-side north-side hellroaring; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/whitefish-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays, per panel
python3 $T/pdf_resort.py whitefish
