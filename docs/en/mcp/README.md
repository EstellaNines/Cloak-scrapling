# MCP tools

## Start server

stdio mode:

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

## Minimal MCP config

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
