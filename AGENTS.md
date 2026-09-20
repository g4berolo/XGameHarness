# XGameHarness 维护指南

本仓库是共享游戏开发插件市场，支持 Codex 与 Claude Code。默认中文交流。

- 两个插件的 `.claude-plugin/plugin.json` 与 `.codex-plugin/plugin.json` 版本保持一致。
  分发内容改变需更新版本，marketplace 条目不重复填写版本。
- 通用 skills、角色正文、rules、项目知识共用；Codex 行为入口是
  `plugins/game-studio-core/scripts/harness.py` 和 `hooks/dispatch.py`。
- 自定义项目数据不得在升级时静默覆盖；Codex 个人配置／记忆不属于项目迁移范围。
- `plugins/game-studio-core/skills/archify/` 是 vendored release，不直接编辑。
- 验证：`python -m unittest discover -s tests -v` 和 `python scripts/validate.py`。
  Windows 使用 Python 3.11+；PowerShell 可直接捕获输出。使用 Git Bash 时按当前宿主
  的输出捕获约定处理，脚本内部逻辑不能依赖交互终端。
- 验证通过不代表引擎运行通过。文档分开记录源码测试、插件安装、hook 实际触发及游戏实测。
- 不自动提交或推送；分支与提交策略遵循本次用户请求。
