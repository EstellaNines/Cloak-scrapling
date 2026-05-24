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

## Interactive shell

```powershell
cloak-scrapling-shell --lang en
```

Common commands:

```text
help
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

## Python API

```python
import asyncio
from cloak_scrapling import CloakScraplingBridge

async def main() -> None:
    async with CloakScraplingBridge() as bridge:
        page = await bridge.fetch("https://example.com", wait=100)
        print(page.css("title::text").get())

asyncio.run(main())
```

MCP-style call:

```python
import asyncio
from cloak_scrapling import CloakScraplingBridge

async def main() -> None:
    async with CloakScraplingBridge() as bridge:
        result = await bridge.mcp_stealthy_fetch(
            "https://example.com",
            extraction_type="markdown",
            css_selector="main",
        )
        print(result.status)
        print(result.content)

asyncio.run(main())
```

## Environment variables

| Variable | Description |
| --- | --- |
| `CLOAK_SCRAPLING_CONSOLE=1` | Enable colored sidecar console. |
| `CLOAK_SCRAPLING_CONSOLE_HOLD=1` | Keep console open after completion. |
| `CLOAK_SCRAPLING_CACHE_DIR` | Browser cache directory. |
| `CLOAK_SCRAPLING_LOG_DIR` | JSONL log directory. |
| `CLOAKBROWSER_BINARY_PATH` | Use an existing browser executable. |
| `CLOAKBROWSER_DOWNLOAD_URL` | Use an internal browser download mirror. |

Windows example:

```powershell
$env:CLOAK_SCRAPLING_CACHE_DIR = "D:\Cache\cloak-scrapling\browser"
$env:CLOAK_SCRAPLING_LOG_DIR = "D:\Cache\cloak-scrapling\logs"
```
