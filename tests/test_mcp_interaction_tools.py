from __future__ import annotations

import unittest
import sys
import types

from cloak_scrapling.browser_controller import BrowserElement, BrowserState


fastmcp_module = types.ModuleType("mcp.server.fastmcp")


class DummyFastMCP:
    def add_tool(self, *args: object, **kwargs: object) -> None:
        pass

    def run(self, *args: object, **kwargs: object) -> None:
        pass


fastmcp_module.FastMCP = DummyFastMCP
sys.modules.setdefault("mcp", types.ModuleType("mcp"))
sys.modules.setdefault("mcp.server", types.ModuleType("mcp.server"))
sys.modules.setdefault("mcp.server.fastmcp", fastmcp_module)

from cloak_scrapling.mcp_server import CloakScraplingMCPServer


class FakeSession:
    cdp_url = "ws://127.0.0.1/devtools/browser/test"

    async def open(self, url: str, **kwargs: object) -> dict[str, object]:
        return {"status": 200, "url": url, "title": "Fake"}

    async def state(self) -> BrowserState:
        return BrowserState(
            url="https://example.test",
            title="Fake",
            elements=[BrowserElement(index=1, tag="button", text="Go")],
        )

    async def click(self, index: int) -> dict[str, object]:
        return {"clicked": index}

    async def input(self, index: int, text: str) -> dict[str, object]:
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


class MCPInteractionToolTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.server = CloakScraplingMCPServer()
        self.server.session = FakeSession()  # type: ignore[assignment]

    async def test_open_and_state_return_structured_results(self) -> None:
        opened = await self.server.open("https://example.test")
        state = await self.server.state()

        self.assertEqual(opened["status"], 200)
        self.assertEqual(state["elements"][0]["text"], "Go")
        self.assertIn("[1]<button>Go</button>", state["text"])

    async def test_action_tools_delegate_to_controller(self) -> None:
        self.assertEqual(await self.server.click(1), {"clicked": 1})
        self.assertEqual(await self.server.input(1, "abc"), {"input": 1, "text_length": 3})
        self.assertEqual(await self.server.press("Enter"), {"pressed": "Enter"})
        self.assertEqual(await self.server.scroll("down"), {"direction": "down"})
        self.assertEqual(await self.server.screenshot(), {"path": ".logs/screenshot-test.png"})
        self.assertEqual(await self.server.get_text("main"), {"content": "main"})
        self.assertEqual(await self.server.get_html("main"), {"content": "<div>main</div>"})


if __name__ == "__main__":
    unittest.main()
