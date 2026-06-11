from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .agent_cli_commands import command_help_text
from .agent_cli_models import AgentEvent, AgentStatus
from .browser_models import BrowserState


EVENT_STYLES: dict[str, str] = {
    "user": "cyan",
    "system": "blue",
    "browser": "magenta",
    "error": "bold red",
    "result": "green",
}


class AgentCliRenderer:
    """Render Agent CLI events with Rich when available and plain text otherwise."""

    def __init__(self, console: Any | None = None) -> None:
        self._rich_available = False
        if console is not None:
            self.console = console
            self._rich_available = True
            return
        try:
            from rich.console import Console

            self.console = Console()
            self._rich_available = True
        except Exception:
            self.console = None

    def render_banner(self) -> None:
        self._print("Cloak-scrapling Agent CLI", style="bold")
        self._print("Type /help for commands, /exit to quit.", style="dim")

    def render_events(self, events: Iterable[AgentEvent]) -> None:
        for event in events:
            self.render_event(event)

    def render_event(self, event: AgentEvent) -> None:
        prefix = f"[{event.kind}]"
        message = f"{prefix} {event.message}"
        if event.details:
            details = " ".join(f"{key}={value}" for key, value in event.details.items())
            message = f"{message} {details}"
        self._print(message, style=EVENT_STYLES.get(event.kind, "white"))

    def render_status(self, status: AgentStatus) -> None:
        fields = [
            f"running={status.running}",
            f"url={status.current_url or '-'}",
            f"cdp={status.cdp_url or '-'}",
            f"core={status.browser_core_provider or '-'}",
            f"headful={status.headful}",
            f"humanize={status.humanize}",
        ]
        self._print(" | ".join(fields), style="bold blue")

    def render_help(self) -> None:
        self._print(command_help_text(), style="white")

    def render_browser_state(self, state: BrowserState) -> None:
        self._print(state.to_text(), style="green")

    def _print(self, message: str, *, style: str | None = None) -> None:
        if self._rich_available:
            self.console.print(message, style=style)
            return
        print(message)
