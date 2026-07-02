#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PID_FILE="${PID_FILE:-yt-service.pid}"

if [[ ! -f "$PID_FILE" ]]; then
    echo "yt-service is not running: missing $PID_FILE"
    exit 0
fi

PID="$(cat "$PID_FILE")"
if [[ -z "$PID" ]] || ! kill -0 "$PID" 2>/dev/null; then
    rm -f "$PID_FILE"
    echo "yt-service is not running: stale pid file removed"
    exit 0
fi

kill "$PID"

for _ in {1..10}; do
    if ! kill -0 "$PID" 2>/dev/null; then
        rm -f "$PID_FILE"
        echo "yt-service stopped (pid: $PID)"
        exit 0
    fi
    sleep 1
done

echo "yt-service did not stop after 10 seconds; sending SIGKILL" >&2
kill -9 "$PID" 2>/dev/null || true
rm -f "$PID_FILE"
echo "yt-service stopped (pid: $PID)"
