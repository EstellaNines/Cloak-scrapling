# Cloak-scrapling

[English](README.en.md) | 简体中文

面向 AI Agent 的浏览器爬虫桥接工具包。`cloak-scrapling` 将 CloakBrowser 的隐身 Chromium 能力与 Scrapling 的页面抽取能力封装为 CLI、MCP Server 和 Agent Skill，让支持 MCP 的 Agent 可以通过真实浏览器抓取动态网页。

![Cloak-scrapling 使用流程图](docs/usage-flow.svg)

## 功能概览

- **MCP Server**：提供 `fetch`、`status`、`close_browser`、`reset_browser`。
- **CLI 抓取**：通过 `cloak-scrapling-fetch` 执行一次性抓取。
- **交互式 Shell**：通过 `cloak-scrapling-shell` 使用中英文交互式爬虫命令。
- **Agent Skill**：通过 `cloak-scrapling-install-skill` 安装到 Codex / Claude。
- **CloakBrowser + Scrapling**：自动启动浏览器、解析 CDP WebSocket，并返回 `text` / `html` / `markdown`。
- **Sidecar Console**：可选显示彩色输入输出日志。

## 快速开始

```powershell
python -m pip install cloak-scrapling
cloak-scrapling-fetch https://example.com --selector "title::text"
```

本地 wheel 安装：

```powershell
python -m pip install --force-reinstall .\dist\cloak_scrapling-0.1.0-py3-none-any.whl
```

## 文档

| 文档 | 内容 |
| --- | --- |
| [安装与打包](docs/zh-CN/installation/README.md) | pip 安装、本地 wheel、源码安装、重新打包。 |
| [使用说明](docs/zh-CN/usage/README.md) | CLI、交互式 Shell、Python API、环境变量。 |
| [MCP 工具](docs/zh-CN/mcp/README.md) | MCP Server、工具列表、`fetch` 参数。 |
| [AI Agent 接入](docs/zh-CN/agents/README.md) | Codex、Claude、Cursor、Windsurf、Cline/Roo Code 配置。 |
| [开发与安全](docs/zh-CN/development/README.md) | 测试、打包检查、安全注意事项。 |
| [架构说明](docs/architecture.md) | 桥接链路与实现结构。 |

## 命令

```powershell
cloak-scrapling-fetch --help
cloak-scrapling-shell --help
cloak-scrapling-mcp --help
cloak-scrapling-install-skill --help
```

## 基本 MCP 配置

```toml
[mcp_servers.cloak-scrapling]
type = "stdio"
command = "cloak-scrapling-mcp"
args = []
```

如果 Agent 找不到命令，可以使用模块方式：

```toml
[mcp_servers.cloak-scrapling]
type = "stdio"
command = "python"
args = ["-m", "cloak_scrapling.mcp_server"]
```

## 状态

当前项目已完成 wheel / sdist 打包，并通过：

```powershell
python -m twine check dist\*
```

## 许可证

MIT License。见 [LICENSE](LICENSE)。
