from __future__ import annotations

import argparse
import asyncio
from collections.abc import Sequence


async def run_agent_cli(args: argparse.Namespace) -> int:
    """Run the lightweight Agent CLI shell."""
    if args.once:
        print("cloak-scrapling-agent: interactive UI is not wired yet.")
        print(f"received: {args.once}")
        return 0

    print("cloak-scrapling-agent: interactive UI is not wired yet.")
    print("Use --help to inspect the available startup flags.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Codex/Claude Code style Cloak-scrapling Agent CLI.",
    )
    parser.add_argument(
        "--headful",
        action="store_true",
        help="Run CloakBrowser visibly when browser commands are used.",
    )
    parser.add_argument(
        "--humanize",
        action="store_true",
        help="Enable CloakBrowser humanized actions.",
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Enable the colored sidecar console for browser events.",
    )
    parser.add_argument(
        "--once",
        help="Run one command and exit. Useful for smoke tests.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    raise SystemExit(asyncio.run(run_agent_cli(args)))


if __name__ == "__main__":
    main()
