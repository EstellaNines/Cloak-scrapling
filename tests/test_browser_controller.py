from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cloak_scrapling.browser_controller import (
    BrowserController,
    BrowserElement,
    BrowserState,
)


class BrowserControllerFormattingTests(unittest.TestCase):
    def test_state_text_uses_compact_indexed_elements(self) -> None:
        state = BrowserState(
            url="https://example.test/login",
            title="Login",
            elements=[
                BrowserElement(
                    index=1,
                    tag="input",
                    text="",
                    attributes={"type": "email", "placeholder": "Email"},
                ),
                BrowserElement(
                    index=2,
                    tag="button",
                    text="Sign in",
                    attributes={"role": "button"},
                ),
            ],
        )

        self.assertEqual(
            state.to_text(),
            "\n".join(
                [
                    "url=https://example.test/login",
                    "title=Login",
                    "",
                    '[1]<input type="email" placeholder="Email" />',
                    '[2]<button role="button">Sign in</button>',
                ]
            ),
        )

    def test_default_screenshot_path_uses_logs_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            controller = BrowserController(
                "ws://127.0.0.1/devtools/browser/test",
                default_screenshot_dir=Path(tmpdir) / ".logs",
            )

            path = controller.default_screenshot_path()

            self.assertEqual(path.parent, Path(tmpdir) / ".logs")
            self.assertRegex(path.name, r"^screenshot-\d{8}-\d{6}\.png$")

    def test_scroll_delta_accepts_only_supported_directions(self) -> None:
        self.assertEqual(BrowserController.scroll_delta("down"), 800)
        self.assertEqual(BrowserController.scroll_delta("up"), -800)

        with self.assertRaisesRegex(ValueError, "direction must be 'up' or 'down'"):
            BrowserController.scroll_delta("left")


if __name__ == "__main__":
    unittest.main()
