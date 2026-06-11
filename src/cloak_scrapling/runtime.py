from __future__ import annotations

import json
import os
import socket
import sys
import time
from pathlib import Path
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOL_ROOT = PROJECT_ROOT.parent
DEFAULT_CLOAK_SOURCE = TOOL_ROOT / "CloakBrowser"
DEFAULT_SCRAPLING_SOURCE = TOOL_ROOT / "scrapling"


def default_cache_dir() -> Path:
    if os.environ.get("CLOAK_SCRAPLING_CACHE_DIR"):
        return Path(os.environ["CLOAK_SCRAPLING_CACHE_DIR"])
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "CloakScrapling" / "cloakbrowser"
    return Path.home() / ".cache" / "cloak-scrapling" / "cloakbrowser"


def local_sources_enabled() -> bool:
    return os.environ.get("CLOAK_SCRAPLING_USE_LOCAL_SOURCES", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def prepare_local_sources() -> None:
    """Prepare optional development source overrides and runtime cache env."""
    if local_sources_enabled():
        _prepend_source_path("CLOAKBROWSER_SOURCE_DIR", DEFAULT_CLOAK_SOURCE)
        _prepend_source_path("SCRAPLING_SOURCE_DIR", DEFAULT_SCRAPLING_SOURCE)
    os.environ.setdefault("CLOAKBROWSER_CACHE_DIR", str(default_cache_dir()))
    os.environ.setdefault("CLOAKBROWSER_AUTO_UPDATE", "false")


def find_free_port(host: str = "127.0.0.1") -> int:
    sock = socket.socket()
    try:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])
    finally:
        sock.close()


def wait_for_cdp_ws_url(host: str, port: int, timeout: float = 20.0) -> str:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urlopen(f"http://{host}:{port}/json/version", timeout=1) as response:
                data = json.loads(response.read())
            ws_url = data["webSocketDebuggerUrl"]
            if not ws_url.startswith(("ws://", "wss://")):
                raise RuntimeError(f"Scrapling requires a ws/wss CDP URL, got {ws_url!r}")
            return ws_url
        except Exception as exc:
            last_error = exc
            time.sleep(0.25)
    raise RuntimeError(f"CloakBrowser CDP endpoint did not become ready: {last_error!r}")


def _prepend_source_path(env_name: str, default_path: Path) -> None:
    source = Path(os.environ.get(env_name, default_path))
    if source.exists():
        source_text = str(source)
        if source_text not in sys.path:
            sys.path.insert(0, source_text)
