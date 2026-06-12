from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROOT_PYPROJECT = PROJECT_ROOT / "pyproject.toml"
UV_PACKAGE_ROOT = PROJECT_ROOT / "packages" / "cloak-scrapling-mcp"
UV_PYPROJECT = UV_PACKAGE_ROOT / "pyproject.toml"


class MCPUvPackageTests(unittest.TestCase):
    def test_mcp_uv_package_matches_main_package_version_and_entrypoint(self) -> None:
        root = tomllib.loads(ROOT_PYPROJECT.read_text(encoding="utf-8"))
        wrapper = tomllib.loads(UV_PYPROJECT.read_text(encoding="utf-8"))
        version = root["project"]["version"]

        self.assertEqual(wrapper["project"]["name"], "cloak-scrapling-mcp")
        self.assertEqual(wrapper["project"]["version"], version)
        self.assertIn(f"cloak-scrapling=={version}", wrapper["project"]["dependencies"])
        self.assertEqual(
            wrapper["project"]["scripts"]["cloak-scrapling-mcp"],
            "cloak_scrapling_mcp:main",
        )
        self.assertEqual(
            wrapper["tool"]["uv"]["sources"]["cloak-scrapling"]["workspace"],
            True,
        )
        self.assertIn(
            "packages/cloak-scrapling-mcp",
            root["tool"]["uv"]["workspace"]["members"],
        )

    def test_uv_package_documentation_mentions_uvx_entrypoint(self) -> None:
        targets = [
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "README.en.md",
            PROJECT_ROOT / "src" / "cloak_scrapling" / "agent_skill" / "SKILL.md",
            PROJECT_ROOT / "docs" / "zh-CN" / "mcp" / "README.md",
            PROJECT_ROOT / "docs" / "en" / "mcp" / "README.md",
            UV_PACKAGE_ROOT / "README.md",
        ]

        for path in targets:
            with self.subTest(path=path):
                self.assertIn("uvx cloak-scrapling-mcp", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
