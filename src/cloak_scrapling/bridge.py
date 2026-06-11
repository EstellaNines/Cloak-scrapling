from __future__ import annotations

import asyncio
import json
import os
import socket
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from .agent_console import AgentConsole
from .browser_core import BrowserCoreResolver
from .browser_controller import BrowserController


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


def _prepend_source_path(env_name: str, default_path: Path) -> None:
    source = Path(os.environ.get(env_name, default_path))
    if source.exists():
        source_text = str(source)
        if source_text not in sys.path:
            sys.path.insert(0, source_text)


def local_sources_enabled() -> bool:
    return os.environ.get("CLOAK_SCRAPLING_USE_LOCAL_SOURCES", "").strip().lower() in {"1", "true", "yes", "on"}


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


@dataclass(slots=True)
class CloakScraplingConfig:
    headless: bool = True
    cdp_host: str = "127.0.0.1"
    cdp_port: int | None = None
    browser_args: list[str] = field(default_factory=list)
    stealth_args: bool = True
    humanize: bool = False
    browser_kwargs: dict[str, Any] = field(default_factory=dict)
    console: bool | None = None
    console_title: str = "Cloak-scrapling Agent Console"
    console_log_dir: Path | None = None
    console_hold: bool | None = None


class CloakScraplingBridge:
    """Launch CloakBrowser and let Scrapling control it over CDP."""

    def __init__(self, config: CloakScraplingConfig | None = None) -> None:
        self.config = config or CloakScraplingConfig()
        self.browser: Any | None = None
        self.cdp_url: str | None = None
        self.controller: BrowserController | None = None
        self.console = AgentConsole(
            enabled=self.config.console,
            title=self.config.console_title,
            log_dir=self.config.console_log_dir,
            hold=self.config.console_hold,
        )

    async def __aenter__(self) -> "CloakScraplingBridge":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def start(self) -> str:
        self.console.start()
        prepare_local_sources()
        browser_core = BrowserCoreResolver()
        browser_core_info = browser_core.resolve()
        browser_core.apply_to_environment(browser_core_info)
        self.console.log(
            "browser_core",
            "browser core resolved",
            browser_core_provider=browser_core_info.provider,
            browser_core_path=browser_core_info.binary_path,
        )
        from cloakbrowser import launch_async

        port = self.config.cdp_port or find_free_port(self.config.cdp_host)
        args = [
            f"--remote-debugging-port={port}",
            f"--remote-debugging-address={self.config.cdp_host}",
            *self.config.browser_args,
        ]
        self.console.log(
            "launch",
            "launching CloakBrowser",
            headless=self.config.headless,
            humanize=self.config.humanize,
            cdp_host=self.config.cdp_host,
            cdp_port=port,
        )
        try:
            self.browser = await launch_async(
                headless=self.config.headless,
                args=args,
                stealth_args=self.config.stealth_args,
                humanize=self.config.humanize,
                **self.config.browser_kwargs,
            )
            self.cdp_url = await asyncio.to_thread(wait_for_cdp_ws_url, self.config.cdp_host, port)
            self.console.log("cdp", "CDP websocket ready", cdp_url=self.cdp_url)
        except Exception as exc:
            self.console.log("error", "failed to launch CloakBrowser", error=repr(exc))
            raise
        return self.cdp_url

    async def close(self) -> None:
        self.console.log("system", "closing bridge")
        try:
            if self.controller is not None:
                await self.controller.close()
                self.controller = None
            if self.browser is not None:
                await self.browser.close()
                self.browser = None
            self.cdp_url = None
        finally:
            self.console.close()

    async def fetch(self, url: str, **kwargs: Any) -> Any:
        if not self.cdp_url:
            raise RuntimeError("Bridge is not started. Use 'async with CloakScraplingBridge()'.")
        prepare_local_sources()
        from scrapling.fetchers import StealthyFetcher

        kwargs.setdefault("google_search", False)
        self.console.log("input", "direct fetch requested", url=url, options=kwargs)
        try:
            page = await StealthyFetcher.async_fetch(url, cdp_url=self.cdp_url, **kwargs)
            self.console.log("output", "direct fetch completed", **_summarize_page(page))
            return page
        except Exception as exc:
            self.console.log("error", "direct fetch failed", url=url, error=repr(exc))
            raise

    async def ensure_controller(self) -> BrowserController:
        if not self.cdp_url:
            await self.start()
        if not self.cdp_url:
            raise RuntimeError("CloakBrowser CDP endpoint is not ready.")
        if self.controller is None or self.controller.cdp_url != self.cdp_url:
            self.controller = BrowserController(
                self.cdp_url,
                default_screenshot_dir=PROJECT_ROOT / ".logs",
            )
        return self.controller

    async def mcp_stealthy_fetch(self, url: str, **kwargs: Any) -> Any:
        if not self.cdp_url:
            raise RuntimeError("Bridge is not started. Use 'async with CloakScraplingBridge()'.")
        prepare_local_sources()
        from scrapling.core.ai import ScraplingMCPServer

        kwargs.setdefault("google_search", False)
        server = ScraplingMCPServer()
        self.console.log("input", "MCP stealthy_fetch requested", url=url, options=kwargs)
        try:
            result = await server.stealthy_fetch(url, cdp_url=self.cdp_url, **kwargs)
            self.console.log("mcp", "MCP stealthy_fetch completed", **_summarize_mcp_result(result))
            return result
        except Exception as exc:
            self.console.log("error", "MCP stealthy_fetch failed", url=url, error=repr(exc))
            raise


def _summarize_page(page: Any) -> dict[str, Any]:
    title = None
    try:
        title = page.css("title::text").get()
    except Exception:
        title = None
    text = getattr(page, "text", "") or ""
    return {
        "status": getattr(page, "status", None),
        "url": getattr(page, "url", None),
        "title": title,
        "text_len": len(text),
        "preview": text[:160].replace("\n", " "),
    }


def _summarize_mcp_result(result: Any) -> dict[str, Any]:
    content = getattr(result, "content", []) or []
    joined = " ".join(str(item).strip() for item in content if str(item).strip())
    return {
        "status": getattr(result, "status", None),
        "url": getattr(result, "url", None),
        "items": len(content),
        "preview": joined[:200].replace("\n", " "),
    }
