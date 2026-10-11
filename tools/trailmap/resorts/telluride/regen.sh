#!/bin/bash
# Telluride: rebuild the app data (src/data/resorts/telluride/: one trail list, and per map panel in
# panels/<panel>/ its pieces, proposals, reviews and overlays) from the 2024-25 trail map PDF (still the current
# one) and the resort's two inset images, the map's reading (resort.py, panels/<panel>/resort.py, letters.json,
# names.py, report.json) and the naming decisions (panels/<panel>/decisions.py). Run from anywhere; working files
# go to $TELLURIDE_WORK (default work/telluride, git-ignored).
#
#   tools/trailmap/resorts/telluride/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/telluride/regen.sh   # also rewrite public/maps/telluride-*.jpg
#   FORCE=1 ...                                               # go on although the PDF's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export TELLURIDE_WORK=${TELLURIDE_WORK:-$PWD/work/telluride}; W=$TELLURIDE_WORK
mkdir -p "$W"

# 1. the source (plain curl): the trail map PDF tellurideskiresort.com's mountain page links ("DOWNLOAD MAP PDF")
[ -f "$W/telluride_2024-25.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/telluride_2024-25.pdf" \
  'https://tellurideskiresort.com/wp-content/uploads/2425_TSR_Trail-Map_layered-trailmap.pdf'
# and the two inset images of the hike-to terrain the same page shows ("See Reverse for Detail" on the map)
for f in revvy-23.24-1.png palmyra-23.24.png; do
  [ -f "$W/$f" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/$f" "https://tellurideskiresort.com/wp-content/uploads/$f"
done

# the file this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/telluride_2024-25.pdf" 3b8f9daea9300aeb5dbe650f3aee6acd09bf9b7d51d4893c71c4390d7e98a38b  # 1211649 bytes
check "$W/revvy-23.24-1.png" 4d3ddef5e2c9970a92b993bd94908aae9108997f12c40318af7e9ee2e189f4d7  # 1873055 bytes
check "$W/palmyra-23.24.png" 75718679ed70b3056e05e8d8b06d5332c576e0fd0c5354ed5bfe1dc5023532dc  # 1753240 bytes

# 2. per panel: the map image, the line pieces, the names and the symbols (prepare.py)
python3 $T/resorts/telluride/prepare.py
if [ -n "$IMAGES" ]; then
  for p in main revelation black-iron-bowl; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/telluride-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece of every panel, then the trail list, and per panel the proposals, Claude's reviews and overlays
python3 $T/pdf_resort.py telluride
