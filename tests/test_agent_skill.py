from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cloak_scrapling.install_skill import SKILL_NAME, install_skill


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = PROJECT_ROOT / "src" / "cloak_scrapling" / "agent_skill" / "SKILL.md"


class AgentSkillTests(unittest.TestCase):
    def test_skill_guides_agents_through_automation_workflow(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("automated browser-backed scraping", skill)
        self.assertIn("MCP Automation Workflow", skill)
        self.assertIn("open(url)", skill)
        self.assertIn("state()", skill)
        self.assertIn("get_text(selector=None)", skill)
        self.assertIn("close_browser", skill)
        self.assertIn("reset_browser", skill)
        self.assertIn("CloakScraplingSession", skill)
        self.assertIn("Grey-backed `› /command`", skill)
        self.assertNotIn("future Codex", skill)

    def test_install_skill_copies_packaged_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)

            installed = install_skill("codex", target_root=target_root)

            installed_skill = installed / "SKILL.md"
            self.assertEqual(installed, target_root / "skills" / SKILL_NAME)
            self.assertTrue(installed_skill.is_file())
            self.assertIn("MCP Automation Workflow", installed_skill.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
