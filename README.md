# XGameHarness — GameStudio 共享 Agent Harness

多项目共享的 **Codex + Claude Code** 插件市场（注册名 `XGameHarness`）。
所有 GameStudio 项目从这里获取统一的 skills / agents / hooks / 流程规则。

> **版本**：两个插件的 `plugin.json` 写显式 `version`（2026-09-18 起，原来是
> commit 即版本）。**改了 harness 要 bump 它**，否则各项目静默停在旧版本 ——
> 规则和坏法见下面「修改 harness 的规范」，为什么这么定见
> [`docs/codex-parity.md`](docs/codex-parity.md)。

> **⚡ 主推入口：`/how-to-do <想做的事>`** —— 任何时间任何情况帮你澄清目标、检索
> 匹配 skill/agent、给出完整建议流程并立刻推进（无参数 = "我现在该干嘛"）。
>
> **📖 详细操作手册**：[`plugins/game-studio-core/docs/HANDBOOK.md`](plugins/game-studio-core/docs/HANDBOOK.md)
> —— 任务导向速查（「我想写策划案」→ 用哪个 skill/agent），含 hooks 说明、rules 双层
> 管理、加插件流程、故障排查。已接入项目内 `/handbook <关键词>` 直查。
>
> agent 侧执行 **R5 Skill-first 路由**（superpowers 式强制流程）：接到任务先扫
> skill 匹配，命中即调用；SessionStart hook 每 session 注入该规则。

## Codex 快速接入

需要 Python 3.11+、Git。macOS/Linux hooks 通过 Bash 选择 Python；Windows Codex
使用原生 `python`，无需 Git Bash。Claude 原有 Bash hooks 保留。

```powershell
# 当前本地仓库（包括尚未推送的改动）
codex plugin marketplace add D:/work/GameStudio/XGameHarness
codex plugin add game-studio-core@XGameHarness
codex plugin add unreal-pack@XGameHarness   # 仅 UE 项目
codex plugin marketplace list
```

其他机器在变更发布后使用仓库地址添加：
`codex plugin marketplace add https://github.com/g4berolo/XGameHarness.git`。
私有仓库需要可用的 Git 身份验证。不要同时用同名本地和远程市场。

在 Codex **新任务**里使用 `$project-init`（已有项目 `$harness-upgrade`）。它会从
实际插件目录安装项目 `AGENTS.md` 入口、13 个可选专家中的适用部分和共享规则，
不会改个人 Codex 记忆或自动提交。用 `/hooks` 审阅并信任 hook 定义；信任前自动钩子
不会执行，项目 AGENTS.md 与显式 skills 仍可使用。

| 能力 | Codex 入口 |
|---|---|
| 任务流程 | `$how-to-do`、`$start`、26 个其他技能（两个插件合计 28 个，含 vendored archify） |
| Unreal | `$unreal-workflow`；项目级 `unreal-pack--<role>` |
| 初始化／升级 | `scripts/harness.py init` / `sync` / `roster` / `doctor`；支持 `--dry-run` 和定制保护 |
| 记忆／交接 | `$session-checkpoint`；共享 team 目录 + 按任务隔离的本地机械快照 |
| hook | 共享清单、运行时 dispatch；Codex 原生 JSON payload 与 Windows 命令 |
| 校验 | `python scripts/validate.py` + `python -m unittest discover -s tests -v` |

完整安装、项目迁移、升级和验证边界见 [Codex 接入说明](docs/codex-parity.md)。
游戏开发的不足及开源对比见 [审查报告](docs/harness-game-development-review.md)。

以下 `/skill`、`subagent_type` 和 `claude plugin` 示例属于 **Claude Code**；Codex
使用 `$skill`，专家名用 `<pack>--<role>`，按上述接入说明操作。

## 插件

新增 **`blender-pack`**：本机 Blender 后台/实时建模、参考图驱动迭代、独立资产评审、
GLB/FBX 导出回读。见 [安装与使用](plugins/blender-pack/README.md)。三个 pack 共用双引擎市场；
Blender pack 不依赖 UE，两个 pack 可组合做真正的引擎导入验收。

