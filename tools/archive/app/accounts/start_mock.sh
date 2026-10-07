#!/bin/bash
DIR=$(cd "$(dirname "$0")" && pwd)
cd /home/user/myskiruns
nohup node scripts/mockSupabase.cjs 54321 > "$DIR/mock.log" 2>&1 &
echo $! > "$DIR/mock.pid"
