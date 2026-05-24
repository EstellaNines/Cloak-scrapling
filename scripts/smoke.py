from __future__ import annotations

import asyncio
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cloak_scrapling import CloakScraplingBridge
from cloak_scrapling.ports import find_chrome_safe_port


HTML = b"""<!doctype html>
<html>
  <head><title>Cloak Scrapling Smoke</title></head>
  <body>
    <main id="app">
      <h1>AI crawler bridge OK</h1>
      <ul>
        <li>alpha</li>
        <li>beta</li>
        <li>gamma</li>
      </ul>
      <p class="marker">cloak-scrapling-smoke</p>
    </main>
  </body>
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
        target = f"http://127.0.0.1:{httpd.server_address[1]}/products"
        async with CloakScraplingBridge() as bridge:
            page = await bridge.fetch(target, wait=100)
            print("cdp_scheme=" + bridge.cdp_url.split(":", 1)[0])
            print("title=" + str(page.css("title::text").get()))
            print("h1=" + str(page.css("h1::text").get()))
            print("items=" + "|".join(page.css("li::text").getall()))
            print("marker=" + str(page.css(".marker::text").get()))
    finally:
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    asyncio.run(main())
