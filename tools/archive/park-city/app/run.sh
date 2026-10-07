#!/bin/bash
cd /home/user/myskiruns
S=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad
node $S/offline/serve.cjs $S/dist-hover 4199 > $S/hover-server.log 2>&1 &
SP=$!
for i in $(seq 1 50); do curl -s -o /dev/null http://localhost:4199/ && break; python3 -c "import time; time.sleep(0.2)"; done
PLAYWRIGHT_PATH=$(npm root -g)/playwright node $S/pcui/check.cjs http://localhost:4199/ $S/pcui 2>&1 | tail -20
kill $SP
