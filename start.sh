#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PID_FILE="${PID_FILE:-yt-service.pid}"
LOG_FILE="${LOG_FILE:-yt-service.log}"
PORT="${PORT:-80}"

if [[ -f "$PID_FILE" ]]; then
    PID="$(cat "$PID_FILE")"
    if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
        echo "yt-service is already running (pid: $PID, port: $PORT)"
        exit 0
    fi
    rm -f "$PID_FILE"
fi

nohup env PORT="$PORT" YT_DLP_PATH="${YT_DLP_PATH:-yt-dlp}" YT_DLP_TIMEOUT="${YT_DLP_TIMEOUT:-30}" \
    python3 server.py >> "$LOG_FILE" 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"

sleep 1
if kill -0 "$PID" 2>/dev/null; then
    echo "yt-service started (pid: $PID, port: $PORT)"
    echo "log: $LOG_FILE"
else
    rm -f "$PID_FILE"
    echo "yt-service failed to start. Check $LOG_FILE" >&2
    exit 1
fi
