#!/usr/bin/env python3
"""yt-service — extract playable MP4/audio links from YouTube URLs via yt-dlp."""

import json
import os
import re
import subprocess
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

YT_DLP = os.environ.get("YT_DLP_PATH", "yt-dlp")
PORT = int(os.environ.get("PORT", 8080))
TIMEOUT = int(os.environ.get("YT_DLP_TIMEOUT", 30))


def is_valid_youtube_url(url: str) -> bool:
    """Basic YouTube URL validation."""
    patterns = [
        r"^https?://(www\.)?youtube\.com/watch\?v=",
        r"^https?://youtu\.be/",
        r"^https?://(www\.)?youtube\.com/shorts/",
        r"^https?://(www\.)?youtube\.com/embed/",
    ]
    return any(re.search(p, url) for p in patterns)


def extract_urls(video_url: str, mode: str = "video") -> list[str]:
    """Run yt-dlp -g to extract direct media URLs.

    Args:
        video_url: YouTube video URL.
        mode: "video" (default) for MP4 video, "audio" for audio-only.
    """
    if mode == "audio":
        fmt = "bestaudio[ext=m4a]/bestaudio"
    else:
        fmt = "best[ext=mp4]/best"

    result = subprocess.run(
        [YT_DLP, "-g", "-f", fmt, "--no-playlist", video_url],
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(stderr or f"yt-dlp exited with code {result.returncode}")

    lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("yt-dlp returned no URLs")
    return lines


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTPServer with threading support for concurrent requests."""


class Handler(BaseHTTPRequestHandler):
    server_version = "yt-service/1.0"

    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, message: str, status: int = 400) -> None:
        self._send_json({"error": message}, status)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/health":
            self._send_json({"status": "ok"})
            return

        if parsed.path == "/extract":
            params = urllib.parse.parse_qs(parsed.query)
            url = params.get("url", [None])[0]
            if not url:
                self._send_error_json("Missing 'url' parameter", 400)
                return
            fmt = params.get("format", ["video"])[0]
            self._handle_extract(url, fmt)
            return

        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"yt-service: /extract?url=<youtube_url>[&format=audio]\n")
            return

        self._send_error_json("Not found", 404)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/extract":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_error_json("Invalid JSON body", 400)
                return

            url = data.get("url")
            if not url:
                self._send_error_json("Missing 'url' in JSON body", 400)
                return
            fmt = data.get("format", "video")
            self._handle_extract(url, fmt)
            return

        self._send_error_json("Not found", 404)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _handle_extract(self, url: str, fmt: str) -> None:
        if not is_valid_youtube_url(url):
            self._send_error_json("Invalid YouTube URL", 400)
            return

        try:
            urls = extract_urls(url, mode=fmt)
        except subprocess.TimeoutExpired:
            self._send_error_json("yt-dlp timed out", 504)
            return
        except RuntimeError as e:
            self._send_error_json(str(e), 502)
            return

        self._send_json({
            "source": url,
            "format": fmt,
            "urls": urls,
        })

    def log_message(self, format, *args):
        """Minimal logging to stderr."""
        print(f"[{self.log_date_time_string()}] {args[0]}", flush=True)


def main():
    server = ThreadedHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"yt-service listening on 0.0.0.0:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.", flush=True)
        server.shutdown()


if __name__ == "__main__":
    main()
