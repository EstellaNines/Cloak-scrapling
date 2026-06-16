from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRUTHY = {"1", "true", "yes", "on"}


def env_console_enabled() -> bool:
    return os.environ.get("CLOAK_SCRAPLING_CONSOLE", "").strip().lower() in TRUTHY


def env_console_hold_enabled() -> bool:
    return os.environ.get("CLOAK_SCRAPLING_CONSOLE_HOLD", "").strip().lower() in TRUTHY


def _safe_home() -> Path:
    """Return the user home, falling back to the temp dir if undeterminable.

    On Windows ``Path.home()`` relies on ``USERPROFILE``/``HOMEDRIVE`` and raises
    ``RuntimeError`` when those are absent (e.g. a stripped environment), unlike
    POSIX where ``pwd`` provides a fallback. Guard against that so log-path
    resolution never crashes.
    """
    import tempfile

    try:
        return Path.home()
    except RuntimeError:
        return Path(tempfile.gettempdir())


def default_log_dir() -> Path:
    if os.environ.get("CLOAK_SCRAPLING_LOG_DIR"):
        return Path(os.environ["CLOAK_SCRAPLING_LOG_DIR"])
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / "CloakScrapling" / "logs"
        return _safe_home() / "AppData" / "Local" / "CloakScrapling" / "logs"
    return _safe_home() / ".cache" / "cloak-scrapling" / "logs"


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        return repr(value)


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


class AgentConsole:
    """Sidecar console process fed by JSONL events."""

    def __init__(
        self,
        enabled: bool | None = None,
        title: str = "Cloak-scrapling Agent Console",
        log_dir: Path | None = None,
        hold: bool | None = None,
    ) -> None:
        self.enabled = env_console_enabled() if enabled is None else enabled
        self.title = title
        self.log_dir = log_dir or default_log_dir()
        self.hold = env_console_hold_enabled() if hold is None else hold
        self.log_path: Path | None = None
        self._stream = None
        self._process: subprocess.Popen | None = None

    def start(self) -> None:
        if not self.enabled or self._stream is not None:
            return

        self.log_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.log_path = self.log_dir / f"agent-{stamp}-{uuid4().hex[:8]}.jsonl"
        self._stream = self.log_path.open("a", encoding="utf-8", buffering=1)
        self._spawn_viewer()
        self.log("system", "agent console started", log_path=str(self.log_path))

    def log(self, label: str, message: str, **data: Any) -> None:
        if not self.enabled:
            return
        if self._stream is None:
            self.start()
        if self._stream is None:
            return

        record = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "label": label,
            "message": message,
            "data": {key: _json_safe(value) for key, value in data.items()},
        }
        self._stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._stream.flush()

    def close(self) -> None:
        if not self.enabled:
            return
        self.log("system", "agent console closing")
        if self._stream is not None:
            self._stream.close()
            self._stream = None

    def _spawn_viewer(self) -> None:
        assert self.log_path is not None
        viewer_cmd = [
            sys.executable,
            "-m",
            "cloak_scrapling.console_viewer",
            str(self.log_path),
            "--title",
            self.title,
        ]
        if self.hold:
            viewer_cmd.append("--hold")
        env = os.environ.copy()
        source_path = str(PROJECT_ROOT / "src")
        if Path(source_path).exists():
            env["PYTHONPATH"] = source_path + os.pathsep + env.get("PYTHONPATH", "")

        creationflags = 0
        cmd = viewer_cmd
        if os.name == "nt":
            creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
            ps_viewer = " ".join(_ps_quote(part) for part in viewer_cmd)
            cmd = [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-NoExit" if self.hold else "-Command",
            ]
            if self.hold:
                cmd.extend(
                    [
                        "-Command",
                        f"$Host.UI.RawUI.WindowTitle = {_ps_quote(self.title)}; & {ps_viewer}",
                    ]
                )
            else:
                cmd.append(f"$Host.UI.RawUI.WindowTitle = {_ps_quote(self.title)}; & {ps_viewer}")

        try:
            self._process = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT),
                env=env,
                creationflags=creationflags,
                close_fds=os.name != "nt",
            )
        except OSError as exc:
            self._process = None
            if self._stream is not None:
                self._stream.write(
                    json.dumps(
                        {
                            "ts": datetime.now().isoformat(timespec="seconds"),
                            "label": "error",
                            "message": "failed to spawn console viewer",
                            "data": {"error": repr(exc)},
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
