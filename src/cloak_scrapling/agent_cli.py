from __future__ import annotations

import argparse
import asyncio
from collections.abc import Sequence

from .agent_cli_commands import SLASH_COMMANDS, parse_agent_command
from .agent_cli_models import AgentCommandResult, AgentEvent, AgentStatus
from .agent_cli_renderer import AgentCliRenderer
from .bridge import CloakScraplingConfig
from .browser_core import BrowserCoreResolver
from .session import CloakScraplingSession


class AgentCliApp:
    def __init__(
        self,
        args: argparse.Namespace,
        renderer: AgentCliRenderer | None = None,
        session: CloakScraplingSession | None = None,
    ) -> None:
        self.args = args
        self.renderer = renderer or AgentCliRenderer()
        self.session = session
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

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()
            self.session = None
            self.status.running = False
            self.status.cdp_url = None

    async def dispatch(self, line: str) -> AgentCommandResult:
        try:
            command = parse_agent_command(line)
        except ValueError as exc:
            return AgentCommandResult.single("error", str(exc))

        if command.name == "help":
            self.renderer.render_help()
            return AgentCommandResult()
        if command.name == "status":
            await self.refresh_status()
            return AgentCommandResult.single(
                "system",
                "status",
                status=self.status,
            )
        if command.name == "exit":
            await self.close()
            return AgentCommandResult.single("system", "exiting", should_exit=True)
        if command.name in {"close", "restart"}:
            return AgentCommandResult.single(
                "system",
                f"/{command.name} requires confirmation; confirmation wiring comes next",
                status=self.status,
            )

        try:
            return await self.dispatch_session_command(command.name, command.args)
        except Exception as exc:
            return AgentCommandResult.single("error", repr(exc), status=self.status)

    async def dispatch_session_command(self, name: str, args: list[str]) -> AgentCommandResult:
        if name == "open":
            url = self._require_arg(args, "Usage: /open <url>")
            session = await self.ensure_session()
            result = await session.open(url)
            self.status.current_url = str(result.get("url") or url)
            await self.refresh_status()
            return AgentCommandResult.single(
                "browser",
                f"opened {self.status.current_url}",
                details={"status": result.get("status"), "title": result.get("title")},
                status=self.status,
            )

        if name == "state":
            session = await self.ensure_session()
            state = await session.state()
            self.status.current_url = state.url
            await self.refresh_status()
            return AgentCommandResult.single("result", state.to_text(), status=self.status)

        if name == "click":
            index = self._parse_index(args, "Usage: /click <index>")
            session = await self.ensure_session()
            result = await session.click(index)
            await self.refresh_status()
            return AgentCommandResult.single("browser", f"clicked {index}", details=result, status=self.status)

        if name == "input":
            index = self._parse_index(args, "Usage: /input <index> <text>")
            if len(args) < 2:
                raise ValueError("Usage: /input <index> <text>")
            session = await self.ensure_session()
            result = await session.input(index, " ".join(args[1:]))
            await self.refresh_status()
            return AgentCommandResult.single("browser", f"input {index}", details=result, status=self.status)

        if name == "press":
            key = self._require_arg(args, "Usage: /press <key>")
            session = await self.ensure_session()
            result = await session.press(key)
            await self.refresh_status()
            return AgentCommandResult.single("browser", f"pressed {key}", details=result, status=self.status)

        if name == "scroll":
            direction = self._require_arg(args, "Usage: /scroll up|down")
            session = await self.ensure_session()
            result = await session.scroll(direction)
            await self.refresh_status()
            return AgentCommandResult.single("browser", f"scrolled {direction}", details=result, status=self.status)

        if name == "text":
            session = await self.ensure_session()
            content = await session.get_text(args[0] if args else None)
            await self.refresh_status()
            return AgentCommandResult.single("result", content, status=self.status)

        if name == "html":
            session = await self.ensure_session()
            content = await session.get_html(args[0] if args else None)
            await self.refresh_status()
            return AgentCommandResult.single("result", content, status=self.status)

        if name == "fetch":
            url = self._require_arg(args, "Usage: /fetch <url> [selector]")
            selector = args[1] if len(args) > 1 else None
            session = await self.ensure_session()
            page = await session.fetch(url, wait=100)
            content = "\n".join(str(item) for item in page.css(selector).getall()) if selector else page.text
            await self.refresh_status()
            return AgentCommandResult.single("result", str(content or ""), status=self.status)

        if name == "mcp":
            url = self._require_arg(args, "Usage: /mcp <url> [selector]")
            selector = args[1] if len(args) > 1 else None
            session = await self.ensure_session()
            result = await session.mcp_fetch(
                url,
                extraction_type="text",
                css_selector=selector,
                main_content_only=False,
                wait=100,
            )
            content = "\n".join(str(item) for item in getattr(result, "content", []) or [])
            await self.refresh_status()
            return AgentCommandResult.single("result", content, status=self.status)

        if name == "screenshot":
            session = await self.ensure_session()
            result = await session.screenshot(args[0] if args else None)
            await self.refresh_status()
            return AgentCommandResult.single("result", "screenshot saved", details=result, status=self.status)

        raise ValueError(f"Unsupported command: /{name}")

    async def ensure_session(self) -> CloakScraplingSession:
        if self.session is None:
            config = CloakScraplingConfig(
                headless=not self.args.headful,
                humanize=self.args.humanize,
                console=True if self.args.console else None,
                console_title="Cloak-scrapling Agent CLI",
            )
            self.session = CloakScraplingSession(config)
        await self.session.start()
        return self.session

    async def refresh_status(self) -> AgentStatus:
        if self.session is not None:
            info = self.session.browser_core_info
            self.status.running = bool(self.session.cdp_url)
            self.status.cdp_url = self.session.cdp_url
            self.status.browser_core_provider = info.provider
        else:
            self.status.browser_core_provider = BrowserCoreResolver().resolve().provider
        return self.status

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

    @staticmethod
    def _require_arg(args: list[str], message: str) -> str:
        if not args:
            raise ValueError(message)
        return args[0]

    @staticmethod
    def _parse_index(args: list[str], message: str) -> int:
        if not args:
            raise ValueError(message)
        try:
            return int(args[0])
        except ValueError as exc:
            raise ValueError(message) from exc

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
