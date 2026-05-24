# AI Agent setup

## Install Skill

Codex:

```powershell
cloak-scrapling-install-skill --agent codex --target-root F:\Cache\codex --force
```

Claude:

```powershell
cloak-scrapling-install-skill --agent claude --target-root F:\Cache\claude --force
```

Both:

```powershell
cloak-scrapling-install-skill --agent both --force
```

## Codex

`F:\Cache\codex\config.toml`:

```toml
[mcp_servers.cloak-scrapling]
type = "stdio"
command = "cloak-scrapling-mcp"
args = []
```

Optional env:

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

Claude CLI helper:

```powershell
claude mcp add cloak-scrapling cloak-scrapling-mcp
```

## Cursor

`.cursor/mcp.json`:

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

Add to MCP settings:

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

Add to extension MCP settings:

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

If the command is not found, use an absolute path or module form:

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

## Other agents

Any MCP stdio client can use:

```text
command: cloak-scrapling-mcp
args: []
```

If the agent does not have a Skill system, copy `src/cloak_scrapling/agent_skill/SKILL.md` into its project rules or custom instructions.
