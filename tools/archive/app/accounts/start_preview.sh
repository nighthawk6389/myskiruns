#!/bin/bash
# start vite preview on the accounts test build; its PID goes to preview.pid
DIR=$(cd "$(dirname "$0")" && pwd)
cd /home/user/myskiruns
SUPABASE_URL=http://localhost:54321 VITE_SUPABASE_ANON_KEY=anon-key SUPABASE_SERVICE_ROLE_KEY=service-key \
  nohup node node_modules/vite/bin/vite.js preview --port 4310 --strictPort --outDir "$DIR/../dist-acct" > "$DIR/preview.log" 2>&1 &
echo $! > "$DIR/preview.pid"
