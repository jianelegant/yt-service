#!/bin/bash
cd /Users/peter/dev/server/yt-service
PORT="${PORT:-8080}"
python3 server.py &
SERVER_PID=$!
sleep 1

echo "=== Health check ==="
curl -s "http://localhost:${PORT}/health"
echo ""

echo "=== Missing url param ==="
curl -s "http://localhost:${PORT}/extract"
echo ""

echo "=== Invalid URL ==="
curl -s "http://localhost:${PORT}/extract?url=not-a-youtube-link"
echo ""

echo "=== Audio format param (GET) ==="
curl -s "http://localhost:${PORT}/extract?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&format=audio"
echo ""

echo "=== Audio format param (POST) ==="
curl -s -X POST "http://localhost:${PORT}/extract" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "format": "audio"}'
echo ""

echo "=== 404 ==="
curl -s "http://localhost:${PORT}/nonexistent"
echo ""

kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
echo "=== Done ==="
