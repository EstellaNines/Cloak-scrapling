from __future__ import annotations

from .shell_commands import InteractiveShell, ShellState, build_parser, main


__all__ = [
    "InteractiveShell",
    "ShellState",
    "build_parser",
    "main",
]


if __name__ == "__main__":
    main()
