from __future__ import annotations

import argparse
import asyncio

from .bridge import CloakScraplingBridge, CloakScraplingConfig


async def _run(args: argparse.Namespace) -> None:
    config = CloakScraplingConfig(
        headless=not args.headful,
        humanize=args.humanize,
        console=True if args.console or args.console_hold else None,
        console_hold=True if args.console or args.console_hold else None,
    )
    async with CloakScraplingBridge(config) as bridge:
        if args.mcp:
            result = await bridge.mcp_stealthy_fetch(
                args.url,
                extraction_type=args.extraction_type,
                css_selector=args.selector,
                main_content_only=not args.full_page,
                wait=args.wait,
                timeout=args.timeout,
            )
            print(f"status={result.status}")
            print(f"url={result.url}")
            content = [str(item) for item in result.content]
            bridge.console.log("output", "CLI MCP output printed", status=result.status, url=result.url, content=content)
            for item in content:
                print(item)
            return

        page = await bridge.fetch(args.url, wait=args.wait, timeout=args.timeout)
        if args.selector:
            values = page.css(args.selector).getall()
            bridge.console.log("output", "CLI selector output printed", selector=args.selector, values=values)
            print("\n".join(str(value) for value in values))
        else:
            output = page.text[: args.limit]
            bridge.console.log("output", "CLI text output printed", limit=args.limit, preview=output[:500])
            print(output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch a URL through CloakBrowser-backed Scrapling.")
    parser.add_argument("url")
    parser.add_argument("--selector", help="CSS selector to extract from the fetched page.")
    parser.add_argument("--headful", action="store_true", help="Run the browser visibly.")
    parser.add_argument("--humanize", action="store_true", help="Enable CloakBrowser wrapper-level humanized actions.")
    parser.add_argument("--console", action="store_true", help="Open a colored sidecar console for Agent I/O events and keep it open.")
    parser.add_argument("--console-hold", action="store_true", help="Keep the sidecar console open after completion.")
    parser.add_argument("--wait", type=float, default=100, help="Milliseconds to wait after navigation.")
    parser.add_argument("--timeout", type=float, default=30000, help="Operation timeout in milliseconds.")
    parser.add_argument("--limit", type=int, default=2000, help="Max characters printed when no selector is given.")
    parser.add_argument("--mcp", action="store_true", help="Use ScraplingMCPServer.stealthy_fetch instead of direct fetcher.")
    parser.add_argument("--extraction-type", default="text", choices=["text", "html", "markdown"])
    parser.add_argument("--full-page", action="store_true", help="Disable main-content-only extraction for MCP mode.")
    return parser


def main() -> None:
    parser = build_parser()
    asyncio.run(_run(parser.parse_args()))
