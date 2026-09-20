---
name: unreal-workflow
description: "Unreal Engine 专家入口：C++、Blueprint、GAS、UMG、复制与项目 Codex 专家安装。"
---

# Unreal 工作流

插件根目录为本 SKILL.md 向上两级。先读取项目引擎版本和实际代码，再按任务读取
本插件 `agents/` 内对应角色说明及 `rules/` 内适用规则，不一次读全。

| 任务 | 角色文件 |
|---|---|
| UE 架构、引擎边界、打包 | `agents/unreal-specialist.md` |
| Blueprint / C++ 边界 | `agents/ue-blueprint-specialist.md` |
| Gameplay Ability System | `agents/ue-gas-specialist.md` |
| UMG / CommonUI | `agents/ue-umg-specialist.md` |
| 网络复制 | `agents/ue-replication-specialist.md` |

Claude 使用 `unreal-pack:<role>`。Codex 使用项目 `.codex/agents/` 中已安装的
`unreal-pack--<role>`；不存在时主 agent 读取角色执行，不能调用不存在的类型。
需要安装时定位已启用的 game-studio-core，从其实际根目录执行：

```text
python <core-root>/scripts/harness.py init --project <project-root> --unreal-root <this-plugin-root>
```

仅在用户或适用指令授权时委派；模型和沙箱继承当前宿主。角色中 Claude 特有的
tools/memory/maxTurns 元数据在 Codex 不生效，任务实际授权优先于旧角色审批措辞。

二进制资产用可用的编辑器工具修改。每次交付分开报告：文本代码验证、引擎编译、
PIE/打包运行、目标机性能、真人体验。未执行的项标记未验证，不从代码推断运行通过。
