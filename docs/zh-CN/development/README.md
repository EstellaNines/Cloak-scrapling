# 开发与安全

## 测试

```powershell
python scripts\smoke.py
python scripts\mcp_smoke.py
python scripts\cli_smoke.py
python scripts\package_mcp_smoke.py
python scripts\interactive_smoke.py
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

## 安全注意事项

- 不要把 `cloak-scrapling-mcp --http --host 0.0.0.0` 暴露到不可信网络。
- `fetch` 能访问任意 URL，Agent 规则中应限制授权目标。
- sidecar console 会记录 URL、selector 和内容预览，敏感任务建议关闭。
- 生产环境建议固定 `CLOAK_SCRAPLING_CACHE_DIR` 或 `CLOAKBROWSER_BINARY_PATH`。

## 已加固点

- 默认日志目录使用用户缓存目录。
- 默认关闭相邻源码目录覆盖。
- Skill 安装器检查目标路径并拒绝替换 symlink。
- sidecar console 不使用 `shell=True`。
- 构建脚本会清理旧产物后再打包。
