# Usage

## One-shot fetch

```powershell
cloak-scrapling-fetch https://example.com --selector "title::text"
```

Fetch text preview:

```powershell
cloak-scrapling-fetch https://example.com --limit 3000
```

Use MCP-style extraction:

```powershell
cloak-scrapling-fetch https://example.com --mcp --selector body --extraction-type text
```

Return Markdown:

```powershell
cloak-scrapling-fetch https://example.com --mcp --selector main --extraction-type markdown
```

Show browser window:

```powershell
cloak-scrapling-fetch https://example.com --headful
```

Enable sidecar console:

```powershell
cloak-scrapling-fetch https://example.com --selector "title::text" --console
```

## Browser core management

```powershell
cloak-scrapling-browser info
cloak-scrapling-browser info --json
cloak-scrapling-browser install
cloak-scrapling-browser clear-cache
```

## Interactive shell

```powershell
cloak-scrapling-shell --lang en
```

Common commands:

```text
help
open https://example.com
state
input 2 hello
click 3
scroll down
screenshot .logs/example.png
text body
html main
fetch https://example.com title::text
mcp https://example.com body
console on
hold on
headful on
humanize on
config
restart
close
exit
```

Interaction mode reuses the current CloakBrowser session. `state` returns indexed elements for the current page; run `state` again after page changes to refresh indexes.

## Agent CLI

`cloak-scrapling-agent` is a Codex / Claude Code style slash-command interface.
It reuses the same `CloakScraplingSession` backend:

```powershell
cloak-scrapling-agent --headful
```

Common commands:

```text
/help
/open https://example.com
/state
/click 1
/input 2 hello
/text body
/fetch https://example.com title::text
/mcp https://example.com body
/status
/close
/exit
```

The older `cloak-scrapling-shell` is the command-oriented crawler shell. The new
`cloak-scrapling-agent` is the Agent-oriented interface with a bottom prompt,
completion, and status-oriented output.

## Python API

Prefer the unified `CloakScraplingSession` facade for new code:

```python
import asyncio
from cloak_scrapling import CloakScraplingSession

async def main() -> None:
    async with CloakScraplingSession() as session:
        await session.open("https://example.com")
        state = await session.state()
        print(state.to_text())
        page = await session.fetch("https://example.com", wait=100)
        print(page.css("title::text").get())

asyncio.run(main())
```

MCP-style call:

```python
import asyncio
from cloak_scrapling import CloakScraplingSession

async def main() -> None:
    async with CloakScraplingSession() as session:
        result = await session.mcp_fetch(
            "https://example.com",
            extraction_type="markdown",
            css_selector="main",
        )
        print(result.status)
        print(result.content)

asyncio.run(main())
```

`CloakScraplingBridge` remains available for existing scripts.

## Environment variables

| Variable | Description |
| --- | --- |
| `CLOAK_SCRAPLING_CONSOLE=1` | Enable colored sidecar console. |
| `CLOAK_SCRAPLING_CONSOLE_HOLD=1` | Keep console open after completion. |
| `CLOAK_SCRAPLING_CACHE_DIR` | Browser cache directory. |
| `CLOAK_SCRAPLING_LOG_DIR` | JSONL log directory. |
| `CLOAKBROWSER_BINARY_PATH` | Use an existing browser executable. |
| `CLOAKBROWSER_DOWNLOAD_URL` | Use an internal browser download mirror. |
| `CLOAK_SCRAPLING_VENDOR_BROWSER_DIR` | Override the bundled browser-core directory. |
| `CLOAK_SCRAPLING_USE_LOCAL_SOURCES=1` | Use local checkouts instead of vendored sources during development. |
| `CLOAKBROWSER_SOURCE_DIR` | Local CloakBrowser source directory, only used with local source override. |
| `SCRAPLING_SOURCE_DIR` | Local Scrapling source directory, only used with local source override. |

Windows example:

```powershell
$env:CLOAK_SCRAPLING_CACHE_DIR = "D:\Cache\cloak-scrapling\browser"
$env:CLOAK_SCRAPLING_LOG_DIR = "D:\Cache\cloak-scrapling\logs"
```
