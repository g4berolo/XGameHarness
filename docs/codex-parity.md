# Codex 接入、升级与验证

更新：2026-09-19（本地时区）。本文件替代原先“都没实测／大概率无需修改”的记录。
本轮本机 CLI 为 `codex-cli 0.155.0-alpha.9.2`，两插件基础版本为 `1.2.0`，本机最终安装版本为
`1.2.0+codex.20260920044226`（官方 helper 生成的开发缓存后缀）。

## 1. 市场和插件

仓库保留两套清单：Claude `.claude-plugin/marketplace.json`；Codex
`.agents/plugins/marketplace.json`。两者引用同一 `plugins/<name>/` 源目录。
Codex 条目包含 installation/authentication policy，两套 plugin.json 的 version 同步。

本机本地安装（可以使用尚未提交的工作区改动）：

```powershell
codex plugin marketplace add D:/work/GameStudio/XGameHarness
codex plugin add game-studio-core@XGameHarness
codex plugin add unreal-pack@XGameHarness
codex plugin marketplace list
codex plugin list
```

其他机器在发布本轮改动之后添加远程 Git 市场：

```text
codex plugin marketplace add https://github.com/g4berolo/XGameHarness.git
```

私有仓库需要 Git 认证。不要把远程地址当作已包含本地未推送改动。
同名市场只能选择一个来源；切换来源前检查 `marketplace list`。
CLI 命令以 `codex plugin --help` 为准，旧版客户端可能需升级。

安装之后在新任务中检查 `$how-to-do`、`$project-init`、`$unreal-workflow` 是否可用。
用 `/hooks` 查看并信任定义。**安装成功不意味着 hooks 已获信任**，不能由 harness
替用户绕过信任审查。没有信任时用项目 AGENTS.md 和显式 skills。

## 2. 项目初始化与迁移

在目标游戏项目使用 `$project-init` 或 `$harness-upgrade`，它们有独立 Codex 分支。
也可从当前加载的 core 插件根目录手工执行（Python 3.11+）：

```text
python <core-root>/scripts/harness.py init --project <game-project> --dry-run
python <core-root>/scripts/harness.py init --project <game-project>
python <core-root>/scripts/harness.py roster --project <game-project> --from <docs-repo-url>
python <core-root>/scripts/harness.py doctor --project <game-project>
```

`<...>` 是需要替换的实际路径，带空格路径加引号。UE 另传
`--unreal-root <当前启用的unreal-pack根目录>`。非 UE 不传。

身份表**不由脚本生成**（1.3.0 起没有 `--identity`）：名册归服务器／管理员，本地不自注册 ——
拿当前机器的 `git user.name` 替用户登记，换台机器就解析成 `unknown`。缺 `.claude/team.json`
时 `init/sync` 照常写完其余文件并以 **exit 3** 打印 `NEEDS-ROSTER` 指引；单仓项目由管理员
提交进本仓，拆了文档仓的用上面的 `roster`（远端记在 `.codex/harness.json` 的 `roster.remote`，
之后可省略 `--from`；本地副本是缓存，与远端不同即被覆盖）。未映射身份时 hooks 不向
unknown 共享目录写入。

初始化／同步会：

- 合并 AGENTS.md 管理块，保留块外内容；检测到块内手改也保留并报告。
- 安装 `.codex/xgameharness.md` 和项目级 `.codex/agents/*.toml`：core 8 个，UE 可选 5 个。
  默认继承宿主模型／沙箱，Claude 的 tools、memory、maxTurns 不冒充 Codex 配置。
- 同步共享 `.claude/rules/`，只更新仍带匹配 managed-by 的规则。
- 补缺 `plan/stage.md`、共享 Technology Stack 文件 `CLAUDE.md`、按已装 pack 的
  `.claude/settings.json` 和忽略项；已有阶段、team 配置和 Claude settings 不覆盖。
- 记录 `.codex/harness.json` 中来源、版本和文件哈希，用于定制保护和来源失效检查。

保留 `.claude/team.json`、`.claude/rules/` 等名称是为了兼容现有 Studio／Claude 消费方，
不是要求安装 Claude。Codex **运行时**不读 `.claude/settings.json`，但脚本在缺失时会写
——同一个仓库常常两个运行时都要用，只写 Codex 侧会让它在 Claude 里是未接入状态。
`doctor` 只验证项目文件契约，不能证明宿主已加载插件、信任 hook 或运行引擎。

旧项目若有手工 `.codex/hooks/` 镜像，先比对内容，再移除重复注册；脚本不自动删用户 hook。
同一个事件注册两份会导致重复注入／记录。

## 3. 运行时对照

