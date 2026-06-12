---
name: cloak-scrapling
description: Use when an AI Agent needs automated browser-backed scraping, dynamic page extraction, or page interaction through Cloak-scrapling MCP tools, CLI commands, or the Python Session API.
---

# Cloak-scrapling Agent Skill

Use this skill when the task needs automated web scraping through a real
CloakBrowser Chromium session, especially when the page needs JavaScript
rendering, stealth browser behavior, clicks, form input, scrolling, screenshots,
or CSS selector extraction.

## Tool Selection

Prefer the uvx MCP package when the host Agent supports MCP:

```text
uvx cloak-scrapling-mcp
```

If the main package is already installed, this console script is equivalent:

```text
cloak-scrapling-mcp
```

Use the Agent CLI when a human operator wants an interactive terminal surface:

```text
cloak-scrapling-agent --headful
```

Use the one-shot CLI when MCP is unavailable and the task only needs extraction:

```text
cloak-scrapling-fetch <url> --selector "<css or selector::text>"
```

Use Python only when the Agent is editing or running project code directly:

```python
from cloak_scrapling import CloakScraplingSession
```

All adapters should call `CloakScraplingSession` rather than reaching directly
into CloakBrowser, Scrapling, or Playwright.

## MCP Automation Workflow

For direct extraction:

```text
fetch(url, extraction_type="markdown", css_selector=None, main_content_only=True)
```

For browser interaction:

```text
open(url)
state()
input(index, text)
click(index)
press(key)
scroll(direction)
get_text(selector=None)
get_html(selector=None)
screenshot(path=None)
```

Recommended Agent loop:

1. Call `open(url)` for pages that need rendering or interaction.
2. Call `state()` and inspect indexed interactive elements.
3. Use `input`, `click`, `press`, or `scroll` with indexes from the latest `state`.
4. Call `state()` again after navigation or DOM changes.
5. Extract with `get_text`, `get_html`, or `fetch` depending on the task.
6. Use `screenshot` when visual confirmation or debugging is needed.
7. Close or reset with `close_browser` / `reset_browser` when the task is done.

Element indexes are only valid for the latest `state()` result. Refresh state
after any click, input, navigation, or scroll that may change the DOM.

## Available MCP Tools

```text
status
fetch
open
state
click
input
press
scroll
screenshot
get_text
get_html
close_browser
reset_browser
```

`fetch` returns extracted content from Scrapling through the CloakBrowser CDP
session. Interaction tools reuse the same browser session through Playwright CDP
control and return structured dictionaries suitable for Agent planning.

## Agent CLI Fallback

Start:

```powershell
cloak-scrapling-agent --headful
```

Useful slash commands:

```text
/help
/open https://example.com
/state
/input 2 search text
/click 3
/text body
/html main
/fetch https://example.com title::text
/mcp https://example.com body
/screenshot
/status
/close
/exit
```

The Agent CLI transcript is designed for Codex / Claude Code style operation:

- Grey-backed `› /command`: user input or slash command.
- White dot `● content`: fetched, extracted, or text-read content.
- Green dot `● opened ...`: successful browser action output with highlighted markers such as `status=`, `title=`, `url=`, and `path=`.

Use `cloak-scrapling-shell --lang zh` only when the operator wants the older
command-oriented crawler shell.

## Browser Core and Runtime Notes

The Python sources for `cloakbrowser` and `scrapling` are bundled inside the
`cloak-scrapling` package. Do not require separate upstream package installs
unless explicitly testing upstream checkouts.

Inspect or install the active browser core with:

```powershell
cloak-scrapling-browser info
cloak-scrapling-browser install
```

Browser core resolution order:

```text
CLOAKBROWSER_BINARY_PATH
vendor_browser/<platform>/
CloakBrowser cache
CloakBrowser install/download
```

For shared or offline caches, set `CLOAK_SCRAPLING_CACHE_DIR` or
`CLOAKBROWSER_CACHE_DIR`. For offline deployments, place the browser core in the
documented `vendor_browser/<platform>/` layout.

## Safety and Failure Handling

- Do not expose `cloak-scrapling-mcp --http --host 0.0.0.0` to untrusted networks.
- Do not pass plain `http://127.0.0.1:<port>` as Scrapling `cdp_url`; Scrapling expects `ws://` or `wss://`.
- If an element action fails, call `state()` again before retrying.
- If `fetch` is enough, prefer it over interactive browser actions.
- If MCP is unavailable, use `cloak-scrapling-agent` or `cloak-scrapling-fetch`.
- If dependencies are missing in a bare interpreter, run inside the installed package environment or install project dependencies.

## Console Audit

For visible browser and Agent event logs:

```powershell
$env:CLOAK_SCRAPLING_CONSOLE = "1"
$env:CLOAK_SCRAPLING_CONSOLE_HOLD = "1"
```

The console records `SYSTEM`, `LAUNCH`, `CDP`, `INPUT`, `OUTPUT`, `MCP`, and
`ERROR` events to `.logs/agent-*.jsonl`.
