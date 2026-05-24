---
name: cloak-scrapling
description: Use when an AI Agent needs browser-backed web scraping through CloakBrowser stealth Chromium and Scrapling parsing/MCP tools.
---

# Cloak-scrapling Agent Skill

Use `cloak-scrapling` when the task needs:

- Browser-backed scraping with stealth Chromium.
- Dynamic page rendering before extraction.
- CSS selector extraction, text/HTML/Markdown output, or MCP-driven fetches.
- A visible sidecar console for Agent input/output audit logs.

## Preferred Tools

Use the MCP server when available:

```text
cloak-scrapling-mcp
```

Primary MCP tool:

```text
fetch(url, extraction_type="markdown", css_selector=None, main_content_only=True)
```

The MCP server starts CloakBrowser automatically, extracts the CDP WebSocket URL, connects Scrapling over CDP, and reuses the browser between fetch calls.

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
- The package does not bundle Chromium. CloakBrowser downloads/caches its binary on first run unless `CLOAKBROWSER_BINARY_PATH` is set.
- Set `CLOAK_SCRAPLING_CACHE_DIR` or `CLOAKBROWSER_CACHE_DIR` for shared/offline browser caches.
