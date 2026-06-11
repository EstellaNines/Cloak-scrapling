from __future__ import annotations

from pathlib import Path
from typing import Any

from .bridge import CloakScraplingBridge, CloakScraplingConfig
from .browser_controller import BrowserController
from .browser_core import BrowserCoreInfo, BrowserCoreResolver
from .browser_models import BrowserState


class CloakScraplingSession:
    """Public facade for CloakBrowser launch, Scrapling fetch, and page control."""

    def __init__(self, config: CloakScraplingConfig | None = None) -> None:
        self.config = config or CloakScraplingConfig()
        self.bridge = CloakScraplingBridge(self.config)

    async def __aenter__(self) -> "CloakScraplingSession":
        await self.start()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.close()

    @property
    def cdp_url(self) -> str | None:
        return self.bridge.cdp_url

    @property
    def browser_core_info(self) -> BrowserCoreInfo:
        return BrowserCoreResolver().resolve()

    async def start(self) -> str:
        if self.bridge.cdp_url:
            return self.bridge.cdp_url
        return await self.bridge.start()

    async def close(self) -> None:
        await self.bridge.close()

    async def fetch(self, url: str, **kwargs: Any) -> Any:
        await self.start()
        return await self.bridge.fetch(url, **kwargs)

    async def mcp_fetch(self, url: str, **kwargs: Any) -> Any:
        await self.start()
        return await self.bridge.mcp_stealthy_fetch(url, **kwargs)

    async def mcp_stealthy_fetch(self, url: str, **kwargs: Any) -> Any:
        return await self.mcp_fetch(url, **kwargs)

    async def open(self, url: str, timeout: int | float = 30000) -> dict[str, Any]:
        controller = await self.ensure_controller()
        return await controller.open_url(url, timeout=timeout)

    async def state(self) -> BrowserState:
        controller = await self.ensure_controller()
        return await controller.state()

    async def click(self, index: int) -> dict[str, Any]:
        controller = await self.ensure_controller()
        return await controller.click(index)

    async def input(self, index: int, text: str) -> dict[str, Any]:
        controller = await self.ensure_controller()
        return await controller.input_text(index, text)

    async def press(self, key: str) -> dict[str, Any]:
        controller = await self.ensure_controller()
        return await controller.press(key)

    async def scroll(self, direction: str) -> dict[str, Any]:
        controller = await self.ensure_controller()
        return await controller.scroll(direction)

    async def screenshot(self, path: str | Path | None = None) -> dict[str, Any]:
        controller = await self.ensure_controller()
        return await controller.screenshot(path)

    async def get_text(self, selector: str | None = None) -> str:
        controller = await self.ensure_controller()
        return await controller.get_text(selector)

    async def get_html(self, selector: str | None = None) -> str:
        controller = await self.ensure_controller()
        return await controller.get_html(selector)

    async def ensure_controller(self) -> BrowserController:
        await self.start()
        return await self.bridge.ensure_controller()
