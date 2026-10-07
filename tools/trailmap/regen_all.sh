#!/bin/bash
# Every resort's regen.sh (tools/trailmap/resorts/<id>/regen.sh), one after another, then whether git sees any change
# in that resort's data or map image: each should rebuild its files byte for byte. Run it after changing a shared
# tool (pdf_resort.py, pdf_glyphs.py, extract_pdf_vectors.py, traces_to_reviews.py, scripts/applyTrailProposals.mjs,
# ...): a change that shows up here alters a resort that was already checked, so look at it on crops.
#
#   tools/trailmap/regen_all.sh               # every resort that has a regen.sh, map images included
#   tools/trailmap/regen_all.sh hunter vail   # some
#   NO_IMAGES=1 tools/trailmap/regen_all.sh   # data only (leaves public/maps/ alone; faster)
#
# Each log goes to work/regen_<id>.log. A first run downloads each resort's sources into work/<id>/ (a few
# hundred MB in all).
cd "$(dirname "$0")/../.."
targets=("$@")
[ ${#targets[@]} -eq 0 ] && targets=($(ls tools/trailmap/resorts/*/regen.sh | awk -F/ '{print $(NF-1)}'))
mkdir -p work
status=0
for r in "${targets[@]}"; do
  start=$(date +%s)
  if [ -n "$NO_IMAGES" ]; then tools/trailmap/resorts/$r/regen.sh > "work/regen_$r.log" 2>&1
  else IMAGES=1 tools/trailmap/resorts/$r/regen.sh > "work/regen_$r.log" 2>&1; fi
  code=$?
  changed=$(git status --short -- "src/data/resorts/$r" public/maps/$r.jpg public/maps/$r-*.jpg 2>/dev/null)
  echo "== $r: exit $code in $(( $(date +%s) - start ))s; files changed: $(echo -n "$changed" | grep -c .)"
  [ -n "$changed" ] && echo "$changed" | head -8 | sed 's/^/     /'
  [ $code -ne 0 ] && tail -5 "work/regen_$r.log" | sed 's/^/     /'
  { [ $code -ne 0 ] || [ -n "$changed" ]; } && status=1
done
exit $status
