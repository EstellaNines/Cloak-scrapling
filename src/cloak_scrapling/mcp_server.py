from __future__ import annotations

import argparse
import asyncio
import atexit
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from .bridge import CloakScraplingBridge, CloakScraplingConfig


ExtractionType = Literal["markdown", "html", "text"]


class CloakScraplingMCPServer:
    def __init__(self, config: CloakScraplingConfig | None = None) -> None:
        self.config = config or CloakScraplingConfig()
        self.bridge: CloakScraplingBridge | None = None

    async def _ensure_bridge(self) -> CloakScraplingBridge:
        if self.bridge and self.bridge.cdp_url:
            return self.bridge
        self.bridge = CloakScraplingBridge(self.config)
        await self.bridge.start()
        return self.bridge

    async def _ensure_controller(self) -> Any:
        bridge = await self._ensure_bridge()
        return await bridge.ensure_controller()

    async def status(self) -> dict[str, Any]:
        """Return the current CloakBrowser/Scrapling bridge status."""
        return {
            "running": bool(self.bridge and self.bridge.cdp_url),
            "cdp_url": self.bridge.cdp_url if self.bridge else None,
            "headless": self.config.headless,
            "humanize": self.config.humanize,
            "console": self.config.console,
        }

    async def fetch(
        self,
        url: str,
        extraction_type: ExtractionType = "markdown",
        css_selector: str | None = None,
        main_content_only: bool = True,
        wait: int | float = 100,
        timeout: int | float = 30000,
        network_idle: bool = False,
    ) -> dict[str, Any]:
        """Fetch a URL through CloakBrowser-backed Scrapling and return extracted content."""
        bridge = await self._ensure_bridge()
        result = await bridge.mcp_stealthy_fetch(
            url,
            extraction_type=extraction_type,
            css_selector=css_selector,
            main_content_only=main_content_only,
            wait=wait,
            timeout=timeout,
            network_idle=network_idle,
        )
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return {"status": result.status, "url": result.url, "content": result.content}

    async def open(self, url: str, timeout: int | float = 30000) -> dict[str, Any]:
        """Open a URL in the live browser page."""
        controller = await self._ensure_controller()
        return await controller.open_url(url, timeout=timeout)

    async def state(self) -> dict[str, Any]:
        """Return indexed interactive elements for the current page."""
        controller = await self._ensure_controller()
        return (await controller.state()).to_dict()

    async def click(self, index: int) -> dict[str, Any]:
        """Click an element from the latest state result by index."""
        controller = await self._ensure_controller()
        return await controller.click(index)

    async def input(self, index: int, text: str) -> dict[str, Any]:
        """Fill an element from the latest state result by index."""
        controller = await self._ensure_controller()
        return await controller.input_text(index, text)

    async def press(self, key: str) -> dict[str, Any]:
        """Send a keyboard key to the current page."""
        controller = await self._ensure_controller()
        return await controller.press(key)

    async def scroll(self, direction: str) -> dict[str, Any]:
        """Scroll the current page up or down."""
        controller = await self._ensure_controller()
        return await controller.scroll(direction)

    async def screenshot(self, path: str | None = None) -> dict[str, Any]:
        """Save a full-page screenshot."""
        controller = await self._ensure_controller()
        return await controller.screenshot(path)

    async def get_text(self, selector: str | None = None) -> dict[str, Any]:
        """Return text from the page or a CSS selector."""
        controller = await self._ensure_controller()
        return {"content": await controller.get_text(selector)}

    async def get_html(self, selector: str | None = None) -> dict[str, Any]:
        """Return HTML from the page or a CSS selector."""
        controller = await self._ensure_controller()
        return {"content": await controller.get_html(selector)}

    async def close_browser(self) -> dict[str, Any]:
        """Close the current CloakBrowser browser session."""
        if self.bridge is not None:
            await self.bridge.close()
            self.bridge = None
        return {"closed": True}

    async def reset_browser(self) -> dict[str, Any]:
        """Close and recreate the browser on the next fetch call."""
        await self.close_browser()
        return {"reset": True}

    def register(self, server: FastMCP) -> None:
        server.add_tool(self.status, title="status", structured_output=True)
        server.add_tool(self.fetch, title="fetch", structured_output=True)
        server.add_tool(self.open, title="open", structured_output=True)
        server.add_tool(self.state, title="state", structured_output=True)
        server.add_tool(self.click, title="click", structured_output=True)
        server.add_tool(self.input, title="input", structured_output=True)
        server.add_tool(self.press, title="press", structured_output=True)
        server.add_tool(self.scroll, title="scroll", structured_output=True)
        server.add_tool(self.screenshot, title="screenshot", structured_output=True)
        server.add_tool(self.get_text, title="get_text", structured_output=True)
        server.add_tool(self.get_html, title="get_html", structured_output=True)
        server.add_tool(self.close_browser, title="close_browser", structured_output=True)
        server.add_tool(self.reset_browser, title="reset_browser", structured_output=True)

    def close_sync(self) -> None:
        if self.bridge is None:
            return
        try:
            asyncio.run(self.close_browser())
        except RuntimeError:
            pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Cloak-scrapling MCP server.")
    parser.add_argument("--http", action="store_true", help="Use streamable-http transport instead of stdio.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--headful", action="store_true", help="Run CloakBrowser visibly.")
    parser.add_argument("--humanize", action="store_true", help="Enable CloakBrowser humanized actions.")
    parser.add_argument("--console", action="store_true", help="Open the colored Agent sidecar console.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = CloakScraplingConfig(
        headless=not args.headful,
        humanize=args.humanize,
        console=True if args.console else None,
        console_title="Cloak-scrapling MCP Console",
    )
    tools = CloakScraplingMCPServer(config)
    atexit.register(tools.close_sync)

    server = FastMCP(name="CloakScrapling", host=args.host, port=args.port)
    tools.register(server)
    server.run(transport="streamable-http" if args.http else "stdio")


if __name__ == "__main__":
    main()
