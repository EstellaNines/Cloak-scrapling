from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"


class VendoredSourceTests(unittest.TestCase):
    def test_scrapling_and_cloakbrowser_resolve_from_repo_sources(self) -> None:
        for package_name in ("scrapling", "cloakbrowser"):
            with self.subTest(package_name=package_name):
                spec = importlib.util.find_spec(package_name)

                self.assertIsNotNone(spec)
                self.assertIsNotNone(spec.origin)
                origin = Path(str(spec.origin)).resolve()
                expected = SRC_ROOT / package_name / "__init__.py"
                self.assertEqual(origin, expected.resolve())

    def test_upstream_license_notices_are_kept_with_vendored_sources(self) -> None:
        expected_licenses = [
            PROJECT_ROOT / "third_party_licenses" / "SCRAPLING-BSD-3-CLAUSE.txt",
            PROJECT_ROOT / "third_party_licenses" / "CLOAKBROWSER-MIT.txt",
        ]

        for license_path in expected_licenses:
            with self.subTest(license_path=license_path.name):
                self.assertTrue(license_path.is_file(), license_path)

    def test_project_metadata_uses_vendored_sources_not_upstream_packages(self) -> None:
        pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertNotIn('"cloakbrowser>=', pyproject)
        self.assertNotIn('"scrapling[all]>=', pyproject)
        self.assertIn('"httpx>=0.24"', pyproject)
        self.assertIn('"lxml>=6.1.1"', pyproject)
        self.assertIn('"third_party_licenses/*"', pyproject)


if __name__ == "__main__":
    unittest.main()
