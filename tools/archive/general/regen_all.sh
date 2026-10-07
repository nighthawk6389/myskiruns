#!/bin/bash
# rerun every other PDF resort's regen.sh (with images) and report whether git sees any change
cd /home/user/myskiruns
S=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad
for r in hunter wildcat sunday-river sugarloaf smugglers-notch whistler-blackcomb park-city palisades-tahoe big-sky; do
  start=$(date +%s)
  IMAGES=1 tools/trailmap/resorts/$r/regen.sh > $S/regen_$r.log 2>&1
  echo "== $r exit $? in $(( $(date +%s) - start ))s; changed: $(git status --short -- src public | wc -l)"
  git status --short -- src public | head -5
done
