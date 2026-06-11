from __future__ import annotations

import argparse
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from cloak_scrapling.agent_cli import AgentCliApp
from cloak_scrapling.agent_cli_commands import parse_agent_command
from cloak_scrapling.agent_cli_models import AgentEvent, AgentStatus
from cloak_scrapling.agent_cli_renderer import AgentCliRenderer
from cloak_scrapling.browser_models import BrowserElement, BrowserState


class FakeCoreInfo:
    provider = "cache"


class FakeCssSelection:
    def getall(self) -> list[str]:
        return ["Fake Title"]


class FakePage:
    text = "Fake body"

    def css(self, selector: str) -> FakeCssSelection:
        return FakeCssSelection()


class FakeMCPResult:
    content = ["Fake MCP"]


class FakeSession:
    def __init__(self) -> None:
        self.cdp_url: str | None = None
        self.closed = False

    @property
    def browser_core_info(self) -> FakeCoreInfo:
        return FakeCoreInfo()

    async def start(self) -> str:
        self.cdp_url = "ws://127.0.0.1/devtools/browser/test"
        return self.cdp_url

    async def close(self) -> None:
        self.closed = True
        self.cdp_url = None

    async def open(self, url: str, timeout: int | float = 30000) -> dict[str, object]:
        return {"status": 200, "url": url, "title": "Fake"}

    async def state(self) -> BrowserState:
        return BrowserState(
            url="https://example.test",
            title="Fake",
            elements=[BrowserElement(index=1, tag="button", text="Go")],
        )

    async def fetch(self, url: str, **kwargs: object) -> FakePage:
        return FakePage()

    async def mcp_fetch(self, url: str, **kwargs: object) -> FakeMCPResult:
        return FakeMCPResult()

    async def get_text(self, selector: str | None = None) -> str:
        return selector or "body text"


def _args(**overrides: object) -> argparse.Namespace:
    values = {
        "headful": False,
        "humanize": False,
        "console": False,
        "once": None,
        "yes": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class AgentCliParserTests(unittest.TestCase):
    def test_parse_url_and_aliases(self) -> None:
        self.assertEqual(parse_agent_command("https://example.test").name, "open")
        self.assertEqual(parse_agent_command("q").name, "exit")
        self.assertEqual(parse_agent_command("/input 1 hello").args, ["1", "hello"])


class AgentCliRendererTests(unittest.TestCase):
    def test_plain_renderer_outputs_brand_banner(self) -> None:
        renderer = AgentCliRenderer()
        renderer._rich_available = False

        output = io.StringIO()
        with redirect_stdout(output):
            renderer.render_banner()

        printed = output.getvalue()
        self.assertIn("◈ Cloak Scrapling", printed)
        self.assertIn("Agent CLI / browser control / scraping", printed)

    def test_plain_renderer_outputs_event_and_status(self) -> None:
        renderer = AgentCliRenderer()
        renderer._rich_available = False

        output = io.StringIO()
        with redirect_stdout(output):
            renderer.render_event(AgentEvent(kind="system", message="ready"))
            renderer.render_status(AgentStatus(running=True, current_url="https://example.test"))

        printed = output.getvalue()
        self.assertIn("[system] ready", printed)
        self.assertIn("running=True", printed)

    def test_plain_renderer_uses_input_and_dot_event_shapes(self) -> None:
        renderer = AgentCliRenderer()
        renderer._rich_available = False

        output = io.StringIO()
        with redirect_stdout(output):
            renderer.render_event(AgentEvent(kind="user", message="/state"))
            renderer.render_event(AgentEvent(kind="result", message="page text"))
            renderer.render_event(
                AgentEvent(
                    kind="browser",
                    message="opened https://example.test",
                    details={"status": 200, "title": "Fake"},
                )
            )

        printed = output.getvalue()
        self.assertIn("› /state", printed)
        self.assertIn("● page text", printed)
        self.assertIn("● opened https://example.test status=200 title=Fake", printed)


class AgentCliFlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_open_state_fetch_and_close_use_session(self) -> None:
        session = FakeSession()
        app = AgentCliApp(_args(yes=True), session=session)

        opened = await app.dispatch("/open https://example.test")
        state = await app.dispatch("/state")
        fetched = await app.dispatch("/fetch https://example.test title")
        closed = await app.dispatch("/close")

        self.assertEqual(opened.events[0].kind, "browser")
        self.assertIn("[1]<button>Go</button>", state.events[0].message)
        self.assertEqual(fetched.events[0].message, "Fake Title")
        self.assertEqual(closed.events[0].message, "browser session closed")
        self.assertTrue(session.closed)

    async def test_close_without_confirmation_is_canceled(self) -> None:
        session = FakeSession()
        app = AgentCliApp(_args(yes=False), session=session)

        with patch.object(app, "_confirm", return_value=False):
            result = await app.dispatch("/close")

        self.assertEqual(result.events[0].message, "/close canceled")
        self.assertFalse(session.closed)

    async def test_run_once_echoes_user_input_before_result(self) -> None:
        session = FakeSession()
        renderer = AgentCliRenderer()
        renderer._rich_available = False
        app = AgentCliApp(_args(), renderer=renderer, session=session)

        output = io.StringIO()
        with redirect_stdout(output):
            await app.run_once("/open https://example.test")

        printed = output.getvalue()
        self.assertIn("› /open https://example.test", printed)
        self.assertIn("● opened https://example.test status=200 title=Fake", printed)


if __name__ == "__main__":
    unittest.main()
