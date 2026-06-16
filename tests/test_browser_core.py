from __future__ import annotations

import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from cloak_scrapling.browser_core import (
    BrowserCoreResolver,
    clear_browser_core_cache,
    ensure_browser_core,
)


def _expected_cache_suffix() -> str:
    """Platform-aware tail of the default cache dir.

    On Windows the default lands under ``LOCALAPPDATA`` (``CloakScrapling\\
    cloakbrowser``); on POSIX it lands under ``~/.cache``. Tests assert the
    tail rather than an absolute path so they hold on either OS.
    """
    if os.name == "nt":
        return os.path.join("CloakScrapling", "cloakbrowser")
    return os.path.join(".cache", "cloak-scrapling", "cloakbrowser")


class BrowserCoreResolverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.env_patcher = patch.dict(os.environ, {}, clear=True)
        self.env_patcher.start()
        self.addCleanup(self.env_patcher.stop)

    def test_env_binary_path_wins_even_when_missing(self) -> None:
        os.environ["CLOAKBROWSER_BINARY_PATH"] = "/missing/chrome"

        info = BrowserCoreResolver(
            platform_tag="linux-x64",
            chromium_version="146.0.7680.177.5",
        ).resolve()

        self.assertEqual(info.provider, "env")
        self.assertEqual(info.binary_path, "/missing/chrome")
        self.assertFalse(info.installed)

    def test_vendor_binary_sets_cloakbrowser_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vendor_root = Path(tmpdir) / "vendor_browser"
            chrome = vendor_root / "linux-x64" / "chrome"
            chrome.parent.mkdir(parents=True)
            chrome.write_text("#!/bin/sh\n", encoding="utf-8")
            chrome.chmod(0o755)

            resolver = BrowserCoreResolver(
                platform_tag="linux-x64",
                chromium_version="146.0.7680.177.5",
                vendor_root=vendor_root,
            )
            info = resolver.resolve()
            resolver.apply_to_environment(info)

            self.assertEqual(info.provider, "vendor")
            self.assertEqual(info.binary_path, str(chrome))
            self.assertTrue(info.installed)
            self.assertEqual(os.environ["CLOAKBROWSER_BINARY_PATH"], str(chrome))

    def test_cache_binary_wins_before_download_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_root = Path(tmpdir) / "cache"
            chrome = cache_root / "chromium-146.0.7680.177.5" / "chrome"
            chrome.parent.mkdir(parents=True)
            chrome.write_text("#!/bin/sh\n", encoding="utf-8")
            chrome.chmod(0o755)

            info = BrowserCoreResolver(
                platform_tag="linux-x64",
                chromium_version="146.0.7680.177.5",
                cache_root=cache_root,
                vendor_root=Path(tmpdir) / "empty-vendor",
            ).resolve()

            self.assertEqual(info.provider, "cache")
            self.assertEqual(info.binary_path, str(chrome))
            self.assertTrue(info.installed)

    def test_missing_binary_reports_download_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            info = BrowserCoreResolver(
                platform_tag="linux-x64",
                chromium_version="146.0.7680.177.5",
                cache_root=Path(tmpdir) / "cache",
                vendor_root=Path(tmpdir) / "vendor",
            ).resolve()

            self.assertEqual(info.provider, "download")
            self.assertFalse(info.installed)
            self.assertIn("chromium-146.0.7680.177.5", info.cache_dir)

    def test_install_sets_cloakbrowser_cache_dir_before_download(self) -> None:
        fake_package = types.ModuleType("cloakbrowser")
        fake_package.__path__ = []
        fake_download = types.ModuleType("cloakbrowser.download")
        calls: list[str] = []

        def fake_ensure_binary() -> str:
            calls.append(os.environ["CLOAKBROWSER_CACHE_DIR"])
            return "/cache/chromium/chrome"

        fake_download.ensure_binary = fake_ensure_binary

        with patch.dict(
            sys.modules,
            {"cloakbrowser": fake_package, "cloakbrowser.download": fake_download},
        ):
            path = ensure_browser_core()

        self.assertEqual(path, "/cache/chromium/chrome")
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0].endswith(_expected_cache_suffix()))

    def test_clear_cache_sets_cloakbrowser_cache_dir_before_clearing(self) -> None:
        fake_package = types.ModuleType("cloakbrowser")
        fake_package.__path__ = []
        fake_download = types.ModuleType("cloakbrowser.download")
        calls: list[str] = []

        def fake_clear_cache() -> None:
            calls.append(os.environ["CLOAKBROWSER_CACHE_DIR"])

        fake_download.clear_cache = fake_clear_cache

        with patch.dict(
            sys.modules,
            {"cloakbrowser": fake_package, "cloakbrowser.download": fake_download},
        ):
            clear_browser_core_cache()

        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0].endswith(_expected_cache_suffix()))


if __name__ == "__main__":
    unittest.main()
