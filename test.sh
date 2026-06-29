#!/bin/bash
cd /Users/peter/dev/server/yt-service
python3 server.py &
SERVER_PID=$!
sleep 1

echo "=== Health check ==="
curl -s http://localhost:8080/health
echo ""

echo "=== Root ==="
curl -s http://localhost:8080/
echo ""

echo "=== Missing url param ==="
curl -s "http://localhost:8080/extract"
echo ""

echo "=== Invalid URL ==="
curl -s "http://localhost:8080/extract?url=not-a-youtube-link"
echo ""

echo "=== 404 ==="
curl -s http://localhost:8080/nonexistent
echo ""

kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
echo "=== Done ==="
