# Cloak-scrapling

English | [简体中文](README.md)

A browser-backed scraping bridge for AI Agents. `cloak-scrapling` wraps CloakBrowser stealth Chromium and Scrapling extraction into a CLI, an MCP server, and an installable Agent Skill, so MCP-capable agents can fetch dynamic pages through a real browser.

![Cloak-scrapling workflow](docs/usage-flow.svg)

## Features

- **MCP Server**: exposes `fetch`, `status`, `close_browser`, and `reset_browser`.
- **CLI fetcher**: one-shot scraping with `cloak-scrapling-fetch`.
- **Interactive shell**: bilingual crawler shell with `cloak-scrapling-shell`.
- **Agent Skill**: installable with `cloak-scrapling-install-skill` for Codex / Claude.
- **CloakBrowser + Scrapling**: starts a browser, resolves the CDP WebSocket URL, and returns `text` / `html` / `markdown`.
- **Sidecar Console**: optional colored input/output audit console.

## Quick start

```powershell
python -m pip install cloak-scrapling
cloak-scrapling-fetch https://example.com --selector "title::text"
```

Install from local wheel:

```powershell
python -m pip install --force-reinstall .\dist\cloak_scrapling-0.1.0-py3-none-any.whl
```

## Documentation

| Document | Content |
| --- | --- |
| [Installation & packaging](docs/en/installation/README.md) | pip install, local wheel, source install, package build. |
| [Usage](docs/en/usage/README.md) | CLI, interactive shell, Python API, environment variables. |
| [MCP tools](docs/en/mcp/README.md) | MCP server, tools, `fetch` arguments. |
| [AI Agent setup](docs/en/agents/README.md) | Codex, Claude, Cursor, Windsurf, Cline/Roo Code configuration. |
| [Development & security](docs/en/development/README.md) | Tests, package checks, security notes. |
| [Architecture](docs/architecture.md) | Bridge runtime flow and structure. |

## Commands

```powershell
cloak-scrapling-fetch --help
cloak-scrapling-shell --help
cloak-scrapling-mcp --help
cloak-scrapling-install-skill --help
```

## Minimal MCP config

```toml
[mcp_servers.cloak-scrapling]
type = "stdio"
command = "cloak-scrapling-mcp"
args = []
```

Fallback module form:

```toml
[mcp_servers.cloak-scrapling]
type = "stdio"
command = "python"
args = ["-m", "cloak_scrapling.mcp_server"]
```

## Status

The package builds wheel / sdist artifacts and passes:

```powershell
python -m twine check dist\*
```

## License

MIT License. See [LICENSE](LICENSE).