| 插件 | 内容 | 适用 |
|---|---|---|
| `game-studio-core` | 26 个自研流程 skills（/how-to-do、/start、/brainstorm、/explore-design、/design-system、/sprint-plan、/gate-check、/project-init、/harness-upgrade、/sync-rules、/handbook…）+ 1 个 vendored 第三方 skill（`archify` 画架构/流程/时序/数据流/状态机图，见下）+ 8 个设计 agents（producer、creative-director、technical-director、narrative-director、*-designer）+ 8 个 hooks（session-state 恢复 / 身份解析 / R2 语言注入 / rules 注入 / git 校验；另有 `resolve-identity.sh` 为共享库非 hook）+ 通用 rules 源 + 流程 docs、模板、操作手册、项目接入模板 | 所有游戏项目 |
| `unreal-pack` | 1 个 unreal-workflow skill + 5 个 UE 专家 agents（unreal-specialist、ue-blueprint/gas/umg/replication-specialist）+ UE path-scoped rules 源（gameplay/ai/ui/test） | 仅 UE 项目 |
| `blender-pack` | 1 个 blender-workflow skill + blender-artist / asset-reviewer 两个角色 + 本地 MCP/CLI 执行器、五视图、网格检查、导出回读 | 需要 3D 资产的项目；需本机 Blender |

> **调用 agent 必须带插件前缀**：`subagent_type` 取 `game-studio-core:producer` /
> `unreal-pack:ue-gas-specialist` 这种全名，裸名会直接报 `Agent type not found`。
>
> **模型**：13 个 agent 全部 `model: inherit`，跟随主 session 当前模型，harness
> 不锁定 —— 硬编码模型对没有该模型权限的开发者是直接故障，而项目侧无法覆盖
> 插件 agent 的配置（同名文件只会新建一个裸名 agent）。**建议在 Opus 或 Fable
> 下调用 subagent**；单次覆盖可在 Agent 调用时传 `model` 参数。

