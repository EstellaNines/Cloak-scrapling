# Cloak-scrapling

English | [简体中文](README.md)

A browser-backed scraping bridge for AI Agents. `cloak-scrapling` wraps CloakBrowser stealth Chromium and Scrapling extraction into a CLI, an MCP server, and an installable Agent Skill, so MCP-capable agents can fetch dynamic pages through a real browser.

![Cloak-scrapling workflow](docs/usage-flow.svg)

## Features

- **MCP Server**: exposes page fetching, page opening, element state, click, input, screenshot, and browser lifecycle tools.
- **CLI fetcher**: one-shot scraping with `cloak-scrapling-fetch`.
- **Interactive shell**: bilingual extraction and page interaction shell with `cloak-scrapling-shell`.
- **Agent Skill**: installable with `cloak-scrapling-install-skill` for Codex / Claude.
- **Vendored CloakBrowser + Scrapling sources**: ships both Python source trees, starts a browser, resolves the CDP WebSocket URL, and returns `text` / `html` / `markdown`.
- **BrowserAct-like browser core management**: inspect, install, and clear the current platform browser core with `cloak-scrapling-browser`.
- **Sidecar Console**: optional colored input/output audit console.

## Quick start

```powershell
python -m pip install cloak-scrapling
cloak-scrapling-fetch https://example.com --selector "title::text"
```

The `cloakbrowser` and `scrapling` Python sources are bundled in this package.
The browser core is resolved in this order: `CLOAKBROWSER_BINARY_PATH`,
`vendor_browser/<platform>/`, CloakBrowser cache, then install/download.

Install from local wheel:

```powershell
python -m pip install --force-reinstall .\dist\cloak_scrapling-0.1.1-py3-none-any.whl
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
| [Third-party sources](THIRD_PARTY_SOURCES.md) | Vendored Scrapling / CloakBrowser sources, commits, and licenses. |

## Commands

```powershell
cloak-scrapling-fetch --help
cloak-scrapling-shell --help
cloak-scrapling-mcp --help
cloak-scrapling-browser --help
cloak-scrapling-install-skill --help
cloakbrowser --help
scrapling --help
```

Interactive page operations:

```powershell
cloak-scrapling-shell --lang en
```

```text
open https://example.com
state
input 2 hello
click 3
text body
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

The package now contains the `cloak_scrapling`, `cloakbrowser`, and `scrapling`
Python packages. It builds wheel / sdist artifacts and passes:

```powershell
python -m twine check dist\*
```

## License

The integration package is MIT licensed. See [LICENSE](LICENSE).

Vendored upstream sources keep their original license notices:

- Scrapling: BSD-3-Clause, see [SCRAPLING-BSD-3-CLAUSE.txt](third_party_licenses/SCRAPLING-BSD-3-CLAUSE.txt).
- CloakBrowser: MIT, see [CLOAKBROWSER-MIT.txt](third_party_licenses/CLOAKBROWSER-MIT.txt).
