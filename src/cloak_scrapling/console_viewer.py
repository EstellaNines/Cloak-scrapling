from __future__ import annotations

import argparse
import ctypes
import json
import os
import sys
import time
from pathlib import Path


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
COLORS = {
    "system": "\033[36m",
    "launch": "\033[95m",
    "cdp": "\033[94m",
    "fetch": "\033[92m",
    "mcp": "\033[96m",
    "input": "\033[93m",
    "output": "\033[32m",
    "error": "\033[91m",
}


def enable_ansi() -> None:
    if os.name != "nt":
        return
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    mode = ctypes.c_uint32()
    if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)


def set_title(title: str) -> None:
    if os.name == "nt":
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    else:
        print(f"\033]0;{title}\007", end="")


def format_record(record: dict) -> str:
    label = str(record.get("label", "system"))
    color = COLORS.get(label, "\033[37m")
    ts = record.get("ts", "")
    message = record.get("message", "")
    data = record.get("data") or {}
    prefix = f"{DIM}{ts}{RESET} {color}{BOLD}[{label.upper()}]{RESET}"
    if data:
        details = " ".join(f"{key}={value!r}" for key, value in data.items())
        return f"{prefix} {message} {DIM}{details}{RESET}"
    return f"{prefix} {message}"


def _wait_before_exit() -> None:
    print()
    input(f"{DIM}Agent run finished. Press Enter to close this console...{RESET}")


def follow(log_path: Path, title: str, hold: bool) -> None:
    enable_ansi()
    set_title(title)
    print(f"{BOLD}Cloak-scrapling Agent Console{RESET}")
    print(f"{DIM}log: {log_path}{RESET}")
    print()

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch(exist_ok=True)

    with log_path.open("r", encoding="utf-8") as stream:
        shutdown_seen = False
        while True:
            line = stream.readline()
            if not line:
                if shutdown_seen:
                    time.sleep(1)
                    if hold:
                        _wait_before_exit()
                    return
                time.sleep(0.2)
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                print(f"{COLORS['error']}[RAW]{RESET} {line.rstrip()}")
                continue

            print(format_record(record), flush=True)
            if record.get("label") == "system" and record.get("message") == "agent console closing":
                shutdown_seen = True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render Cloak-scrapling JSONL events as colored console output.")
    parser.add_argument("log_path")
    parser.add_argument("--title", default="Cloak-scrapling Agent Console")
    parser.add_argument("--hold", action="store_true", help="Keep the console open after the Agent run finishes.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        follow(Path(args.log_path), args.title, args.hold)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
