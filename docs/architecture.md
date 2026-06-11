# Architecture

## Purpose

`Cloak-scrapling` is a vendored integration layer. It carries the upstream
Python sources for CloakBrowser and Scrapling inside this repository, then adds
the bridge, CLI, MCP server, and Agent Skill that make them work together:

- `src/cloakbrowser/` owns Chromium launch, binary cache, fingerprint flags, and optional humanized actions.
- `src/scrapling/` owns page fetching, response objects, selectors, content conversion, sessions, and MCP tools.
- `src/cloak_scrapling/` owns the glue needed to launch CloakBrowser, pass its CDP WebSocket URL into Scrapling, and expose page interaction commands.

Vendoring removes the runtime dependency on separately installed `cloakbrowser`
and `scrapling` packages. The browser core is managed separately: if a
`vendor_browser/<platform>/` core exists it is preferred, otherwise the
CloakBrowser cache/install path is used. Snapshot commits and license notices
are tracked in [`THIRD_PARTY_SOURCES.md`](../THIRD_PARTY_SOURCES.md).

## Runtime Flow

```text
AI Agent / script
  -> cloak_scrapling.CloakScraplingSession
  -> vendored cloakbrowser.launch_async(...)
  -> http://127.0.0.1:<port>/json/version
  -> ws://127.0.0.1:<port>/devtools/browser/<id>
  -> vendored Scrapling cdp_url
  -> parsed Response / MCP ResponseModel
```

`CloakScraplingBridge` remains as a compatibility layer for existing scripts.
New adapters should use `CloakScraplingSession`, which exposes one facade for
browser startup, direct fetch, MCP fetch, and live page interaction.

## Core API Layout

- `runtime.py`: cache paths, local source overrides, free port discovery, and CDP readiness checks.
- `browser_core.py`: browser core resolution, install, cache, and vendor lookup.
- `browser_models.py`: serializable page state and indexed element models.
- `browser_controller.py`: Playwright CDP connection and live page actions.
- `scraping.py`: Scrapling direct fetch and Scrapling MCP fetch helpers.
- `session.py`: public `CloakScraplingSession` facade used by adapters.
- `agent_cli.py`: Codex / Claude Code style slash-command Agent CLI over the core facade.
- `interactive.py` and `mcp_server.py`: thin legacy shell and MCP adapters over the core facade.

The Agent CLI builds on `CloakScraplingSession` rather than calling
CloakBrowser, Scrapling, or Playwright directly.

## Reserved Locations

- `src/cloak_scrapling/`: core session API, bridge compatibility, adapters, and import-safe runtime helpers.
- `src/cloakbrowser/`: vendored CloakBrowser Python package.
- `src/scrapling/`: vendored Scrapling Python package.
- `vendor_browser/`: optional offline browser core drops, one directory per platform.
- `third_party_licenses/`: upstream license notices for vendored sources.
- `scripts/`: local executable examples and smoke tests.
- `docs/`: integration notes and operational playbooks.
- user cache directory: downloaded CloakBrowser Chromium binary cache, overrideable by environment.
- `.logs/`: Agent console JSONL event logs, ignored by Git.

## Import Rules

- `scripts/` may import `cloak_scrapling`.
- `cloak_scrapling` may import `cloakbrowser` and `scrapling`.
- Neither `CloakBrowser` nor `scrapling` should import this package.
- Keep vendored upstream changes contained to `src/cloakbrowser/` and `src/scrapling/`.
- When refreshing vendored sources, update `third_party_licenses/` and dependency metadata together.

## Environment Overrides

- `CLOAK_SCRAPLING_USE_LOCAL_SOURCES=1`: opt into development source overrides.
- `CLOAKBROWSER_SOURCE_DIR`: override the vendored CloakBrowser package with a local checkout.
- `SCRAPLING_SOURCE_DIR`: override the vendored Scrapling package with a local checkout.
- `CLOAK_SCRAPLING_VENDOR_BROWSER_DIR`: override the vendored browser-core directory.
- `CLOAK_SCRAPLING_CACHE_DIR`: override the Cloak-scrapling browser cache directory.
- `CLOAKBROWSER_CACHE_DIR`: override the Chromium binary cache directory.
- `CLOAK_SCRAPLING_CONSOLE`: set to `1` to open the colored Agent console automatically.
- `CLOAK_SCRAPLING_CONSOLE_HOLD`: set to `1` to keep the console open after shutdown.

Source overrides are disabled by default. Normal installs use the vendored
packages shipped under `src/`.
