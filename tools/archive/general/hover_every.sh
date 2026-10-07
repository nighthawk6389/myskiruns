#!/bin/bash
cd /home/user/myskiruns
S=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad
node $S/offline/serve.cjs $S/dist-hover 4199 > $S/hover-server.log 2>&1 &
SP=$!
for i in $(seq 1 50); do curl -s -o /dev/null http://localhost:4199/ && break; python3 -c "import time; time.sleep(0.2)"; done
export PLAYWRIGHT_PATH=$(npm root -g)/playwright
for r in killington stowe okemo sugarbush jay-peak whiteface winter-park breckenridge copper-mountain keystone hunter wildcat sunday-river sugarloaf smugglers-notch; do
  echo "== $r $(node tools/trailmap/hover_check.cjs http://localhost:4199/ --resort $r 2>&1 | head -1)"
done
for p in front-side back-bowls blue-sky; do
  echo "== vail $p $(node tools/trailmap/hover_check.cjs http://localhost:4199/ --resort vail --panel $p 2>&1 | head -1)"
done
for p in main symphony glacier; do
  echo "== whistler-blackcomb $p $(node tools/trailmap/hover_check.cjs http://localhost:4199/ --resort whistler-blackcomb --panel $p 2>&1 | head -1)"
done
kill $SP
