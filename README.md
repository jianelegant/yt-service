# yt-service

HTTP service that accepts a YouTube video link and returns playable MP4 URLs via yt-dlp.

## Endpoints

### `GET /health`

Health check.

```
curl http://localhost:8080/health
# {"status":"ok"}
```

### `GET /extract?url=<youtube_url>`

```
curl "http://localhost:8080/extract?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### `POST /extract`

```bash
curl -X POST http://localhost:8080/extract \
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

### Environment variables

| Variable | Default | Description |
|-----------|---------|-------------|
| `PORT` | 8080 | Listen port |
| `YT_DLP_PATH` | yt-dlp | Path to yt-dlp binary |
| `YT_DLP_TIMEOUT` | 30 | Timeout in seconds |

## Requirements

- Python 3.8+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
