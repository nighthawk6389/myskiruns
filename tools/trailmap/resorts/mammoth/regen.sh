#!/bin/bash
# Mammoth Mountain: rebuild the app data (src/data/resorts/mammoth/) from the 2025-26 trail map PDF (skimap.org
# keeps the resort's two-page PDF; mammothmountain.com shows its trail map only in season), the resort's interactive
# maps' SVGs (the run lines, which the printed map doesn't draw), the map's reading (resort.py, report.json) and the
# naming decisions (panels/<panel>/decisions.py). Run from anywhere; working files go to $MAMMOTH_WORK (default
# work/mammoth, git-ignored).
#
#   tools/trailmap/resorts/mammoth/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/mammoth/regen.sh   # also rewrite public/maps/mammoth-<panel>.jpg
#   FORCE=1 ...                                        # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export MAMMOTH_WORK=${MAMMOTH_WORK:-$PWD/work/mammoth}; W=$MAMMOTH_WORK
mkdir -p "$W/vicomap" "$W/vicomap_back"

# 1. the sources (plain curl): the map PDF (skimap.org 42347; page 2 is the map) and the interactive maps' SVGs
#    (resorts-interactive.com map 1812, the whole mountain, and 1819, the back side: every run's line, grouped by
#    name, over the same paintings)
[ -f "$W/mammoth_2025-26.pdf" ] || curl -sSfL -o "$W/mammoth_2025-26.pdf" https://skimap.org/skimaps/view/42347
[ -f "$W/vicomap/map.svg" ] || curl -sSfL -o "$W/vicomap/map.svg" https://vicomap-cdn.resorts-interactive.com/map/1812/svg
[ -f "$W/vicomap_back/map.svg" ] || curl -sSfL -o "$W/vicomap_back/map.svg" \
  https://vicomap-cdn.resorts-interactive.com/map/1819/svg

# the files this data was built from: another file (a new edition, or an interactive map redrawn) stops the rebuild
# until its decisions are checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/mammoth_2025-26.pdf" 292c4728e625e3e26a6fba64d1718fb256c526c5abbc32291f8e42ce7e14ab94
check "$W/vicomap/map.svg" 273c0c5530b21fee5670821db0dd0165bd71f0181c9efd1706ca2ab7b46280a5
check "$W/vicomap_back/map.svg" 6d3ae1dc88ffc14031c3f71b79643b118f0141a70271374a6282c2036b576c7e

# 2. per panel the map image, the line pieces (the SVGs' lines), names and symbols (prepare.py)
python3 $T/resorts/mammoth/prepare.py | sed "s#$W/##"
if [ -n "$IMAGES" ]; then
  for p in main back-side; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/mammoth-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays of both panels
python3 $T/pdf_resort.py mammoth
