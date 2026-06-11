from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal


AgentEventKind = Literal["user", "system", "browser", "error", "result"]


@dataclass(frozen=True, slots=True)
class AgentEvent:
    kind: AgentEventKind
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "message": self.message,
            "details": dict(self.details),
            "timestamp": self.timestamp.isoformat(timespec="seconds"),
        }


@dataclass(slots=True)
class AgentStatus:
    running: bool = False
    current_url: str | None = None
    cdp_url: str | None = None
    browser_core_provider: str | None = None
    headful: bool = False
    humanize: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "running": self.running,
            "current_url": self.current_url,
            "cdp_url": self.cdp_url,
            "browser_core_provider": self.browser_core_provider,
            "headful": self.headful,
            "humanize": self.humanize,
        }


@dataclass(frozen=True, slots=True)
class AgentCommandResult:
    events: list[AgentEvent] = field(default_factory=list)
    should_exit: bool = False
    status: AgentStatus | None = None

    @classmethod
    def single(
        cls,
        kind: AgentEventKind,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        should_exit: bool = False,
        status: AgentStatus | None = None,
    ) -> "AgentCommandResult":
        return cls(
            events=[AgentEvent(kind=kind, message=message, details=details or {})],
            should_exit=should_exit,
            status=status,
        )
