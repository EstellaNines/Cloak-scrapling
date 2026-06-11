from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from cloak_scrapling.shell_commands import InteractiveShell, ShellState


class ShellCommandRouterTests(unittest.IsolatedAsyncioTestCase):
    async def test_dispatch_handles_help_unknown_and_language_without_browser(self) -> None:
        shell = InteractiveShell(ShellState(lang="en"))

        output = io.StringIO()
        with redirect_stdout(output):
            self.assertFalse(await shell.dispatch("help"))
            self.assertFalse(await shell.dispatch("lang zh"))
            self.assertFalse(await shell.dispatch("missing-command"))

        printed = output.getvalue()
        self.assertIn("Commands:", printed)
        self.assertIn("语言已切换为中文。", printed)
        self.assertIn("未知命令：missing-command", printed)


if __name__ == "__main__":
    unittest.main()
