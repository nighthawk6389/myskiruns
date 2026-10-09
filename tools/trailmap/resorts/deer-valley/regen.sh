#!/bin/bash
# Deer Valley: rebuild the app data (src/data/resorts/deer-valley/) from the 2025-26 trail map's two exports on
# skimap.org (the resort itself publishes only its interactive map), the map's reading (resort.py, letters.json,
# report.json) and the naming decisions (decisions.py). Run from anywhere; working files go to $DEER_VALLEY_WORK
# (default work/deer-valley, git-ignored).
#
#   tools/trailmap/resorts/deer-valley/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/deer-valley/regen.sh   # also rewrite public/maps/deer-valley.jpg
#   FORCE=1 ...                                            # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export DEER_VALLEY_WORK=${DEER_VALLEY_WORK:-$PWD/work/deer-valley}; W=$DEER_VALLEY_WORK
mkdir -p "$W"

# 1. the sources (skimap.org; plain curl): the vector PDF of 2025-10-16 (map 35124: lines, names, symbols) and the
#    flattened export of 2025-11-04 (map 40099: one 5301x3997 image in a PDF, the map image)
[ -f "$W/deervalley_2025-10.pdf" ] || curl -sSfL -o "$W/deervalley_2025-10.pdf" https://skimap.org/skimaps/view/35124
[ -f "$W/deervalley_2025-11.pdf" ] || curl -sSfL -o "$W/deervalley_2025-11.pdf" https://skimap.org/skimaps/view/40099

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are
# checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/deervalley_2025-10.pdf" 46b651b4678bf264fa8f5ffa88fd3490dd6182e1746020f63bca382e9eee59c4
check "$W/deervalley_2025-11.pdf" 300f73e821aa00242bf4003fc6a35cefb157d000117e3305d71fb6d02cdeff69
[ -f "$W/deervalley_2025-11.png" ] || python3 -I $T/extract_pdf_image.py "$W/deervalley_2025-11.pdf" \
  "$W/deervalley_2025-11.png" | tail -1 | sed "s#$W/##"

# 2. the map image (the November image's trail area), the line pieces, names and symbols (prepare.py)
python3 $T/resorts/deer-valley/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.MAX_IMAGE_PIXELS = None; Image.open('$W/map.png').convert('RGB').save('public/maps/deer-valley.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py deer-valley
