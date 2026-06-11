from __future__ import annotations

import shlex
from dataclasses import dataclass, field


SLASH_COMMANDS: tuple[str, ...] = (
    "help",
    "open",
    "state",
    "click",
    "input",
    "press",
    "scroll",
    "text",
    "html",
    "fetch",
    "mcp",
    "screenshot",
    "status",
    "close",
    "restart",
    "exit",
)

COMMAND_ALIASES: dict[str, str] = {
    "?": "help",
    "quit": "exit",
    "q": "exit",
}


@dataclass(frozen=True, slots=True)
class ParsedAgentCommand:
    name: str
    args: list[str] = field(default_factory=list)
    raw: str = ""

    @property
    def is_exit(self) -> bool:
        return self.name == "exit"


def parse_agent_command(line: str) -> ParsedAgentCommand:
    raw = line.strip()
    if not raw:
        return ParsedAgentCommand(name="help", raw=line)

    if _looks_like_url(raw):
        return ParsedAgentCommand(name="open", args=[raw], raw=line)

    if raw.startswith("/"):
        raw = raw[1:].strip()

    try:
        parts = shlex.split(raw)
    except ValueError as exc:
        raise ValueError(f"Could not parse command: {exc}") from exc

    if not parts:
        return ParsedAgentCommand(name="help", raw=line)

    name = COMMAND_ALIASES.get(parts[0].lower(), parts[0].lower())
    if name not in SLASH_COMMANDS:
        raise ValueError(f"Unknown command: /{name}")

    return ParsedAgentCommand(name=name, args=parts[1:], raw=line)


def command_help_text() -> str:
    return "\n".join(
        [
            "Available commands:",
            "/help",
            "/open <url>",
            "/state",
            "/click <index>",
            "/input <index> <text>",
            "/press <key>",
            "/scroll up|down",
            "/text [selector]",
            "/html [selector]",
            "/fetch <url> [selector]",
            "/mcp <url> [selector]",
            "/screenshot [path]",
            "/status",
            "/close",
            "/restart",
            "/exit",
        ]
    )


def _looks_like_url(value: str) -> bool:
    return value.startswith(("http://", "https://"))
