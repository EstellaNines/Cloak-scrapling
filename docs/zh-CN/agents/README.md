# AI Agent 接入

## 安装 Skill

Codex：

```powershell
cloak-scrapling-install-skill --agent codex --target-root F:\Cache\codex --force
```

Claude：

```powershell
cloak-scrapling-install-skill --agent claude --target-root F:\Cache\claude --force
```

同时安装：

```powershell
cloak-scrapling-install-skill --agent both --force
```

## Codex

`F:\Cache\codex\config.toml`：

```toml
[mcp_servers.cloak-scrapling]
type = "stdio"
command = "cloak-scrapling-mcp"
args = []
```

可选环境变量：

```toml
[mcp_servers.cloak-scrapling.env]
CLOAK_SCRAPLING_CONSOLE = "1"
CLOAK_SCRAPLING_CONSOLE_HOLD = "1"
CLOAK_SCRAPLING_CACHE_DIR = "D:/Cache/cloak-scrapling/browser"
CLOAK_SCRAPLING_LOG_DIR = "D:/Cache/cloak-scrapling/logs"
```

## Claude Code / Claude Desktop

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

Claude CLI helper：

```powershell
claude mcp add cloak-scrapling cloak-scrapling-mcp
```

## Cursor

`.cursor/mcp.json`：

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

## Windsurf

在 MCP 设置中添加：

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

## Cline / Roo Code

在插件 MCP settings 中添加：

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

如果找不到命令，使用绝对路径或模块方式：

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

## 其他 Agent

只要支持 MCP stdio，即可使用：

```text
command: cloak-scrapling-mcp
args: []
```

如果没有 Skill 系统，可以把 `src/cloak_scrapling/agent_skill/SKILL.md` 的内容复制到 Agent 的项目规则或自定义指令中。
