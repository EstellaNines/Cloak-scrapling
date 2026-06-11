# Third-Party Sources

This repository vendors the Python source packages below so `cloak-scrapling`
can run without installing the upstream `scrapling` or `cloakbrowser` packages
as separate Python distributions.

## Scrapling

- Upstream: `https://github.com/D4Vinci/Scrapling`
- Vendored path: `src/scrapling/`
- Snapshot commit: `1490506`
- License: BSD-3-Clause
- Notice file: `third_party_licenses/SCRAPLING-BSD-3-CLAUSE.txt`

## CloakBrowser

- Upstream: `https://github.com/CloakHQ/CloakBrowser`
- Vendored path: `src/cloakbrowser/`
- Snapshot commit: `b06499b`
- License: MIT
- Notice file: `third_party_licenses/CLOAKBROWSER-MIT.txt`

## Browser Core

The Chromium browser core is a runtime asset, not part of the vendored Python
source snapshots above. `cloak-scrapling` resolves it from
`CLOAKBROWSER_BINARY_PATH`, `vendor_browser/<platform>/`, CloakBrowser cache, or
CloakBrowser's install/download path.

## Refresh Checklist

1. Replace only the relevant vendored source directory.
2. Update the matching license notice in `third_party_licenses/`.
3. Reconcile `pyproject.toml` runtime dependencies with upstream metadata.
4. Run `python -m unittest tests.test_vendored_sources -v`.
5. Run the full project verification suite documented in `docs/en/development/README.md`.
