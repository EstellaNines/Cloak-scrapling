from __future__ import annotations

import argparse
import asyncio
import shlex
from dataclasses import dataclass
from typing import Any

from .bridge import CloakScraplingBridge, CloakScraplingConfig


Lang = str


TEXT: dict[Lang, dict[str, str]] = {
    "zh": {
        "banner": "Cloak-scrapling 交互式爬虫 Shell。输入 help 查看命令。",
        "prompt": "crawler[{lang}]> ",
        "bye": "已退出。",
        "unknown": "未知命令：{command}。输入 help 查看命令。",
        "need_url": "缺少 URL。用法：fetch <url> [css_selector]",
        "need_index": "缺少元素编号。用法：{usage}",
        "need_text": "缺少输入文本。用法：input <index> <text>",
        "need_key": "缺少按键。用法：press <key>",
        "need_direction": "缺少方向。用法：scroll up|down",
        "need_lang": "用法：lang zh 或 lang en",
        "lang_set": "语言已切换为中文。",
        "lang_bad": "不支持的语言：{lang}。可用：zh, en",
        "bool_usage": "用法：{name} on|off",
        "bool_set": "{name} 已设置为 {value}，下次浏览器会话生效。",
        "config": (
            "配置：language={lang}, console={console}, console_hold={hold}, "
            "headful={headful}, humanize={humanize}"
        ),
        "starting": "正在启动 CloakBrowser 并通过 CDP 连接 Scrapling...",
        "started": "浏览器会话已就绪：{cdp}",
        "closed": "浏览器会话已关闭。",
        "restart": "会话已重置；下一次抓取会重新启动浏览器并应用新配置。",
        "fetching": "正在抓取：{url}",
        "opening": "正在打开：{url}",
        "opened": "已打开：{url}\n标题：{title}\n状态：{status}",
        "action_result": "{result}",
        "screenshot_saved": "截图已保存：{path}",
        "selector_result": "Selector 结果（{count} 条）：",
        "text_result": "页面标题：{title}\n文本预览：{preview}",
        "mcp_result": "MCP 状态：{status}\nURL：{url}\n内容：\n{content}",
        "error": "错误：{error}",
        "help": """命令：
  help                              显示帮助
  lang zh|en                        切换界面语言
  open <url>                        打开网页并保持页面会话
  state                             列出当前页面可交互元素
  click <index>                     点击 state 中的元素编号
  input <index> <text>              向元素输入文本
  press <key>                       发送键盘按键
  scroll up|down                    滚动页面
  screenshot [path]                 保存当前页面截图
  text [selector]                   读取页面或 selector 文本
  html [selector]                   读取页面或 selector HTML
  fetch <url> [selector]            使用 Scrapling StealthyFetcher 抓取
  mcp <url> [selector]              使用 ScraplingMCPServer.stealthy_fetch 抓取
  console on|off                    开关彩色 sidecar 控制台
  hold on|off                       控制台结束后是否停留
  headful on|off                    是否显示浏览器窗口
  humanize on|off                   是否启用 CloakBrowser humanize
  config                            查看当前配置
  restart                           关闭当前浏览器会话并在下次抓取时重启
  close                             关闭当前浏览器会话
  exit | quit                       退出 shell
示例：
  open https://example.com
  state
  input 2 hello
  click 3
  fetch https://example.com title::text
  mcp https://example.com body
  lang en
""",
    },
    "en": {
        "banner": "Cloak-scrapling interactive crawler shell. Type help for commands.",
        "prompt": "crawler[{lang}]> ",
        "bye": "Exited.",
        "unknown": "Unknown command: {command}. Type help for commands.",
        "need_url": "Missing URL. Usage: fetch <url> [css_selector]",
        "need_index": "Missing element index. Usage: {usage}",
        "need_text": "Missing input text. Usage: input <index> <text>",
        "need_key": "Missing key. Usage: press <key>",
        "need_direction": "Missing direction. Usage: scroll up|down",
        "need_lang": "Usage: lang zh or lang en",
        "lang_set": "Language switched to English.",
        "lang_bad": "Unsupported language: {lang}. Available: zh, en",
        "bool_usage": "Usage: {name} on|off",
        "bool_set": "{name} set to {value}. It will apply to the next browser session.",
        "config": (
            "Config: language={lang}, console={console}, console_hold={hold}, "
            "headful={headful}, humanize={humanize}"
        ),
        "starting": "Launching CloakBrowser and connecting Scrapling over CDP...",
        "started": "Browser session ready: {cdp}",
        "closed": "Browser session closed.",
        "restart": "Session reset. The next fetch will launch a browser with the updated config.",
        "fetching": "Fetching: {url}",
        "opening": "Opening: {url}",
        "opened": "Opened: {url}\nTitle: {title}\nStatus: {status}",
        "action_result": "{result}",
        "screenshot_saved": "Screenshot saved: {path}",
        "selector_result": "Selector results ({count}):",
        "text_result": "Page title: {title}\nText preview: {preview}",
        "mcp_result": "MCP status: {status}\nURL: {url}\nContent:\n{content}",
        "error": "Error: {error}",
        "help": """Commands:
  help                              Show help
  lang zh|en                        Switch UI language
  open <url>                        Open a page and keep it live
  state                             List indexed interactive elements
  click <index>                     Click an indexed element
  input <index> <text>              Fill an indexed element
  press <key>                       Send a keyboard key
  scroll up|down                    Scroll the page
  screenshot [path]                 Save a page screenshot
  text [selector]                   Read page or selector text
  html [selector]                   Read page or selector HTML
  fetch <url> [selector]            Fetch with Scrapling StealthyFetcher
  mcp <url> [selector]              Fetch through ScraplingMCPServer.stealthy_fetch
  console on|off                    Toggle colored sidecar console
  hold on|off                       Keep console open after run
  headful on|off                    Toggle visible browser window
  humanize on|off                   Toggle CloakBrowser humanize
  config                            Show current config
  restart                           Close current browser session and apply config next time
  close                             Close current browser session
  exit | quit                       Exit shell
Examples:
  open https://example.com
  state
  input 2 hello
  click 3
  fetch https://example.com title::text
  mcp https://example.com body
  lang zh
""",
    },
}


