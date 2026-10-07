#!/bin/bash
cd /home/user/myskiruns
node /tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/offline/serve.cjs /tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/dist-hover 4199 > /tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/hover-server.log 2>&1 &
SP=$!
sleep 1
export PLAYWRIGHT_PATH=$(npm root -g)/playwright
for r in killington stowe okemo sugarbush jay-peak whiteface winter-park breckenridge copper-mountain keystone $EXTRA; do
  echo "== $r"; node tools/trailmap/hover_check.cjs http://localhost:4199/ --resort $r 2>&1 | head -1
done
for p in front-side back-bowls blue-sky; do
  echo "== vail $p"; node tools/trailmap/hover_check.cjs http://localhost:4199/ --resort vail --panel $p 2>&1 | head -1
done
kill $SP
