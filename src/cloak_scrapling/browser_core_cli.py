from __future__ import annotations

import argparse
import json
from typing import Sequence

from .browser_core import (
    clear_browser_core_cache,
    ensure_browser_core,
    resolve_browser_core_info,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage the Cloak-scrapling browser core."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    info = sub.add_parser("info", help="Show browser core resolution details.")
    info.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    sub.add_parser("install", help="Download/install the current platform browser core.")
    sub.add_parser("clear-cache", help="Clear the CloakBrowser binary cache.")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.command == "info":
        info = resolve_browser_core_info()
        if args.json:
            print(json.dumps(info, indent=2, sort_keys=True))
            return
        _print_info(info)
        return

    if args.command == "install":
        print(ensure_browser_core())
        return

    if args.command == "clear-cache":
        clear_browser_core_cache()
        print("Cache cleared.")
        return

    raise RuntimeError(f"Unhandled command: {args.command}")


def _print_info(info: dict[str, str | bool]) -> None:
    print(f"Platform:  {info['platform']}")
    print(f"Version:   {info['version']}")
    print(f"Provider:  {info['provider']}")
    print(f"Binary:    {info['binary_path']}")
    print(f"Installed: {info['installed']}")
    print(f"Cache:     {info['cache_dir']}")
    print(f"Vendor:    {info['vendor_dir']}")


if __name__ == "__main__":
    main()
