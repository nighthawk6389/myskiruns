#!/bin/bash
# Schweitzer: rebuild the app data (src/data/resorts/schweitzer/) from the resort's trail-map images, its interactive
# maps' SVGs, the readings (resort.py, names.py, report.json) and each panel's decisions (panels/<panel>/). Run from
# anywhere; working files go to $SCHWEITZER_WORK (default work/schweitzer, git-ignored).
#
#   tools/trailmap/resorts/schweitzer/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/schweitzer/regen.sh   # also rewrite public/maps/schweitzer-<panel>.jpg
#   FORCE=1 ...                                           # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export SCHWEITZER_WORK=${SCHWEITZER_WORK:-$PWD/work/schweitzer}; W=$SCHWEITZER_WORK
mkdir -p "$W"

# 1. the sources (plain curl): the 2025-26 Schweitzer Bowl image schweitzer.com's maps page links (letter size,
#    3300x2550); its Outback Bowl image is 1920 px wide only, so skimap.org's 2024-25 one at 3300x2550, the same
#    artwork, is used (the 2025-26 one is kept to check that against: tools/archive/schweitzer/editions.py); and the
#    interactive maps (resorts-interactive.com maps 1826 and 1827)
M=https://www.schweitzer.com/-/media/schweitzer/pdfs-and-maps
[ -f "$W/schweitzer-bowl_2025-26.jpg" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/schweitzer-bowl_2025-26.jpg" \
  "$M/schweitzer-wintertrailmap-2025-26-1schweitzerbowl-lettersize.jpg"
[ -f "$W/outback-bowl_2025-26-web.jpg" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/outback-bowl_2025-26-web.jpg" \
  "$M/maps/schweitzer-wintertrailmap-2025-26-2outbackbowl-web1920.jpg"
[ -f "$W/outback-bowl_2024-25.webp" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/outback-bowl_2024-25.webp" \
  https://skimap.org/skimaps/view/30575
for id in 1826 1827; do
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
check "$W/schweitzer-bowl_2025-26.jpg" b7feff7b8237781d3c494a6c06e8512ca404382c862bac474da6e53c26571b3e  # 2120280 bytes
check "$W/outback-bowl_2025-26-web.jpg" e07ce08e27db947b0b55405682c5d44ad406137d946e8367095b050da8f53aea  # 937608 bytes
check "$W/outback-bowl_2024-25.webp" 1fa3d50b137210f09040b85c75ad451ff86ecf9e605622f9f68afe293cf9b354  # 1926980 bytes
check "$W/vicomap-1826/map.svg" 4ff0ac9e2c3a1d29d370ab29f1d4d8cac807bcff90f58159adcf8e1ab8e5e6b8  # 2516140 bytes
check "$W/vicomap-1827/map.svg" 32a65a37a0954b81e2aac858eef5657420cf90e010eda06d757c294ab0ed25c8  # 2645648 bytes

# 2. each panel's map image, its labels and symbols, its cat-track pieces (prepare.py)
python3 $T/resorts/schweitzer/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  for p in schweitzer-bowl outback-bowl; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/schweitzer-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece and label, then the trail list, proposals, Claude's reviews and the overlays, per panel
python3 $T/pdf_resort.py schweitzer
