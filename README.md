# Cloak-scrapling

[English](README.en.md) | 简体中文

`cloak-scrapling` 是面向 AI Agent 的浏览器爬虫框架层：它将 vendored
CloakBrowser、vendored Scrapling、浏览器核心管理、统一 Session API、
CLI、MCP Server 与 Agent Skill 收束到同一套运行时中，让 Agent 可以用真实
Chromium 完成动态页面抽取与页面交互。

![Cloak-scrapling 使用流程图](docs/usage-flow.svg)

## 框架定位

`CloakScraplingSession` 是当前框架的唯一核心门面。新代码、CLI、MCP、
Agent CLI 和旧交互 Shell 都应通过它调用能力，而不是直接触碰 CloakBrowser、
Scrapling 或 Playwright。

```text
AI Agent / CLI / Python script
  -> CloakScraplingSession
  -> CloakScraplingBridge
  -> CloakBrowser Chromium + CDP
  -> Scrapling fetch / MCP extraction
  -> BrowserController page actions
```

当前包内同时携带：

- `cloak_scrapling`：框架胶水层、Session API、CLI、MCP、Skill 与浏览器核心解析。
- `cloakbrowser`：内置上游 Python 源码，负责隐身浏览器启动与缓存。
- `scrapling`：内置上游 Python 源码，负责页面抓取、选择器与内容转换。
- `vendor_browser/`：可选离线浏览器核心目录；无本地核心时仍可使用 CloakBrowser 缓存或下载机制。

## 快速开始

安装并执行一次抓取：

```powershell
python -m pip install cloak-scrapling
cloak-scrapling-fetch https://example.com --selector "title::text"
```

检查或安装当前平台浏览器核心：

```powershell
cloak-scrapling-browser info
cloak-scrapling-browser install
```

浏览器核心解析顺序为：

```text
CLOAKBROWSER_BINARY_PATH
  -> vendor_browser/<platform>/
  -> CloakBrowser cache
  -> CloakBrowser install/download
```

本地 wheel 安装示例：

```powershell
python -m pip install --force-reinstall .\dist\cloak_scrapling-0.1.1-py3-none-any.whl
```

## 公开入口

| 入口 | 用途 |
| --- | --- |
| `CloakScraplingSession` | 统一核心 API，覆盖抓取、MCP 抽取与页面交互。 |
| `cloak-scrapling-agent` | 类 Codex / Claude Code 的 Agent CLI UI。 |
| `cloak-scrapling-shell` | 旧式命令交互 Shell，支持中英文命令。 |
| `cloak-scrapling-fetch` | 一次性命令行抓取。 |
| `cloak-scrapling-mcp` | MCP Server，支持 `uvx cloak-scrapling-mcp` 免安装调用。 |
| `cloak-scrapling-browser` | 浏览器核心信息、安装与缓存清理。 |
| `cloak-scrapling-install-skill` | 安装 Agent Skill 到 Codex / Claude。 |

## 能力矩阵

| 能力 | Session API | CLI / MCP 对应 |
| --- | --- | --- |
| 直接抓取 | `fetch(url, **kwargs)` | `cloak-scrapling-fetch` / shell `fetch` |
| MCP 风格抽取 | `mcp_fetch(url, **kwargs)` | shell `/mcp` / MCP `fetch` |
| 打开页面 | `open(url)` | Agent CLI `/open` / MCP `open` |
| 页面状态 | `state()` | Agent CLI `/state` / MCP `state` |
| 点击元素 | `click(index)` | Agent CLI `/click` / MCP `click` |
| 输入文本 | `input(index, text)` | Agent CLI `/input` / MCP `input` |
| 按键 | `press(key)` | Agent CLI `/press` / MCP `press` |
| 滚动 | `scroll(direction)` | Agent CLI `/scroll` / MCP `scroll` |
| 截图 | `screenshot(path=None)` | Agent CLI `/screenshot` / MCP `screenshot` |
| 文本读取 | `get_text(selector=None)` | Agent CLI `/text` / MCP `get_text` |
| HTML 读取 | `get_html(selector=None)` | Agent CLI `/html` / MCP `get_html` |

