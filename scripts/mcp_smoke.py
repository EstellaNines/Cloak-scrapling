from __future__ import annotations

import asyncio
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cloak_scrapling import CloakScraplingBridge
from cloak_scrapling.ports import find_chrome_safe_port


HTML = b"""<!doctype html>
<html>
  <head><title>MCP Smoke</title></head>
  <body><main id="app"><h1>Agent MCP bridge OK</h1><p>mcp-stealthy-fetch-cdp</p></main></body>
</html>"""


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
        target = f"http://127.0.0.1:{httpd.server_address[1]}/agent"
        async with CloakScraplingBridge() as bridge:
            result = await bridge.mcp_stealthy_fetch(
                target,
                extraction_type="text",
                css_selector="#app",
                main_content_only=False,
                wait=100,
            )
            print("cdp_scheme=" + bridge.cdp_url.split(":", 1)[0])
            print("status=" + str(result.status))
            print("content=" + " ".join(item.strip() for item in result.content if item.strip()))
    finally:
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    asyncio.run(main())
