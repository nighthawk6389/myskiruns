#!/bin/bash
# Stratton: rebuild the app data (src/data/resorts/stratton/: trails.ts, linePolylines, trailProposals, trailReviews,
# trailPaths) from this season's flattened trail map PDF, the 2020-21 export of the same artwork (its lines, names and
# symbols), the map's reading (resort.py, report.json) and the naming decisions (decisions.py). Run from anywhere;
# working files go to $STRATTON_WORK (default work/stratton, git-ignored).
#
#   tools/trailmap/resorts/stratton/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/stratton/regen.sh   # also rewrite public/maps/stratton.jpg
#   FORCE=1 ...                                         # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export STRATTON_WORK=${STRATTON_WORK:-$PWD/work/stratton}; W=$STRATTON_WORK
mkdir -p "$W"

# 1. the sources (plain curl): the 2025-26 trail map PDF (stratton.com's trail maps page: the whole page one image)
#    and the 2020-21 trail map PDF (skimap.org map 20146: its lines, names and symbols live)
[ -f "$W/stratton_2025-26.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/stratton_2025-26.pdf" \
  'https://www.stratton.com/-/media/stratton/pdfs/maps/251021_wintermap.pdf'
[ -f "$W/stratton_2020-21.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/stratton_2020-21.pdf" \
  https://skimap.org/skimaps/view/20146

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/stratton_2025-26.pdf" 9e8e6ee27da6794201a341827f8dfb29b4d5ecd70f108b09fe8b64ae601aa81f  # 17682321 bytes
check "$W/stratton_2020-21.pdf" a2dff79d17994d11551613986d06c353f3a4fdbd2ba1ad1cfacf658adeebb656  # 11674750 bytes

# 2. the map image, the line pieces, the names and the symbols (prepare.py)
python3 $T/resorts/stratton/prepare.py
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.MAX_IMAGE_PIXELS = None; Image.open('$W/map.png').convert('RGB').save('public/maps/stratton.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py stratton
