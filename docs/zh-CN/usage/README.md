# 使用说明

## 一次性抓取

```powershell
cloak-scrapling-fetch https://example.com --selector "title::text"
```

抓取正文预览：

```powershell
cloak-scrapling-fetch https://example.com --limit 3000
```

使用 MCP 风格抽取：

```powershell
cloak-scrapling-fetch https://example.com --mcp --selector body --extraction-type text
```

输出 Markdown：

```powershell
cloak-scrapling-fetch https://example.com --mcp --selector main --extraction-type markdown
```

显示浏览器：

```powershell
cloak-scrapling-fetch https://example.com --headful
```

启用 sidecar 控制台：

```powershell
cloak-scrapling-fetch https://example.com --selector "title::text" --console
```

## 交互式 Shell

```powershell
cloak-scrapling-shell --lang zh
```

常用命令：

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

MCP 风格：

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

## 常用环境变量

| 变量 | 说明 |
| --- | --- |
| `CLOAK_SCRAPLING_CONSOLE=1` | 启用彩色 sidecar 控制台。 |
| `CLOAK_SCRAPLING_CONSOLE_HOLD=1` | 任务结束后保持控制台窗口。 |
| `CLOAK_SCRAPLING_CACHE_DIR` | 浏览器缓存目录。 |
| `CLOAK_SCRAPLING_LOG_DIR` | JSONL 日志目录。 |
| `CLOAKBROWSER_BINARY_PATH` | 使用已有浏览器可执行文件。 |
| `CLOAKBROWSER_DOWNLOAD_URL` | 使用内部浏览器下载镜像。 |

Windows 示例：

```powershell
$env:CLOAK_SCRAPLING_CACHE_DIR = "D:\Cache\cloak-scrapling\browser"
$env:CLOAK_SCRAPLING_LOG_DIR = "D:\Cache\cloak-scrapling\logs"
```
