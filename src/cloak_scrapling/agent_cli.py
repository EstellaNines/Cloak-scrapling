from __future__ import annotations

import argparse
import asyncio
from collections.abc import Sequence

from .agent_cli_commands import SLASH_COMMANDS, parse_agent_command
from .agent_cli_models import AgentCommandResult, AgentEvent, AgentStatus
from .agent_cli_renderer import AgentCliRenderer


class AgentCliApp:
    def __init__(self, args: argparse.Namespace, renderer: AgentCliRenderer | None = None) -> None:
        self.args = args
        self.renderer = renderer or AgentCliRenderer()
        self.status = AgentStatus(
            headful=bool(args.headful),
            humanize=bool(args.humanize),
        )

    async def run(self) -> int:
        self.renderer.render_banner()
        while True:
            try:
                line = await asyncio.to_thread(self._prompt)
            except (EOFError, KeyboardInterrupt):
                self.renderer.render_event(AgentEvent(kind="system", message="exiting"))
                return 0
            result = await self.dispatch(line)
            self.renderer.render_events(result.events)
            if result.status is not None:
                self.status = result.status
            if result.should_exit:
                return 0

    async def dispatch(self, line: str) -> AgentCommandResult:
        try:
            command = parse_agent_command(line)
        except ValueError as exc:
            return AgentCommandResult.single("error", str(exc))

        if command.name == "help":
            self.renderer.render_help()
            return AgentCommandResult()
        if command.name == "status":
            return AgentCommandResult.single(
                "system",
                "status",
                status=self.status,
            )
        if command.name == "exit":
            return AgentCommandResult.single("system", "exiting", should_exit=True)

        return AgentCommandResult.single(
            "system",
            f"/{command.name} will be available after session wiring",
            details={"args": " ".join(command.args)},
        )

    def _prompt(self) -> str:
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.completion import WordCompleter
            from prompt_toolkit.history import InMemoryHistory
        except Exception:
            return input("cloak> ")

        if not hasattr(self, "_prompt_session"):
            commands = [f"/{command}" for command in SLASH_COMMANDS]
            self._prompt_session = PromptSession(
                history=InMemoryHistory(),
                completer=WordCompleter(commands, ignore_case=True),
            )
        return self._prompt_session.prompt("cloak> ")

    async def run_once(self, line: str) -> int:
        result = await self.dispatch(line)
        self.renderer.render_events(result.events)
        if result.status is not None:
            self.renderer.render_status(result.status)
        return 0

async def run_agent_cli(args: argparse.Namespace) -> int:
    """Run the lightweight Agent CLI shell."""
    app = AgentCliApp(args)
    if args.once:
        return await app.run_once(args.once)
    return await app.run()


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