## Agent CLI UI

启动：

```powershell
cloak-scrapling-agent --headful
```

常用流程：

```text
/help
/open https://example.com
/state
/text body
/fetch https://example.com title::text
/status
/close
/exit
```

Agent CLI 当前采用类 Codex / Claude Code 的 transcript 界面：

- 灰底 `› /command`：用户输入的内容或 slash command。
- 白色圆点 `● content`：通过抓取、MCP 抽取或文本读取返回的内容。
- 绿色圆点 `● opened ...`：浏览器动作正确返回的内容，并高亮 `status=`、`title=`、`url=`、`path=` 等标志词。

`cloak-scrapling-shell` 仍保留为命令式爬虫壳；`cloak-scrapling-agent`
则面向 Agent 操作流，提供底部输入、slash command、命令补全、状态输出与
transcript 样式。

## MCP 与 Skill 适配状态

MCP 当前适配。`cloak-scrapling-mcp` 已通过 `CloakScraplingSession` 持有核心会话，
并暴露以下工具：

```text
status / fetch / open / state / click / input / press / scroll
screenshot / get_text / get_html / close_browser / reset_browser
```

推荐 uvx MCP 配置：

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

若已安装主包，也可使用 console script：

```toml
[mcp_servers.cloak-scrapling]
type = "stdio"
command = "cloak-scrapling-mcp"
args = []
```

若 Agent 找不到可执行命令，可改用模块方式：

```toml
[mcp_servers.cloak-scrapling]
type = "stdio"
command = "python"
args = ["-m", "cloak_scrapling.mcp_server"]
```

Agent Skill 当前基本适配。它会提示 Agent 优先使用 MCP Server，并在没有 MCP
时退回 CLI；本轮同步刷新 Skill 文案，使其明确当前 Agent CLI 已实现，并说明
transcript UI 语义。

安装 Skill：

```powershell
cloak-scrapling-install-skill --agent codex --force
cloak-scrapling-install-skill --agent claude --force
```

## Python API

新代码优先使用 `CloakScraplingSession`：

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

`CloakScraplingBridge` 仍保留，用于兼容既有脚本；新增适配器不应再绕过
`CloakScraplingSession`。

## 文档

| 文档 | 内容 |
| --- | --- |
| [安装与打包](docs/zh-CN/installation/README.md) | pip 安装、本地 wheel、源码安装、重新打包。 |
| [使用说明](docs/zh-CN/usage/README.md) | CLI、交互式 Shell、Python API、环境变量。 |
| [MCP 工具](docs/zh-CN/mcp/README.md) | MCP Server、工具列表、`fetch` 参数。 |
| [AI Agent 接入](docs/zh-CN/agents/README.md) | Codex、Claude、Cursor、Windsurf、Cline/Roo Code 配置。 |
| [开发与安全](docs/zh-CN/development/README.md) | 测试、打包检查、安全注意事项。 |
| [架构说明](docs/architecture.md) | 桥接链路与模块结构。 |
| [第三方源码](THIRD_PARTY_SOURCES.md) | 内置 Scrapling / CloakBrowser 来源、提交与许可证。 |

## 开发验证

常用验证命令：

```powershell
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 -m compileall -q src scripts tests
git diff --check
PYTHONPATH=src python3 -m cloak_scrapling.agent_cli --once /status
```

打包检查：

```powershell
python -m build
python -m twine check dist\*
```

## 许可证

本项目主体为 MIT License。见 [LICENSE](LICENSE)。

内置上游源码保留原许可证声明：

- Scrapling：BSD-3-Clause，见 [SCRAPLING-BSD-3-CLAUSE.txt](third_party_licenses/SCRAPLING-BSD-3-CLAUSE.txt)。
- CloakBrowser：MIT，见 [CLOAKBROWSER-MIT.txt](third_party_licenses/CLOAKBROWSER-MIT.txt)。
