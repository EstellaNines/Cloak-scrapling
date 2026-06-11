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

## 浏览器核心管理

```powershell
cloak-scrapling-browser info
cloak-scrapling-browser info --json
cloak-scrapling-browser install
cloak-scrapling-browser clear-cache
```

## 交互式 Shell

```powershell
cloak-scrapling-shell --lang zh
```

常用命令：

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

交互模式会复用当前 CloakBrowser 会话。`state` 会返回当前页面可操作元素编号；页面变化后需要重新运行 `state` 刷新编号。

## Python API

新代码建议使用统一门面 `CloakScraplingSession`：

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

MCP 风格：

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

`CloakScraplingBridge` 仍保留，供既有脚本兼容使用。

## 常用环境变量

| 变量 | 说明 |
| --- | --- |
| `CLOAK_SCRAPLING_CONSOLE=1` | 启用彩色 sidecar 控制台。 |
| `CLOAK_SCRAPLING_CONSOLE_HOLD=1` | 任务结束后保持控制台窗口。 |
| `CLOAK_SCRAPLING_CACHE_DIR` | 浏览器缓存目录。 |
| `CLOAK_SCRAPLING_LOG_DIR` | JSONL 日志目录。 |
| `CLOAKBROWSER_BINARY_PATH` | 使用已有浏览器可执行文件。 |
| `CLOAKBROWSER_DOWNLOAD_URL` | 使用内部浏览器下载镜像。 |
| `CLOAK_SCRAPLING_VENDOR_BROWSER_DIR` | 覆盖随包浏览器核心目录。 |
| `CLOAK_SCRAPLING_USE_LOCAL_SOURCES=1` | 开发时用本地 checkout 覆盖内置源码。 |
| `CLOAKBROWSER_SOURCE_DIR` | CloakBrowser 本地源码目录，仅在启用本地覆盖时生效。 |
| `SCRAPLING_SOURCE_DIR` | Scrapling 本地源码目录，仅在启用本地覆盖时生效。 |

Windows 示例：

```powershell
$env:CLOAK_SCRAPLING_CACHE_DIR = "D:\Cache\cloak-scrapling\browser"
$env:CLOAK_SCRAPLING_LOG_DIR = "D:\Cache\cloak-scrapling\logs"
```
