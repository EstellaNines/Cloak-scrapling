# 开发与安全

## 测试

```powershell
python -m unittest tests.test_browser_core tests.test_browser_core_cli -v
python -m unittest tests.test_vendored_sources -v
python scripts\smoke.py
python scripts\mcp_smoke.py
python scripts\cli_smoke.py
python scripts\package_mcp_smoke.py
python scripts\interactive_smoke.py
python scripts\interaction_smoke.py
python scripts\installed_shell_smoke.py
```

可见控制台测试：

```powershell
.\scripts\visible_console_smoke.ps1
```

## 打包检查

```powershell
.\scripts\build_package.ps1
python -m twine check dist\*
```

源码内置检查会确认：

- `scrapling` 与 `cloakbrowser` 均从本仓 `src/` 解析。
- `cloak-scrapling-browser` 会展示并管理浏览器核心解析结果。
- `pyproject.toml` 不再依赖外部 `scrapling[all]` 或 `cloakbrowser` 包。
- `third_party_licenses/` 保留上游许可证声明。

## 安全注意事项

- 不要把 `cloak-scrapling-mcp --http --host 0.0.0.0` 暴露到不可信网络。
- `fetch` 能访问任意 URL，Agent 规则中应限制授权目标。
- sidecar console 会记录 URL、selector 和内容预览，敏感任务建议关闭。
- 生产环境建议固定 `CLOAK_SCRAPLING_CACHE_DIR` 或 `CLOAKBROWSER_BINARY_PATH`。

## 已加固点

- 默认日志目录使用用户缓存目录。
- 默认关闭相邻源码目录覆盖。
- 浏览器核心解析优先级由 `CLOAKBROWSER_BINARY_PATH`、`vendor_browser/` 与缓存共同决定。
- 内置上游源码保留第三方许可证文件。
- Skill 安装器检查目标路径并拒绝替换 symlink。
- sidecar console 不使用 `shell=True`。
- 构建脚本会清理旧产物后再打包。