| 能力 | Claude Code | Codex |
|---|---|---|
| Skills | `/skill` / Skill tool | `$skill` 或读取 SKILL.md，28 个技能共用 |
| 专家 | `<pack>:<role>` 插件 agents | `<pack>--<role>` 项目 TOML；需 init/sync |
| 角色缺失 | 报告缺少插件 | 读取角色正文主任务执行，或授权后传给现有通用子 agent |
| 工具 | Bash / Edit / Write | 支持 Bash 别名、exec_command/cmd、apply_patch 多文件／移动 |
| 项目根 | 旧脚本约定 | 从 payload cwd 向上定位项目边界，支持子目录启动 |
| 规则 | 旧 SessionStart 全量 + PostToolUse | AGENTS.md 编辑前按需读；Pre/PostToolUse 提醒匹配文件 |
| Hooks | dispatch 转发既有 Bash/Python 脚本 | dispatch 处理原生 JSON，Windows 使用 commandWindows |
| 记忆 | 原 team 会话结构 | 同一 team 知识 + sessions/<key>.md + 本地快照 |
| 更新 | Claude marketplace/plugin update | Codex marketplace upgrade（Git 来源）+ plugin add，再开新任务 |

官方当前文档说明 shell/exec 的 matcher 有 Bash 别名，但 apply_patch 输入仍是补丁，
不能只看 matcher 匹配就认为旧 `tool_input.file_path` 解析器可用。

## 4. Hook 功能及限制

共享 `hooks/hooks.json` 默认被两个宿主发现；不在 manifest 添加未经验证的额外字段。
macOS/Linux 用 Bash 启动 Python；Windows Codex 的 commandWindows 从 PLUGIN_ROOT 定位脚本。
Python 出错显式写 stderr；不会把没有运行的检查记录为通过。

- SessionStart：项目、身份、任务摘要路径和有限长度恢复预览；缺项提示。
- UserPromptSubmit：中文提醒；只提示已在项目安装且未排除的相关专家，不自动创建 agent。
- PreToolUse：暂存 JSON 检查；无效 JSON 返回 2 阻断；版本/跨成员文件/推送提示为告警。
  规则提示涵盖 patch 的新增、更新、删除和移动目标，外部路径不当作本项目规则路径。
- PostToolUse：规则补充提醒，工具导致的变动仍要由任务自行验证。
- Stop / PreCompact / SessionEnd：Codex 记录 Git 状态并保存未提交任务摘要快照。
  Stop 不续跑任务、不写重复的团队月度摘要；SessionEnd 不能代替工作中的及时保存。

Git 命令识别是辅助 guardrail，**不是 shell 语法解析器或安全策略**。处理常见
`git commit/push`、`git -C <path>`、exec workdir；先 cd/Set-Location 的命令明确提示未检查。
别名、脚本间接执行、stdin 续写、宿主绕过 hook 等不能保证覆盖。CI 才是确定性的发布门槛。

快照在 `.codex/state/sessions/{identity}/{session-key}/`，本地忽略、按任务隔离。
它保存摘要实际内容，不再声称 HEAD 能恢复未提交摘要。日志达到 1 MiB 时保留一份轮转。
长期知识仍写 GDD/ADR；个人 Codex memories 不属于这些脚本的写入范围。

## 5. 验证和发布

```powershell
python scripts/validate.py
python -m unittest discover -s tests -v
```

CI 在 Windows/Linux、Python 3.11 运行同一组测试。测试覆盖新项目、重复升级、项目定制、
子目录和中英文空格路径、多文件 patch、暂存区与工作区不同、未提交快照及任务隔离。
实际客户端安装记录见本次交付说明；**新任务技能加载、hook 信任后的真实事件、UE 编译／
PIE／打包／真机性能未由这些测试证明**。验证时逐项记录，不把单元测试标成端到端通过。

发布时同步两个 manifest 版本；本地开发可使用官方 cachebuster helper，但保持 Claude/Codex
版本一致。市场条目不重复写版本。用户未授权提交／推送时只交付工作区改动。

### 本轮本机验收记录

| 检查 | 结果 |
|---|---|
| 本地 marketplace add | 已成功，来源 `D:/work/GameStudio/XGameHarness` |
| 两插件 plugin add/list | 已安装且 enabled=true；上述最终版本 |
| 两插件缓存 | 对比实际文件 SHA-256，与源码一致（忽略 Python 字节码） |
| Windows Python 回归 | 15 项通过，含清单全部 commandWindows 的真实子进程执行 |
| Codex manifest / Claude marketplace 与两插件 manifest | 校验通过 |
| 第一方 SKILL.md 元数据 | 官方 quick_validate 校验通过；vendored archify 保持原样 |
| Git diff whitespace | 通过；archify 无修改 |
| Linux CI | 已添加 workflow，本机未执行 Linux runner |
| 新任务 skill discovery / 受信 hook 生命周期 | 待用户在新任务中验证；未绕过 hook trust |
| 游戏引擎编译、运行、打包、性能 | 未执行，本仓库不包含消费方游戏工程 |

工作区变更尚未提交／推送，因此远程 Git 市场当前不包含本轮改动。

## 6. 核对来源

- [官方插件打包及市场注册](https://developers.openai.com/plugins/build/plugins)
- [官方 hooks：事件、payload、Windows 命令、插件发现与信任](https://learn.chatgpt.com/docs/hooks)
- [官方项目级自定义 agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

上面是 2026-09-19 读取的当前文档，运行时会演进；本机 CLI help 和实际检查结果优先于历史推测。
