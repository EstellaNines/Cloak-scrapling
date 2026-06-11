from __future__ import annotations

import unittest
from unittest.mock import patch

from cloak_scrapling import CloakScraplingConfig, CloakScraplingSession
from cloak_scrapling.browser_core import BrowserCoreInfo
from cloak_scrapling.browser_models import BrowserElement, BrowserState


class FakeController:
    async def open_url(self, url: str, **kwargs: object) -> dict[str, object]:
        return {"status": 200, "url": url, "title": "Fake"}

    async def state(self) -> BrowserState:
        return BrowserState(
            url="https://example.test",
            title="Fake",
            elements=[BrowserElement(index=1, tag="button", text="Go")],
        )

    async def click(self, index: int) -> dict[str, object]:
        return {"clicked": index}

    async def input_text(self, index: int, text: str) -> dict[str, object]:
        return {"input": index, "text_length": len(text)}

    async def press(self, key: str) -> dict[str, object]:
        return {"pressed": key}

    async def scroll(self, direction: str) -> dict[str, object]:
        return {"direction": direction}

    async def screenshot(self, path: str | None = None) -> dict[str, object]:
        return {"path": path or ".logs/screenshot-test.png"}

    async def get_text(self, selector: str | None = None) -> str:
        return selector or "body text"

    async def get_html(self, selector: str | None = None) -> str:
        return f"<div>{selector or 'body'}</div>"


class FakePage:
    status = 200
    url = "https://example.test"
    text = "Fake page"


class FakeMCPResult:
    status = 200
    url = "https://example.test"
    content = ["Fake content"]


class FakeBridge:
    instances: list["FakeBridge"] = []

    def __init__(self, config: CloakScraplingConfig) -> None:
        self.config = config
        self.cdp_url: str | None = None
        self.controller = FakeController()
        self.started = 0
        self.closed = False
        FakeBridge.instances.append(self)

    async def start(self) -> str:
        self.started += 1
        self.cdp_url = "ws://127.0.0.1/devtools/browser/test"
        return self.cdp_url

    async def close(self) -> None:
        self.closed = True
        self.cdp_url = None

    async def fetch(self, url: str, **kwargs: object) -> FakePage:
        return FakePage()

    async def mcp_stealthy_fetch(self, url: str, **kwargs: object) -> FakeMCPResult:
        return FakeMCPResult()

    async def ensure_controller(self) -> FakeController:
        return self.controller


class FakeResolver:
    def resolve(self) -> BrowserCoreInfo:
        return BrowserCoreInfo(
            platform="linux-x64",
            version="146.0.7680.177.5",
            provider="cache",
            binary_path="/cache/chrome",
            installed=True,
            cache_dir="/cache",
            vendor_dir="/vendor",
        )


class SessionApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        FakeBridge.instances.clear()
        self.bridge_patcher = patch("cloak_scrapling.session.CloakScraplingBridge", FakeBridge)
        self.resolver_patcher = patch(
            "cloak_scrapling.session.BrowserCoreResolver",
            return_value=FakeResolver(),
        )
        self.bridge_patcher.start()
        self.resolver_patcher.start()

    async def asyncTearDown(self) -> None:
        self.resolver_patcher.stop()
        self.bridge_patcher.stop()

    async def test_session_reuses_bridge_for_fetch_and_page_actions(self) -> None:
        session = CloakScraplingSession(CloakScraplingConfig(headless=False))

        self.assertIsNone(session.cdp_url)
        self.assertEqual(await session.start(), "ws://127.0.0.1/devtools/browser/test")
        self.assertEqual(await session.start(), "ws://127.0.0.1/devtools/browser/test")
        self.assertEqual(FakeBridge.instances[0].started, 1)

        page = await session.fetch("https://example.test")
        mcp_result = await session.mcp_fetch("https://example.test")
        opened = await session.open("https://example.test")
        state = await session.state()

        self.assertEqual(page.status, 200)
        self.assertEqual(mcp_result.content, ["Fake content"])
        self.assertEqual(opened["title"], "Fake")
        self.assertEqual(state.elements[0].text, "Go")
        self.assertEqual(await session.click(1), {"clicked": 1})
        self.assertEqual(await session.input(1, "abc"), {"input": 1, "text_length": 3})
        self.assertEqual(await session.press("Enter"), {"pressed": "Enter"})
        self.assertEqual(await session.scroll("down"), {"direction": "down"})
        self.assertEqual(await session.screenshot(), {"path": ".logs/screenshot-test.png"})
        self.assertEqual(await session.get_text("main"), "main")
        self.assertEqual(await session.get_html("main"), "<div>main</div>")

    async def test_session_exposes_browser_core_info(self) -> None:
        session = CloakScraplingSession()

        info = session.browser_core_info

        self.assertEqual(info.provider, "cache")
        self.assertEqual(info.binary_path, "/cache/chrome")


if __name__ == "__main__":
    unittest.main()
