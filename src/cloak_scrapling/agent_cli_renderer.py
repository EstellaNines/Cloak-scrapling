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

BRAND_ICON = "◈"
BRAND_WORDMARK = "Cloak Scrapling"
BRAND_SUBTITLE = "Agent CLI / browser control / scraping"
INPUT_MARK = "›"
EVENT_DOT = "●"
HIGHLIGHT_KEYS = {"status", "title", "url", "path", "index", "selector"}


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
        if self._rich_available:
            self._render_rich_banner()
            return

        self._print(f"{BRAND_ICON} {BRAND_WORDMARK}", style="bold")
        self._print(f"  {BRAND_SUBTITLE}", style="dim")
        self._print("Type /help for commands, /exit to quit.", style="dim")

    def render_events(self, events: Iterable[AgentEvent]) -> None:
        for event in events:
            self.render_event(event)

    def render_event(self, event: AgentEvent) -> None:
        if event.kind == "user":
            self._render_user_event(event)
            return
        if event.kind == "result":
            self._render_dot_event(event, dot_style="white", body_style="white")
            return
        if event.kind == "browser":
            self._render_dot_event(event, dot_style="bold green", body_style="green")
            return

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

    def _render_user_event(self, event: AgentEvent) -> None:
        message = f"{INPUT_MARK} {event.message}"
        if self._rich_available:
            self.console.print(message, style="bold white on grey23")
            return
        print(message)

    def _render_dot_event(self, event: AgentEvent, *, dot_style: str, body_style: str) -> None:
        if self._rich_available:
            self._render_rich_dot_event(event, dot_style=dot_style, body_style=body_style)
            return

        message = self._event_text(event)
        for index, line in enumerate(message.splitlines() or [""]):
            prefix = f"{EVENT_DOT} " if index == 0 else "  "
            print(f"{prefix}{line}")

    def _render_rich_dot_event(self, event: AgentEvent, *, dot_style: str, body_style: str) -> None:
        from rich.text import Text

        message = self._event_text(event)
        text = Text()
        text.append(EVENT_DOT, style=dot_style)
        text.append(" ")
        first = True
        for line in message.splitlines() or [""]:
            if not first:
                text.append("\n  ")
            self._append_highlighted(text, line, body_style=body_style)
            first = False
        self.console.print(text)

    def _event_text(self, event: AgentEvent) -> str:
        if not event.details:
            return event.message
        details = " ".join(f"{key}={value}" for key, value in event.details.items())
        return f"{event.message} {details}"

    def _append_highlighted(self, text: Any, line: str, *, body_style: str) -> None:
        remaining = line
        while remaining:
            matches = [
                (remaining.find(f"{key}="), f"{key}=")
                for key in HIGHLIGHT_KEYS
                if remaining.find(f"{key}=") >= 0
            ]
            if not matches:
                text.append(remaining, style=body_style)
                return

            index, token = min(matches, key=lambda item: item[0])
            if index:
                text.append(remaining[:index], style=body_style)
            text.append(token, style=f"bold {body_style}")
            remaining = remaining[index + len(token) :]

    def _render_rich_banner(self) -> None:
        from rich import box
        from rich.panel import Panel
        from rich.text import Text

        brand = Text()
        brand.append(BRAND_ICON, style="bold cyan")
        brand.append("  ")
        brand.append(BRAND_WORDMARK, style="bold white")
        brand.append("\n")
        brand.append(BRAND_SUBTITLE, style="dim cyan")

        self.console.print(
            Panel.fit(
                brand,
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        self._print("Type /help for commands, /exit to quit.", style="dim")
