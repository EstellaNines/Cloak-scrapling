# Installation and packaging

## pip install

```powershell
python -m pip install cloak-scrapling
```

With `pipx`:

```powershell
pipx install cloak-scrapling
```

With `uv`:

```powershell
uv tool install cloak-scrapling
```

## Install from local wheel

```powershell
cd F:\Workbench\EmptySpace\Tool\Cloak-scrapling
python -m pip install --force-reinstall .\dist\cloak_scrapling-0.1.0-py3-none-any.whl
```

## Source install

```powershell
cd F:\Workbench\EmptySpace\Tool\Cloak-scrapling
python -m pip install -e .
```

## Development dependencies

```powershell
python -m pip install -e ".[dev]"
```

The `dev` extra includes:

- `build`
- `twine`
- `wheel`

## Build package

Recommended:

```powershell
.\scripts\build_package.ps1
```

Artifacts:

```text
dist/cloak_scrapling-0.1.0-py3-none-any.whl
dist/cloak_scrapling-0.1.0.tar.gz
```

Check:

```powershell
python -m twine check dist\*
```

## Isolated build

The script defaults to `python -m build --no-isolation`, which is more stable for Windows/offline environments.

For isolated PEP 517 builds:

```powershell
.\scripts\build_package.ps1 -Isolation
```

## Verify installation

```powershell
cloak-scrapling-fetch --help
cloak-scrapling-shell --help
cloak-scrapling-mcp --help
cloak-scrapling-install-skill --help
```
