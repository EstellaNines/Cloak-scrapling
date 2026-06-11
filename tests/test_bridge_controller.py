from __future__ import annotations

import unittest
import os
import sys
import types
from pathlib import Path
from unittest.mock import patch

from cloak_scrapling.bridge import CloakScraplingBridge


class FakeController:
    instances: list["FakeController"] = []

    def __init__(self, cdp_url: str, *, default_screenshot_dir: Path) -> None:
        self.cdp_url = cdp_url
        self.default_screenshot_dir = default_screenshot_dir
        self.closed = False
        FakeController.instances.append(self)

    async def close(self) -> None:
        self.closed = True


class FakeBrowserCoreInfo:
    provider = "vendor"
    binary_path = "/vendor/linux-x64/chrome"

    def to_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "binary_path": self.binary_path,
            "installed": True,
        }


class BridgeControllerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        FakeController.instances.clear()
        self.env_patcher = patch.dict(os.environ, {}, clear=True)
        self.env_patcher.start()

    async def asyncTearDown(self) -> None:
        self.env_patcher.stop()

    async def test_ensure_controller_reuses_current_cdp_url(self) -> None:
        bridge = CloakScraplingBridge()
        bridge.cdp_url = "ws://127.0.0.1/devtools/browser/test"

        with patch("cloak_scrapling.bridge.BrowserController", FakeController):
            first = await bridge.ensure_controller()
            second = await bridge.ensure_controller()

        self.assertIs(first, second)
        self.assertEqual(first.cdp_url, "ws://127.0.0.1/devtools/browser/test")
        self.assertEqual(first.default_screenshot_dir.name, ".logs")
        self.assertEqual(len(FakeController.instances), 1)

    async def test_close_closes_controller(self) -> None:
        bridge = CloakScraplingBridge()
        bridge.controller = FakeController(
            "ws://127.0.0.1/devtools/browser/test",
            default_screenshot_dir=Path(".logs"),
        )

        await bridge.close()

        self.assertTrue(FakeController.instances[0].closed)
        self.assertIsNone(bridge.controller)

    async def test_start_prepares_browser_core_before_launch(self) -> None:
        launch_calls: list[dict[str, object]] = []

        async def fake_launch_async(**kwargs: object) -> object:
            launch_calls.append(dict(kwargs))

            class Browser:
                async def close(self) -> None:
                    pass

            return Browser()

        class FakeResolver:
            def resolve(self) -> FakeBrowserCoreInfo:
                return FakeBrowserCoreInfo()

            def apply_to_environment(self, info: FakeBrowserCoreInfo) -> None:
                os.environ["CLOAKBROWSER_BINARY_PATH"] = str(info.binary_path)

        fake_cloakbrowser = types.ModuleType("cloakbrowser")
        fake_cloakbrowser.launch_async = fake_launch_async

        with patch.dict(sys.modules, {"cloakbrowser": fake_cloakbrowser}):
            with patch("cloak_scrapling.bridge.BrowserCoreResolver", return_value=FakeResolver()):
                with patch("cloak_scrapling.bridge.find_free_port", return_value=9222):
                    with patch("cloak_scrapling.bridge.wait_for_cdp_ws_url", return_value="ws://127.0.0.1/devtools/browser/test"):
                        bridge = CloakScraplingBridge()
                        cdp_url = await bridge.start()

        self.assertEqual(cdp_url, "ws://127.0.0.1/devtools/browser/test")
        self.assertEqual(os.environ["CLOAKBROWSER_BINARY_PATH"], "/vendor/linux-x64/chrome")
        self.assertEqual(len(launch_calls), 1)


if __name__ == "__main__":
    unittest.main()
