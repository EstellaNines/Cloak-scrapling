# Development and security

## Tests

```powershell
python scripts\smoke.py
python scripts\mcp_smoke.py
python scripts\cli_smoke.py
python scripts\package_mcp_smoke.py
python scripts\interactive_smoke.py
python scripts\installed_shell_smoke.py
```

Visible console smoke:

```powershell
.\scripts\visible_console_smoke.ps1
```

## Package check

```powershell
.\scripts\build_package.ps1
python -m twine check dist\*
```

## Security notes

- Do not expose `cloak-scrapling-mcp --http --host 0.0.0.0` to untrusted networks.
- `fetch` can access arbitrary URLs. Restrict allowed targets in Agent rules.
- The sidecar console records URLs, selectors, and content previews. Disable it for sensitive tasks.
- For production use, pin `CLOAK_SCRAPLING_CACHE_DIR` or `CLOAKBROWSER_BINARY_PATH`.

## Hardened behavior

- Default logs go to a user cache directory.
- Adjacent source override is disabled by default.
- Skill installer validates target paths and refuses symlink replacement.
- Sidecar console does not use `shell=True`.
- Build script cleans old artifacts before packaging.
