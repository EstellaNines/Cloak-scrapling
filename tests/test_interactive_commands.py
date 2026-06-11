from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from cloak_scrapling.browser_controller import BrowserElement, BrowserState
from cloak_scrapling.interactive import InteractiveShell, ShellState


class FakeController:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    async def open_url(self, url: str) -> dict[str, object]:
        self.calls.append(("open", url))
        return {"status": 200, "url": url, "title": "Fake Page"}

    async def state(self) -> BrowserState:
        self.calls.append(("state", None))
        return BrowserState(
            url="https://example.test",
            title="Fake Page",
            elements=[
                BrowserElement(index=1, tag="input", attributes={"placeholder": "Name"}),
                BrowserElement(index=2, tag="button", text="Save"),
            ],
        )

    async def input_text(self, index: int, text: str) -> dict[str, object]:
        self.calls.append(("input", (index, text)))
        return {"input": index, "text_length": len(text)}

    async def click(self, index: int) -> dict[str, object]:
        self.calls.append(("click", index))
        return {"clicked": index, "url": "https://example.test"}

    async def get_text(self, selector: str | None = None) -> str:
        self.calls.append(("text", selector))
        return "Saved"


class FakeBridge:
    cdp_url = "ws://127.0.0.1/devtools/browser/test"

    def __init__(self, controller: FakeController) -> None:
        self.controller = controller

    async def ensure_controller(self) -> FakeController:
        return self.controller


class InteractiveCommandTests(unittest.IsolatedAsyncioTestCase):
    async def test_dispatches_browser_interaction_commands(self) -> None:
        controller = FakeController()
        shell = InteractiveShell(ShellState(lang="en"))
        shell.bridge = FakeBridge(controller)  # type: ignore[assignment]

        output = io.StringIO()
        with redirect_stdout(output):
            await shell.dispatch("open https://example.test")
            await shell.dispatch("state")
            await shell.dispatch("input 1 Estella")
            await shell.dispatch("click 2")
            await shell.dispatch("text body")

        self.assertEqual(
            controller.calls,
            [
                ("open", "https://example.test"),
                ("state", None),
                ("input", (1, "Estella")),
                ("click", 2),
                ("text", "body"),
            ],
        )
        printed = output.getvalue()
        self.assertIn("Opened: https://example.test", printed)
        self.assertIn('[1]<input placeholder="Name" />', printed)
        self.assertIn("Saved", printed)


if __name__ == "__main__":
    unittest.main()