ALIASES = {
    "帮助": "help",
    "?": "help",
    "h": "help",
    "语言": "lang",
    "打开": "open",
    "状态": "state",
    "点击": "click",
    "输入": "input",
    "按键": "press",
    "滚动": "scroll",
    "截图": "screenshot",
    "文本": "text",
    "抓取": "fetch",
    "控制台": "console",
    "配置": "config",
    "重启": "restart",
    "关闭": "close",
    "退出": "exit",
    "q": "exit",
    "quit": "exit",
}


@dataclass
class ShellState:
    lang: Lang = "zh"
    console: bool = False
    console_hold: bool = True
    headful: bool = False
    humanize: bool = False


class InteractiveShell:
    def __init__(self, state: ShellState | None = None) -> None:
        self.state = state or ShellState()
        self.bridge: CloakScraplingBridge | None = None

    def text(self, key: str, **kwargs: Any) -> str:
        return TEXT[self.state.lang][key].format(**kwargs)

    async def run(self) -> None:
        print(self.text("banner"))
        try:
            while True:
                line = await asyncio.to_thread(input, self.text("prompt", lang=self.state.lang))
                should_exit = await self.dispatch(line)
                if should_exit:
                    break
        finally:
            await self.close_bridge()
            print(self.text("bye"))

    async def dispatch(self, line: str) -> bool:
        line = line.strip()
        if not line:
            return False

        try:
            parts = shlex.split(line)
        except ValueError as exc:
            print(self.text("error", error=str(exc)))
            return False

        if not parts:
            return False

        command = ALIASES.get(parts[0].lower(), parts[0].lower())
        args = parts[1:]

        if command == "help":
            print(TEXT[self.state.lang]["help"])
        elif command == "lang":
            self.set_language(args)
        elif command in {"console", "hold", "headful", "humanize"}:
            await self.set_bool(command, args)
        elif command == "config":
            self.print_config()
        elif command == "restart":
            await self.close_bridge()
            print(self.text("restart"))
        elif command == "close":
            await self.close_bridge()
            print(self.text("closed"))
        elif command == "open":
            await self.open_page(args)
        elif command == "state":
            await self.print_page_state()
        elif command == "click":
            await self.click(args)
        elif command == "input":
            await self.input(args)
        elif command == "press":
            await self.press(args)
        elif command == "scroll":
            await self.scroll(args)
        elif command == "screenshot":
            await self.screenshot(args)
        elif command == "text":
            await self.get_text(args)
        elif command == "html":
            await self.get_html(args)
        elif command == "fetch":
            await self.fetch(args, use_mcp=False)
        elif command == "mcp":
            await self.fetch(args, use_mcp=True)
        elif command == "exit":
            return True
        else:
            print(self.text("unknown", command=command))
        return False

    def set_language(self, args: list[str]) -> None:
        if not args:
            print(self.text("need_lang"))
            return
        lang = args[0].lower()
        if lang not in TEXT:
            print(self.text("lang_bad", lang=lang))
            return
        self.state.lang = lang
        print(self.text("lang_set"))

    async def set_bool(self, name: str, args: list[str]) -> None:
        if not args or args[0].lower() not in {"on", "off"}:
            print(self.text("bool_usage", name=name))
            return
        value = args[0].lower() == "on"
        if name == "console":
            self.state.console = value
        elif name == "hold":
            self.state.console_hold = value
        elif name == "headful":
            self.state.headful = value
        elif name == "humanize":
            self.state.humanize = value
        await self.close_bridge()
        print(self.text("bool_set", name=name, value="on" if value else "off"))

    def print_config(self) -> None:
        print(
            self.text(
                "config",
                lang=self.state.lang,
                console=self.state.console,
                hold=self.state.console_hold,
                headful=self.state.headful,
                humanize=self.state.humanize,
            )
        )

    async def fetch(self, args: list[str], use_mcp: bool) -> None:
        if not args:
            print(self.text("need_url"))
            return

        url = args[0]
        selector = args[1] if len(args) > 1 else None
        try:
            bridge = await self.ensure_bridge()
            bridge.console.log(
                "input",
                "interactive command",
                mode="mcp" if use_mcp else "fetch",
                url=url,
                selector=selector,
            )
            print(self.text("fetching", url=url))

            if use_mcp:
                result = await bridge.mcp_stealthy_fetch(
                    url,
                    extraction_type="text",
                    css_selector=selector,
                    main_content_only=False,
                    wait=100,
                )
                content = "\n".join(str(item) for item in result.content)
                bridge.console.log(
                    "output",
                    "interactive MCP output",
                    status=result.status,
                    url=result.url,
                    content=content[:1000],
                )
                print(
                    self.text(
                        "mcp_result",
                        status=result.status,
                        url=result.url,
                        content=content,
                    )
                )
                return

            page = await bridge.fetch(url, wait=100)
            if selector:
                values = [str(item) for item in page.css(selector).getall()]
                bridge.console.log(
                    "output",
                    "interactive selector output",
                    selector=selector,
                    values=values,
                )
                print(self.text("selector_result", count=len(values)))
                print("\n".join(values))
            else:
                title = page.css("title::text").get()
                preview = (page.text or "")[:500].replace("\n", " ")
                bridge.console.log(
                    "output",
                    "interactive text output",
                    title=title,
                    preview=preview,
                )
                print(self.text("text_result", title=title, preview=preview))
        except Exception as exc:
            print(self.text("error", error=repr(exc)))

    async def open_page(self, args: list[str]) -> None:
        if not args:
            print(self.text("need_url"))
            return
        try:
            controller = await self.ensure_controller()
            url = args[0]
            print(self.text("opening", url=url))
            result = await controller.open_url(url)
            print(
                self.text(
                    "opened",
                    url=result.get("url"),
                    title=result.get("title"),
                    status=result.get("status"),
                )
            )
        except Exception as exc:
            print(self.text("error", error=repr(exc)))

    async def print_page_state(self) -> None:
        try:
            controller = await self.ensure_controller()
            state = await controller.state()
            print(state.to_text())
        except Exception as exc:
            print(self.text("error", error=repr(exc)))

    async def click(self, args: list[str]) -> None:
        index = self.parse_index(args, "click <index>")
        if index is None:
            return
        try:
            controller = await self.ensure_controller()
            print(self.text("action_result", result=await controller.click(index)))
        except Exception as exc:
            print(self.text("error", error=repr(exc)))

    async def input(self, args: list[str]) -> None:
        index = self.parse_index(args, "input <index> <text>")
        if index is None:
            return
        if len(args) < 2:
            print(self.text("need_text"))
            return
        try:
            controller = await self.ensure_controller()
            result = await controller.input_text(index, " ".join(args[1:]))
            print(self.text("action_result", result=result))
        except Exception as exc:
            print(self.text("error", error=repr(exc)))

    async def press(self, args: list[str]) -> None:
        if not args:
            print(self.text("need_key"))
            return
        try:
            controller = await self.ensure_controller()
            print(self.text("action_result", result=await controller.press(args[0])))
        except Exception as exc:
            print(self.text("error", error=repr(exc)))

    async def scroll(self, args: list[str]) -> None:
        if not args:
            print(self.text("need_direction"))
            return
        try:
            controller = await self.ensure_controller()
            print(self.text("action_result", result=await controller.scroll(args[0])))
        except Exception as exc:
            print(self.text("error", error=repr(exc)))

    async def screenshot(self, args: list[str]) -> None:
        try:
            controller = await self.ensure_controller()
            result = await controller.screenshot(args[0] if args else None)
            print(self.text("screenshot_saved", path=result["path"]))
        except Exception as exc:
            print(self.text("error", error=repr(exc)))

    async def get_text(self, args: list[str]) -> None:
        try:
            controller = await self.ensure_controller()
            print(await controller.get_text(args[0] if args else None))
        except Exception as exc:
            print(self.text("error", error=repr(exc)))

    async def get_html(self, args: list[str]) -> None:
        try:
            controller = await self.ensure_controller()
            print(await controller.get_html(args[0] if args else None))
        except Exception as exc:
            print(self.text("error", error=repr(exc)))

    def parse_index(self, args: list[str], usage: str) -> int | None:
        if not args:
            print(self.text("need_index", usage=usage))
            return None
        try:
            return int(args[0])
        except ValueError:
            print(self.text("need_index", usage=usage))
            return None

    async def ensure_controller(self) -> Any:
        bridge = await self.ensure_bridge()
        return await bridge.ensure_controller()

    async def ensure_bridge(self) -> CloakScraplingBridge:
        if self.bridge and self.bridge.cdp_url:
            return self.bridge

        print(self.text("starting"))
        config = CloakScraplingConfig(
            headless=not self.state.headful,
            humanize=self.state.humanize,
            console=self.state.console,
            console_hold=self.state.console_hold,
            console_title="Cloak-scrapling Interactive Shell",
        )
        self.bridge = CloakScraplingBridge(config)
        cdp_url = await self.bridge.start()
        print(self.text("started", cdp=cdp_url))
        return self.bridge

    async def close_bridge(self) -> None:
        if self.bridge is not None:
            await self.bridge.close()
            self.bridge = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Interactive CloakBrowser + Scrapling crawler shell."
    )
    parser.add_argument(
        "--lang",
        choices=["zh", "en"],
        default="zh",
        help="Initial UI language.",
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Enable the colored sidecar console.",
    )
    parser.add_argument("--headful", action="store_true", help="Run the browser visibly.")
    parser.add_argument("--humanize", action="store_true", help="Enable CloakBrowser humanize.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    state = ShellState(
        lang=args.lang,
        console=args.console,
        headful=args.headful,
        humanize=args.humanize,
    )
    asyncio.run(InteractiveShell(state).run())


if __name__ == "__main__":
    main()
