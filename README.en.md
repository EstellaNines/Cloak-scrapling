# Cloak-scrapling

English | [简体中文](README.md)

`cloak-scrapling` is a browser-backed scraping framework layer for AI Agents. It
brings vendored CloakBrowser, vendored Scrapling, browser-core management, a
single Session API, CLIs, an MCP server, and an installable Agent Skill into one
runtime so agents can extract and interact with dynamic pages through a real
Chromium browser.

![Cloak-scrapling workflow](docs/usage-flow.svg)

## Framework Position

`CloakScraplingSession` is the central facade for the current framework. New
code, CLIs, MCP tools, the Agent CLI, and the legacy interactive shell should
call through this facade instead of reaching directly into CloakBrowser,
Scrapling, or Playwright.

```text
AI Agent / CLI / Python script
  -> CloakScraplingSession
  -> CloakScraplingBridge
  -> CloakBrowser Chromium + CDP
  -> Scrapling fetch / MCP extraction
  -> BrowserController page actions
```

The package currently ships:

- `cloak_scrapling`: framework glue, Session API, CLIs, MCP, Skill, and browser-core resolution.
- `cloakbrowser`: vendored upstream Python sources for stealth browser launch and cache handling.
- `scrapling`: vendored upstream Python sources for page fetching, selectors, and content conversion.
- `vendor_browser/`: optional offline browser core drops; without a local core, CloakBrowser cache or download remains available.

## Quick Start

Install and run a one-shot fetch:

```powershell
python -m pip install cloak-scrapling
cloak-scrapling-fetch https://example.com --selector "title::text"
```

Inspect or install the current platform browser core:

```powershell
cloak-scrapling-browser info
cloak-scrapling-browser install
```

Browser core resolution order:

```text
CLOAKBROWSER_BINARY_PATH
  -> vendor_browser/<platform>/
  -> CloakBrowser cache
  -> CloakBrowser install/download
```

Install from a local wheel:

```powershell
python -m pip install --force-reinstall .\dist\cloak_scrapling-0.1.1-py3-none-any.whl
```

## Public Entrypoints

| Entrypoint | Purpose |
| --- | --- |
| `CloakScraplingSession` | Unified core API for fetch, MCP extraction, and page interaction. |
| `cloak-scrapling-agent` | Codex / Claude Code style Agent CLI UI. |
| `cloak-scrapling-shell` | Legacy command shell with bilingual commands. |
| `cloak-scrapling-fetch` | One-shot command-line fetcher. |
| `cloak-scrapling-mcp` | MCP server for agent tool calls. |
| `cloak-scrapling-browser` | Browser core info, install, and cache cleanup. |
| `cloak-scrapling-install-skill` | Installs the Agent Skill into Codex / Claude. |

## Capability Matrix

| Capability | Session API | CLI / MCP Mapping |
| --- | --- | --- |
| Direct fetch | `fetch(url, **kwargs)` | `cloak-scrapling-fetch` / shell `fetch` |
| MCP-style extraction | `mcp_fetch(url, **kwargs)` | shell `/mcp` / MCP `fetch` |
| Open page | `open(url)` | Agent CLI `/open` / MCP `open` |
| Page state | `state()` | Agent CLI `/state` / MCP `state` |
| Click element | `click(index)` | Agent CLI `/click` / MCP `click` |
| Type text | `input(index, text)` | Agent CLI `/input` / MCP `input` |
| Press key | `press(key)` | Agent CLI `/press` / MCP `press` |
| Scroll | `scroll(direction)` | Agent CLI `/scroll` / MCP `scroll` |
| Screenshot | `screenshot(path=None)` | Agent CLI `/screenshot` / MCP `screenshot` |
| Read text | `get_text(selector=None)` | Agent CLI `/text` / MCP `get_text` |
| Read HTML | `get_html(selector=None)` | Agent CLI `/html` / MCP `get_html` |

## Agent CLI UI

Start it with:

```powershell
cloak-scrapling-agent --headful
```

Typical flow:

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

The Agent CLI now uses a Codex / Claude Code style transcript:

- Grey-backed `› /command`: user input or slash command.
- White dot `● content`: content returned by fetch, MCP extraction, or text reads.
- Green dot `● opened ...`: successful browser action output, with markers such as `status=`, `title=`, `url=`, and `path=` highlighted.

`cloak-scrapling-shell` remains the command-oriented crawler shell.
`cloak-scrapling-agent` is the Agent-oriented interface with bottom input,
slash commands, completion, status output, and transcript styling.

## MCP and Skill Compatibility

MCP is currently compatible. `cloak-scrapling-mcp` holds its browser session
through `CloakScraplingSession` and exposes these tools:

```text
status / fetch / open / state / click / input / press / scroll
screenshot / get_text / get_html / close_browser / reset_browser
```

Minimal MCP config:

```toml
[mcp_servers.cloak-scrapling]
type = "stdio"
command = "cloak-scrapling-mcp"
args = []
```

If the agent cannot find the executable command, use the module form:

```toml
[mcp_servers.cloak-scrapling]
type = "stdio"
command = "python"
args = ["-m", "cloak_scrapling.mcp_server"]
```

The Agent Skill is also basically compatible. It instructs agents to prefer the
MCP server and fall back to CLIs when MCP is unavailable. This round refreshes
the Skill wording so it treats the Agent CLI as current functionality and
documents the transcript UI semantics.

Install the Skill:

```powershell
cloak-scrapling-install-skill --agent codex --force
cloak-scrapling-install-skill --agent claude --force
```

## Python API

Prefer `CloakScraplingSession` for new code:

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

`CloakScraplingBridge` remains available for existing scripts. New adapters
should not bypass `CloakScraplingSession`.

## Documentation

| Document | Content |
| --- | --- |
| [Installation & packaging](docs/en/installation/README.md) | pip install, local wheel, source install, package build. |
| [Usage](docs/en/usage/README.md) | CLI, interactive shell, Python API, environment variables. |
| [MCP tools](docs/en/mcp/README.md) | MCP server, tools, `fetch` arguments. |
| [AI Agent setup](docs/en/agents/README.md) | Codex, Claude, Cursor, Windsurf, Cline/Roo Code configuration. |
| [Development & security](docs/en/development/README.md) | Tests, package checks, security notes. |
| [Architecture](docs/architecture.md) | Bridge runtime flow and module structure. |
| [Third-party sources](THIRD_PARTY_SOURCES.md) | Vendored Scrapling / CloakBrowser sources, commits, and licenses. |

## Development Verification

Common verification commands:

```powershell
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 -m compileall -q src scripts tests
git diff --check
PYTHONPATH=src python3 -m cloak_scrapling.agent_cli --once /status
```

Package checks:

```powershell
python -m build
python -m twine check dist\*
```

## License

The integration package is MIT licensed. See [LICENSE](LICENSE).

Vendored upstream sources keep their original license notices:

- Scrapling: BSD-3-Clause, see [SCRAPLING-BSD-3-CLAUSE.txt](third_party_licenses/SCRAPLING-BSD-3-CLAUSE.txt).
- CloakBrowser: MIT, see [CLOAKBROWSER-MIT.txt](third_party_licenses/CLOAKBROWSER-MIT.txt).
