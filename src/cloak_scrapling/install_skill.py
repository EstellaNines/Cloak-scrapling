from __future__ import annotations

import argparse
import os
import shutil
from importlib.resources import files
from pathlib import Path


SKILL_NAME = "CloakScrapling-Skill"


def default_agent_home(agent: str) -> Path:
    if agent == "codex":
        return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    if agent == "claude":
        return Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    raise ValueError(f"unsupported agent: {agent}")


def install_skill(agent: str, target_root: Path | None = None, force: bool = False) -> Path:
    root = target_root or default_agent_home(agent)
    target = root / "skills" / SKILL_NAME
    root_resolved = root.resolve(strict=False)
    target_resolved = target.resolve(strict=False)
    if root_resolved == target_resolved or root_resolved not in target_resolved.parents:
        raise ValueError(f"Refusing to install outside target root: {target}")

    if target.exists():
        if not force:
            raise FileExistsError(f"{target} already exists. Re-run with --force to replace it.")
        if target.is_symlink():
            raise ValueError(f"Refusing to replace symlinked skill directory: {target}")
        shutil.rmtree(target)

    source = files("cloak_scrapling").joinpath("agent_skill")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    return target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install the Cloak-scrapling Agent Skill.")
    parser.add_argument("--agent", choices=["codex", "claude", "both"], default="codex")
    parser.add_argument("--target-root", type=Path, help="Override agent home directory. Skill is copied under <target>/skills/.")
    parser.add_argument("--force", action="store_true", help="Replace an existing installed skill.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    agents = ["codex", "claude"] if args.agent == "both" else [args.agent]
    for agent in agents:
        path = install_skill(agent, args.target_root, args.force)
        print(f"Installed {SKILL_NAME} for {agent}: {path}")


if __name__ == "__main__":
    main()
