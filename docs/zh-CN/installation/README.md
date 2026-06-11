# 安装与打包

## pip 安装

```powershell
python -m pip install cloak-scrapling
```

安装包内置 `cloakbrowser` 与 `scrapling` 的 Python 源码，不需要再单独安装这两个上游包。安装过程仍会拉取 `httpx`、`playwright`、`lxml`、`curl_cffi` 等三方运行依赖。

如果使用 `pipx`：

```powershell
pipx install cloak-scrapling
```

如果使用 `uv`：

```powershell
uv tool install cloak-scrapling
```

## 本地 wheel 安装

```powershell
cd F:\Workbench\EmptySpace\Tool\Cloak-scrapling
python -m pip install --force-reinstall .\dist\cloak_scrapling-0.1.1-py3-none-any.whl
```

## 源码安装

```powershell
cd F:\Workbench\EmptySpace\Tool\Cloak-scrapling
python -m pip install -e .
```

## 开发依赖

```powershell
python -m pip install -e ".[dev]"
```

`.[dev]` 包含：

- `build`
- `twine`
- `wheel`

## 打包

推荐使用内置脚本：

```powershell
.\scripts\build_package.ps1
```

产物：

```text
dist/cloak_scrapling-0.1.1-py3-none-any.whl
dist/cloak_scrapling-0.1.1.tar.gz
```

检查：

```powershell
python -m twine check dist\*
```

## 隔离构建

默认脚本使用 `python -m build --no-isolation`，适合 Windows 和离线环境。

如果需要 PEP 517 隔离构建：

```powershell
.\scripts\build_package.ps1 -Isolation
```

## 安装后验证

```powershell
cloak-scrapling-fetch --help
cloak-scrapling-shell --help
cloak-scrapling-mcp --help
cloak-scrapling-browser --help
cloak-scrapling-install-skill --help
cloakbrowser --help
scrapling --help
```
