# Architecture

## Purpose

`Cloak-scrapling` is a composition layer, not a fork. It keeps browser stealth and scraping concerns separated:

- CloakBrowser owns Chromium launch, binary cache, fingerprint flags, and optional humanized actions.
- Scrapling owns page fetching, response objects, selectors, content conversion, sessions, and MCP tools.
- This repository owns only the glue needed to launch CloakBrowser and pass its CDP WebSocket URL into Scrapling.

## Runtime Flow

```text
AI Agent / script
  -> cloak_scrapling.CloakScraplingBridge
  -> cloakbrowser.launch_async(...)
  -> http://127.0.0.1:<port>/json/version
  -> ws://127.0.0.1:<port>/devtools/browser/<id>
  -> Scrapling cdp_url
  -> parsed Response / MCP ResponseModel
```

## Reserved Locations

- `src/cloak_scrapling/`: bridge code and import-safe runtime helpers.
- `scripts/`: local executable examples and smoke tests.
- `docs/`: integration notes and operational playbooks.
- `.cloakbrowser-cache/`: downloaded CloakBrowser Chromium binary cache, ignored by Git.
- `.logs/`: Agent console JSONL event logs, ignored by Git.

## Import Rules

- `scripts/` may import `cloak_scrapling`.
- `cloak_scrapling` may import `cloakbrowser` and `scrapling`.
- Neither `CloakBrowser` nor `scrapling` should import this package.
- Do not copy upstream source files into this repository. Use local path dependencies or environment variables instead.

## Environment Overrides

- `CLOAKBROWSER_SOURCE_DIR`: override the local CloakBrowser checkout path.
- `SCRAPLING_SOURCE_DIR`: override the local Scrapling checkout path.
- `CLOAKBROWSER_CACHE_DIR`: override the Chromium binary cache directory.
- `CLOAK_SCRAPLING_CONSOLE`: set to `1` to open the colored Agent console automatically.
- `CLOAK_SCRAPLING_CONSOLE_HOLD`: set to `1` to keep the console open after shutdown.

Defaults assume all three directories are siblings under `F:\Workbench\EmptySpace\Tool`.
