from __future__ import annotations

import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cloak_scrapling.ports import find_chrome_safe_port


HTML = b"""<!doctype html>
<html>
  <head><title>Installed Shell Smoke</title></head>
  <body><main id="app"><h1>Installed Shell OK</h1><p>entrypoint-ok</p></main></body>
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


def main() -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", find_chrome_safe_port()), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{httpd.server_address[1]}/installed"
    commands = "\n".join(
        [
            "lang en",
            f"fetch {url} title::text",
            f"mcp {url} #app",
            "exit",
            "",
        ]
    )

    try:
        proc = subprocess.run(
            ["cloak-scrapling-shell", "--lang", "zh"],
            input=commands,
            text=True,
            capture_output=True,
            check=False,
        )
        print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        if proc.returncode != 0:
            raise SystemExit(proc.returncode)
        required = ["Installed Shell Smoke", "MCP status: 200", "Installed Shell OK", "entrypoint-ok"]
        missing = [item for item in required if item not in proc.stdout]
        if missing:
            raise SystemExit(f"missing expected output: {missing}")
    finally:
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    main()
