# yt-service

HTTP service that accepts a YouTube video link and returns playable MP4 URLs via yt-dlp.

## Endpoints

### `GET /health`

Health check.

```
curl http://localhost/health
# {"status":"ok"}
```

### `GET /extract?url=<youtube_url>`

```
curl "http://localhost/extract?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### `POST /extract`

```bash
curl -X POST http://localhost/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

Response:

```json
{
  "source": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "urls": [
    "https://rr1---sn-xxxx.googlevideo.com/videoplayback?..."
  ]
}
```

## Usage

```bash
python3 server.py
```

Run in the background:

```bash
./start.sh
```

Stop the background service:

```bash
./stop.sh
```

The scripts use `yt-service.pid` and `yt-service.log` by default. You can override
them with `PID_FILE` and `LOG_FILE`.

### Environment variables

| Variable | Default | Description |
|-----------|---------|-------------|
| `PORT` | 80 | Listen port |
| `YT_DLP_PATH` | yt-dlp | Path to yt-dlp binary |
| `YT_DLP_TIMEOUT` | 30 | Timeout in seconds |

## Requirements

- Python 3.8+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
