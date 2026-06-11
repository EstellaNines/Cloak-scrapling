# Vendored Browser Core

This directory is reserved for optional offline browser-core drops.

`cloak-scrapling` does not commit Chromium binaries in v1. If an offline build or
deployment process provides a CloakBrowser-compatible Chromium binary, place it
under one of these platform directories:

- `vendor_browser/darwin-arm64/Chromium.app/Contents/MacOS/Chromium`
- `vendor_browser/darwin-x64/Chromium.app/Contents/MacOS/Chromium`
- `vendor_browser/linux-x64/chrome`
- `vendor_browser/linux-arm64/chrome`
- `vendor_browser/windows-x64/chrome.exe`

At runtime, `cloak-scrapling` resolves browser cores in this order:

1. `CLOAKBROWSER_BINARY_PATH`
2. this `vendor_browser/<platform>/` directory
3. CloakBrowser's cache
4. CloakBrowser's download/install path
