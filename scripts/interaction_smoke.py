from __future__ import annotations

import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cloak_scrapling.ports import find_chrome_safe_port


HTML = b"""<!doctype html>
<html>
  <head><title>Interaction Smoke</title></head>
  <body>
    <main id="app">
      <input id="name" placeholder="Name" />
      <button id="save" onclick="
        document.querySelector('#status').textContent =
          'Saved ' + document.querySelector('#name').value
      ">Save</button>
      <textarea id="notes" placeholder="Notes"></textarea>
      <select id="kind"><option>Alpha</option><option>Beta</option></select>
      <p id="status">Waiting</p>
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


def main() -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", find_chrome_safe_port()), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{httpd.server_address[1]}/interaction"
    commands = "\n".join(
        [
            f"open {target}",
            "state",
            "input 1 Estella",
            "click 2",
            "text #status",
            "exit",
            "",
        ]
    )

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "cloak_scrapling.interactive", "--lang", "en"],
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
        required = [
            "Opened:",
            '[1]<input',
            "[2]<button>Save</button>",
            "Saved Estella",
        ]
        missing = [item for item in required if item not in proc.stdout]
        if missing:
            raise SystemExit(f"missing expected output: {missing}")
    finally:
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    main()
