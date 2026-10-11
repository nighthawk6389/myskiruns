#!/bin/bash
# Stevens Pass: rebuild the app data (src/data/resorts/stevens-pass/) from the resort's trail map PDF, the map's
# reading (resort.py, panels/*/resort.py, letters.json) and the naming decisions (panels/*/decisions.py). Run from
# anywhere; working files go to $STEVENS_PASS_WORK (default work/stevens-pass, git-ignored).
#
#   tools/trailmap/resorts/stevens-pass/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/stevens-pass/regen.sh   # also rewrite public/maps/stevens-pass-<panel>.jpg
#   FORCE=1 ...                                             # go on although the PDF's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export STEVENS_PASS_WORK=${STEVENS_PASS_WORK:-$PWD/work/stevens-pass}; W=$STEVENS_PASS_WORK
mkdir -p "$W"

# 1. the source: the winter trail map PDF stevenspass.com's trail-maps page links (the 2024-25 edition, the one it
#    still links; no 2025-26 file exists under the season's dated names). Vail Resorts' sites refuse curl: fetched
#    from inside the page in headless Chromium (tools/trailmap/fetch_pdf.cjs)
PAGE=https://www.stevenspass.com/the-mountain/about-the-mountain/trail-maps.aspx
[ -f "$W/sv_2024-25.pdf" ] || PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-$(npm root -g)/playwright} node $T/fetch_pdf.cjs "$PAGE" \
  https://www.stevenspass.com/-/aemasset/sitecore/stevens-pass/maps/winter-2024-2025/20241115_SV_winter-trail_map_001.pdf \
  "$W/sv_2024-25.pdf"

# the file this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/sv_2024-25.pdf" 1af2fcca3c2381897e0a658ffc8e6b32ab0cca7065ee866d892f03ae2ddaeb30  # 6272093 bytes

# 2. per panel: the map image, the line pieces, the names and the symbols (prepare.py)
python3 $T/resorts/stevens-pass/prepare.py
if [ -n "$IMAGES" ]; then
  for p in front-side mill-valley; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/stevens-pass-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece of every panel, then the trail list, and per panel the proposals, Claude's reviews and overlays
python3 $T/pdf_resort.py stevens-pass