> **vendored 第三方 skill**：`plugins/game-studio-core/skills/archify/` 是整包收录的上游
> release（[tt-a1i/archify](https://github.com/tt-a1i/archify) v2.16.0，MIT），把系统描述
> 或仓库代码变成单文件可交互架构图。**那 76 个文件与官方 `archify.zip` 逐字节一致，
> 不要直接改** —— `.gitattributes` 给该路径设了 `-text` 关掉行尾转换，保证随时能对
> SHA-256。来源、校验方法、升级步骤、它那个低频联网版本检查怎么关、品牌图标的许可
> 注意事项，见 [`plugins/game-studio-core/docs/vendored-archify.md`](plugins/game-studio-core/docs/vendored-archify.md)。

## 图

用 `archify` 画的，源在 [`docs/diagrams/`](docs/diagrams/)。每张都是**一个自包含的
可交互 HTML**：能搜节点、追上下游、按引导视图逐段看、切明暗主题、导出 PNG/SVG。
下面的 PNG 只是静态快照，**点标题打开 HTML 才是完整的**。

| 图 | 讲什么 |
|---|---|
| [**一个仓库，三条到达项目的路**](docs/diagrams/harness-overview.html) | marketplace → 两个插件 → A/B/C 三档各自怎么到项目，以及 rules 的双层结构 |
| [**一次 session 里 harness 在什么时候插话**](docs/diagrams/harness-session.html) | 8 个 hook 的三种时机、R5 Skill-first 路由、两道闸门分别拦什么 |
| [**两个仓库接在哪儿**](docs/diagrams/two-repos-contract.html) | harness 定结构、UI 照结构读，中间那四类文件就是唯一的接口 |

[![harness 全貌：三档分发](docs/diagrams/harness-overview.png)](docs/diagrams/harness-overview.html)

改图不要动 HTML，改同名的 `.json` 再重新交付：

```powershell
cd plugins\game-studio-core\skills\archify
node bin\archify.mjs validate architecture ..\..\..\..\docs\diagrams\harness-overview.architecture.json --quality showcase --json
node bin\archify.mjs deliver  architecture ..\..\..\..\docs\diagrams\harness-overview.architecture.json ..\..\..\..\docs\diagrams\harness-overview.html --quality showcase --json
node bin\archify.mjs visual-check ..\..\..\..\docs\diagrams\harness-overview.html --json
```

三张都过了 showcase 档：9 项产物检查全通过、0 错 0 警，`visual-check` 在
1440×900 / 1600×1000 / 1920×1080 / 2048×1320 四档视口、明暗两套主题下都不溢出。

## 新项目接入

在新项目根目录跑一次 **`/project-init`**（自动复制模板 + 填项目名 + 同步 rules +
输出收尾清单）。手动等价步骤见 HANDBOOK § 3。

每台开发机一次性配置（私有仓库自动更新需要）：

```bash
gh auth setup-git
# 环境变量：CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1
```

手动兜底：`/plugin marketplace update XGameHarness`。

## 已接入项目的升级

**harness 更新后，项目不会自己跟上。** 在项目里跑 **`/harness-upgrade`**，它按三档核对：

| 档 | 内容 | 更新方式 |
|---|---|---|
| A 插件本体 | skills / agents / hooks / docs / templates | `claude plugin marketplace update XGameHarness` → `claude plugin update <plugin>@XGameHarness` → **重启**。缓存按 commit SHA 钉版本，**不保证自动更新** |
| B rules 实例 | `.claude/rules/*.md` | `/sync-rules` |
| C 项目文件 | `plan/stage.md`、`CLAUDE.md`、`.claude/settings.json` … | `/harness-upgrade`，清单见 `game-studio-core/docs/project-contract.md` |

改 harness 时新增了任何项目侧必需文件，**同步在 `project-contract.md` 加一行** ——
否则老项目没有任何机制知道它的存在。

## 项目契约（hooks / skills 依赖的目录约定）

hooks 以项目根为 CWD 读以下约定路径，全部有存在性守卫（缺失 = 静默跳过）：

```
design/gdd/                      # GDD（design-docs rule / detect-gaps / pre-compact 读）
plan/                            # sprint / milestone
plan/stage.md                    # 阶段 SoT：frontmatter `current_stage` + sub-phase 矩阵。
                                 #   gate-check / project-stage-detect / start / how-to-do 均读它；
                                 #   由 /project-init 拷模板生成（无独立的 stage.txt）
team/session-state/{identity}/   # active.md 会话状态（session-start 恢复）
team/session-logs/{identity}/    # 月度轮转 session log（session-stop 写）
team/memo/{recipient}/           # 跨开发者 memo（/start surface）
docs/architecture/               # ADR
.claude/team.json                # 身份注册（resolve-identity 读）。1.3.0 起由服务器／管理员
                                 #   下发，本地不自注册：管理员提交进仓，或
                                 #   `harness.py roster --from <docs-repo>` 取回（本地副本是缓存）。
                                 #   缺失时 init/sync 退 3 并打印 NEEDS-ROSTER。
                                 #   git_users 与 git_emails 都要填 —— 只填前者换机器必断；
                                 #   仓库公开又不愿公开邮箱，就把此文件加进 .gitignore
.claude/rules/*.md               # path-scoped rules 项目实例（注入 hook 只读这里）
.claude/harness-config.json      # 可选：{"excludedAgents": ["unreal-pack:ue-replication-specialist"]}
                                 #   抑制 suggest-subagent 提示；填带前缀的 agent 全名
.claude/state/                   # hook 运行时状态（项目模板已带 .gitignore 忽略此目录）
```

## rules 双层管理

pack 内 `rules/` 目录是**分发源**（frontmatter 带 `managed-by: XGameHarness/<pack>`），
项目 `.claude/rules/` 是**运行实例**。用 `/sync-rules` 同步；项目定制（最常见 = 按项目
目录改 `paths:`）后删掉 managed-by 行即固定不被覆盖。详见 HANDBOOK § 4。

## 修改 harness 的规范

- 提交与推送遵循用户授权；发布后各项目显式更新插件，不能假设下个 session 自动生效
- **改了要让项目收到的东西，必须同时 bump 对应插件 `plugin.json` 的 `version`** ——
  忘了 bump 的表现是「推上去了，但谁都没变化」，而且**没有任何地方会报错**。
  同步改 Claude/Codex 两份 `plugin.json`，**别在 `marketplace.json` 里也写** ——
  两处都有时 Claude Code 静默取 `plugin.json` 那个，另一个会掩盖问题
- 改前 `claude plugin validate .`；坏改动回滚 = `git revert` + 各机
  `/plugin marketplace update XGameHarness`
- 插件内脚本引用自身文件用 `${CLAUDE_PLUGIN_ROOT}`（Codex hook 提供兼容别名及 `PLUGIN_ROOT`），读项目文件用相对路径 /
  `CLAUDE_PROJECT_DIR`（勿用 `__file__` 推项目根——脚本运行在插件缓存里）
- Codex 使用插件内共享 hooks，不再手工镜像 `.codex/hooks/`。旧项目存在镜像时先比对，移除重复注册需保留用户自定义项。详见 [接入说明](docs/codex-parity.md)。
- rules 源改动不会自动进入已接入项目——各项目跑 `/sync-rules` 拉取
- 加新插件流程见 HANDBOOK § 5

## 历史

从 RichLethe `.claude/`（上游 fork 自 [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)
模板 v0.3.0）于 2026-07-14 抽取泛化。RichLethe 为第一个消费方。项目专属内容
（rules 实例 / team.json / 项目 docs 三件套 / engine-reference）留在各项目仓库。
同日：仓库改名 claude-harness → XGameHarness（X = owner 代号，去 claude 以便
将来容纳其他 agent 运行时的插件）；rules / 项目模板 / 操作手册 pack 化。
