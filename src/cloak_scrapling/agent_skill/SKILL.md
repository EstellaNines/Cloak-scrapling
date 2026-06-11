---
name: cloak-scrapling
description: Use when an AI Agent needs browser-backed web scraping through CloakBrowser stealth Chromium and Scrapling parsing/MCP tools.
---

# Cloak-scrapling Agent Skill

Use `cloak-scrapling` when the task needs:

- Browser-backed scraping with stealth Chromium.
- Dynamic page rendering before extraction.
- CSS selector extraction, text/HTML/Markdown output, or MCP-driven fetches.
- Live page interaction: open a page, inspect indexed elements, click, input, scroll, press keys, and screenshot.
- A visible sidecar console for Agent input/output audit logs.

## Preferred Tools

Use the MCP server when available:

```text
cloak-scrapling-mcp
```

Primary extraction MCP tool:

```text
fetch(url, extraction_type="markdown", css_selector=None, main_content_only=True)
```

Primary interaction MCP flow:

```text
open(url)
state()
input(index, text)
click(index)
get_text(selector=None)
```

The MCP server starts CloakBrowser automatically, extracts the CDP WebSocket URL, connects Scrapling over CDP for extraction, and connects Playwright over the same CDP URL for page interaction.

The Python sources for `cloakbrowser` and `scrapling` are bundled inside the
`cloak-scrapling` package; do not require separate upstream package installs
unless explicitly testing upstream checkouts.

Use `cloak-scrapling-browser info` to inspect the active browser core. The
resolver checks `CLOAKBROWSER_BINARY_PATH`, `vendor_browser/<platform>/`,
CloakBrowser cache, then CloakBrowser install/download.

## CLI Fallback

One-shot fetch:

```powershell
cloak-scrapling-fetch https://example.com --selector "title::text"
```

Interactive shell:

```powershell
cloak-scrapling-shell --lang zh
```

Useful shell commands:

```text
open https://example.com
state
input 2 hello
click 3
text body
fetch https://example.com title::text
mcp https://example.com body
lang en
console on
config
exit
```

## Console Audit

Enable a visible colored console:

```powershell
$env:CLOAK_SCRAPLING_CONSOLE = "1"
$env:CLOAK_SCRAPLING_CONSOLE_HOLD = "1"
```

The console logs `SYSTEM`, `LAUNCH`, `CDP`, `INPUT`, `OUTPUT`, `MCP`, and `ERROR` events to `.logs/agent-*.jsonl`.

## Operational Notes

- Do not pass plain `http://127.0.0.1:<port>` as Scrapling `cdp_url`; Scrapling requires `ws://` or `wss://`.
- Element indexes are valid only for the latest `state` result; run `state` again after navigation or DOM changes.
- The package does not commit Chromium binaries in v1; place offline cores in `vendor_browser/<platform>/` or use `cloak-scrapling-browser install`.
- Set `CLOAK_SCRAPLING_CACHE_DIR` or `CLOAKBROWSER_CACHE_DIR` for shared/offline browser caches.
