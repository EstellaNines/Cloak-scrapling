# MCP 工具

## 启动方式

stdio 模式：

```powershell
cloak-scrapling-mcp
```

HTTP 调试模式：

```powershell
cloak-scrapling-mcp --http --host 127.0.0.1 --port 8765
```

不建议把 HTTP 模式暴露到不可信网络。

## 工具列表

| 工具 | 说明 |
| --- | --- |
| `fetch` | 通过 CloakBrowser + Scrapling 抓取网页。 |
| `status` | 查看浏览器和 CDP 状态。 |
| `close_browser` | 关闭当前浏览器。 |
| `reset_browser` | 重置浏览器，下次抓取重新启动。 |

## fetch 参数

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

| 参数 | 说明 |
| --- | --- |
| `url` | 要抓取的 URL。 |
| `extraction_type` | `markdown` / `html` / `text`。 |
| `css_selector` | 可选 CSS selector。 |
| `main_content_only` | 是否只保留主内容。 |
| `wait` | 导航后等待毫秒数。 |
| `timeout` | 超时时间，单位毫秒。 |
| `network_idle` | 是否等待网络空闲。 |

## 最小 MCP 配置

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

模块方式：

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
