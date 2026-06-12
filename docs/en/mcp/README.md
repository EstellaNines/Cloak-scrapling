# MCP tools

## Start server

Recommended uvx stdio mode:

```powershell
uvx cloak-scrapling-mcp
```

If the main `cloak-scrapling` package is already installed, use the console script:

```powershell
cloak-scrapling-mcp
```

HTTP debug mode:

```powershell
cloak-scrapling-mcp --http --host 127.0.0.1 --port 8765
```

Do not expose HTTP mode to untrusted networks.

## Tool list

| Tool | Description |
| --- | --- |
| `fetch` | Fetch a page through CloakBrowser + Scrapling. |
| `open` | Open a URL in the live browser page. |
| `state` | Return indexed interactive elements for the current page. |
| `click` | Click an element from the latest `state` result. |
| `input` | Fill an element from the latest `state` result. |
| `press` | Send a keyboard key to the page. |
| `scroll` | Scroll the page `up` or `down`. |
| `screenshot` | Save a full-page screenshot. |
| `get_text` | Read text from the page or a CSS selector. |
| `get_html` | Read HTML from the page or a CSS selector. |
| `status` | Show browser and CDP status. |
| `close_browser` | Close current browser. |
| `reset_browser` | Reset browser; next fetch starts a new session. |

## fetch arguments

```json
{
  "url": "https://example.com",
  "extraction_type": "markdown",
  "css_selector": "main",
  "main_content_only": true,
  "wait": 100,
  "timeout": 30000,
  "network_idle": false
}
```

| Argument | Description |
| --- | --- |
| `url` | URL to fetch. |
| `extraction_type` | `markdown` / `html` / `text`. |
| `css_selector` | Optional CSS selector. |
| `main_content_only` | Keep only main content. |
| `wait` | Wait after navigation, in milliseconds. |
| `timeout` | Timeout in milliseconds. |
| `network_idle` | Whether to wait for network idle. |

## Page interaction tools

Typical flow:

```json
{"url": "https://example.com"}
```

Call `open`, then call `state` to get element indexes, then call `click` or `input` for the target element. Indexes are valid only for the latest `state` result.

## Minimal MCP config

uvx form:

```json
{
  "mcpServers": {
    "cloak-scrapling": {
      "command": "uvx",
      "args": ["cloak-scrapling-mcp"]
    }
  }
}
```

Installed command form:

```json
{
  "mcpServers": {
    "cloak-scrapling": {
      "command": "cloak-scrapling-mcp",
      "args": []
    }
  }
}
```

Module form:

```json
{
  "mcpServers": {
    "cloak-scrapling": {
      "command": "python",
      "args": ["-m", "cloak_scrapling.mcp_server"]
    }
  }
}
```
