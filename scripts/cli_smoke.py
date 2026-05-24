from __future__ import annotations

import asyncio
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cloak_scrapling.cli import _run, build_parser
from cloak_scrapling.ports import find_chrome_safe_port


HTML = b"<!doctype html><html><head><title>CLI Smoke</title></head><body>ok</body></html>"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(HTML)))
        self.end_headers()
        self.wfile.write(HTML)

    def log_message(self, format, *args):
        pass


async def main() -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", find_chrome_safe_port()), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        target = f"http://127.0.0.1:{httpd.server_address[1]}/"
        parser = build_parser()
        args = parser.parse_args([target, "--selector", "title::text"])
        await _run(args)
    finally:
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    asyncio.run(main())
