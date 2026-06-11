from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from cloak_scrapling import browser_core_cli


class BrowserCoreCliTests(unittest.TestCase):
    def test_info_json_outputs_stable_shape(self) -> None:
        output = io.StringIO()

        with patch(
            "cloak_scrapling.browser_core_cli.resolve_browser_core_info",
            return_value={
                "platform": "linux-x64",
                "version": "146.0.7680.177.5",
                "provider": "download",
                "binary_path": "/cache/chromium-146/chrome",
                "installed": False,
                "cache_dir": "/cache/chromium-146",
                "vendor_dir": "/vendor/linux-x64",
            },
        ):
            with redirect_stdout(output):
                browser_core_cli.main(["info", "--json"])

        payload = json.loads(output.getvalue())
        self.assertEqual(payload["provider"], "download")
        self.assertFalse(payload["installed"])
        self.assertEqual(payload["platform"], "linux-x64")

    def test_install_delegates_to_cloakbrowser_ensure_binary(self) -> None:
        output = io.StringIO()

        with patch(
            "cloak_scrapling.browser_core_cli.ensure_browser_core",
            return_value="/cache/chromium/chrome",
        ) as ensure:
            with redirect_stdout(output):
                browser_core_cli.main(["install"])

        ensure.assert_called_once_with()
        self.assertIn("/cache/chromium/chrome", output.getvalue())

    def test_clear_cache_delegates_to_cloakbrowser_clear_cache(self) -> None:
        output = io.StringIO()

        with patch("cloak_scrapling.browser_core_cli.clear_browser_core_cache") as clear:
            with redirect_stdout(output):
                browser_core_cli.main(["clear-cache"])

        clear.assert_called_once_with()
        self.assertIn("Cache cleared", output.getvalue())


if __name__ == "__main__":
    unittest.main()
