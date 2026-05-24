from __future__ import annotations

import asyncio
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cloak_scrapling.mcp_server import CloakScraplingMCPServer
from cloak_scrapling.ports import find_chrome_safe_port


HTML = b"""<!doctype html>
<html>
  <head><title>Package MCP Smoke</title></head>
  <body><main id="app"><h1>Package MCP OK</h1><p>one-click-agent-ready</p></main></body>
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


async def run() -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", find_chrome_safe_port()), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    server = CloakScraplingMCPServer()
    url = f"http://127.0.0.1:{httpd.server_address[1]}/mcp"
    try:
        status_before = await server.status()
        result = await server.fetch(url, extraction_type="text", css_selector="#app", main_content_only=False)
        status_after = await server.status()
        await server.close_browser()

        print(f"STATUS_BEFORE={status_before['running']}")
        print(f"STATUS_AFTER={status_after['running']}")
        print(f"RESULT_STATUS={result['status']}")
        print("CONTENT=" + " ".join(item.strip() for item in result["content"] if item.strip()))

        assert status_before["running"] is False
        assert status_after["running"] is True
        assert result["status"] == 200
        assert "Package MCP OK" in " ".join(result["content"])
        assert "one-click-agent-ready" in " ".join(result["content"])
    finally:
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    asyncio.run(run())
