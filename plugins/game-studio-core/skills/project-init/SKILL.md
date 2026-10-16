---
name: project-init
description: "新项目接入 XGameHarness：取得团队身份注册表 team.json（服务器／管理员下发，本地不自注册）、复制项目模板（settings.json / harness-config.json / CLAUDE.md / .gitignore）、填充项目名、同步 path-scoped rules、初始化目录约定。在新项目根目录（空目录或已有代码）运行一次即可。"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Skill
---

参数：[项目名]


> **运行时适配**：先按需读取本插件 [`docs/codex-runtime.md`](../../docs/codex-runtime.md)。
> Codex 用 `$技能名` 或读取 SKILL.md；共享流程中的 Claude 工具名按宿主现有能力执行。
> `${CLAUDE_PLUGIN_ROOT}` 是本 SKILL.md 向上两级的插件根，不假定它在普通终端里存在。

## 美术项目接入（两个运行时共用）

项目包含美术资产时，先读取 `../../docs/art-assets.md`，盘点已有目录与注册表。用户授权接入时按实际资产建立 `design/art/assets.json`（空模板在 docs/templates/art-assets.json），保留旧注册表和定制目录，不移动引擎资产、不自动批准。只执行脚本 init/sync 不会自动创建资产登记；完成后明确报告是否接入及覆盖范围。

## Codex 分支（在 Claude 专属步骤之前执行）

当前宿主是 Codex 时，从已加载技能的真实插件路径运行：

```text
python <core-root>/scripts/harness.py init --project <project-root> --dry-run
python <core-root>/scripts/harness.py init --project <project-root>
python <core-root>/scripts/harness.py doctor --project <project-root>
```

UE 项目传当前启用的 `--unreal-root <unreal-pack-root>`；不要按缓存 mtime 选择版本。
需要 Blender 的项目另传 `--blender-root <blender-pack-root>`，按需安装建模和独立资产评审角色。
缺 `.claude/team.json` 时脚本**照常写完其余文件**并以 **exit 3** 打印 `NEEDS-ROSTER` 指引：
名册归服务器／管理员，本地不自注册。按指引取得后重跑 `doctor`；有文档仓时用
`python <core-root>/scripts/harness.py roster --project <project-root> --from <docs-repo-url>`
（之后可省略 `--from`，远端记在 `.codex/harness.json` 的 `roster.remote`）。
脚本保留已有配置及定制文件，输出 PRESERVE 项由本次任务范围决定是否手工合并。
`init/sync` 安装项目级 agents 和 AGENTS.md 入口，并在缺失时按已装 pack 写
`.claude/settings.json`（已存在不覆盖）；`sync-rules` 仅更新共享规则及同步记录。
技能／hook 版本需要从 Codex 插件界面更新；命令支持时使用 `codex plugin marketplace upgrade`
和 `codex plugin add <plugin>@XGameHarness`，检查实际 CLI help。变更 hooks 后用 `/hooks` 审阅信任。
完成后结束本分支，不执行以下 Claude 插件缓存更新、重启 Claude 等专属步骤。
（`.claude/settings.json` 不在此列：脚本已经写好，Claude 侧要装 harness 就必须有它。）

# /project-init — 新项目接入 XGameHarness

在**新项目根目录**运行。完成后重启 session，harness（skills / agents / hooks）
随 XGameHarness marketplace 加载。

> **别把「订阅了 marketplace」当成「永远是最新」。** 插件缓存按 commit SHA 钉版本，
> 实测存在订阅配置完全正确、插件却停在一个月前 commit 的情况。harness 有更新时在
> 项目里跑 `/harness-upgrade`，它会显式核对插件版本、按项目契约查缺、并同步 rules。

本 skill 建哪些文件，以 `${CLAUDE_PLUGIN_ROOT}/docs/project-contract.md` 的必需项
清单为准 —— 那份清单同时被 `/harness-upgrade` 消费，**新增项目侧必需文件时先改
那里**，否则老项目没有补上的路径。

## 执行步骤

### 1. 收集信息（缺什么问什么，AskUserQuestion）

- **项目名**（PascalCase，如 RichLethe）：优先用参数；否则默认当前目录名，向用户确认
- **是否 UE 项目**：决定 `enabledPlugins` 是否保留 `unreal-pack@XGameHarness`，
  以及同步哪些 rules

团队身份单独走第 2 步 —— 它是**唯一**会把真人信息落盘的环节，而且这份文件不由你生成。

### 2. 团队名册（`.claude/team.json` —— 拿到，不是生成）

**名册归服务器／管理员所有，本地不自注册。** 身份注册表决定 `resolve-identity.sh`
能否把 git 账号映射成 identity key；映射不上则全流程退化为 `unknown`（session-state /
session-logs / memo 全部写进 `team/*/unknown/`，多人协作时互相踩）。

历史上这一步是「按当前机器的 git 配置现场生成一条」，那正是缺陷的形状：`user.name`
换台机器就变（同一个人 `g4berolo` / `17717649805`），生成出来的名册看着成功，换机器
立刻解析成 `unknown`。**所以不要再用 git 配置替用户注册。**

**2.1 文件已存在（接了工作室服务器的项目，git pull 就有）**

读 `git config user.name` / `user.email`，与名册里的 `git_users` / `git_emails` 对一遍：

- 对得上 → 报出 identity key，进第 3 步
- **对不上 → 不要改这个文件**。告诉用户：把这台机器的 `user.name` 和 `user.email`
  给管理员，加进名册后 `git pull`（或跑 `harness.py roster`）。这是**唯一**正确出路；
  本地补一行会在下次下发时被覆盖，而且别人的机器仍然是坏的

**2.2 文件不存在**

问用户：这个项目**接不接工作室服务器**（AskUserQuestion）。

- **接** → 名册由管理员维护：单仓项目让管理员把 `.claude/team.json` 提交进本仓；
  拆了文档仓的项目跑
  `python <core-root>/scripts/harness.py roster --project . --from <docs-repo-url>`。
  取到之前**不要**编造一份占位，否则第一条历史就写在错的 identity 下
- **不接** → 只有这一支允许手写，按 2.3 做

**2.3 不接服务器时手写（唯一允许手写的分支）**

骨架用 `${CLAUDE_PLUGIN_ROOT}/project-template/.claude/team.json.template`（它是模板，
不要原样复制）。替换全部 `<...>` 占位，删掉 `_template` / `_privacy` 说明字段
（`_comment` 可留）。要问的四项：

| 要问的 | 说明 | 建议默认值 |
|---|---|---|
| identity key | 会成为目录名 `team/session-state/<key>/`。**只能用小写字母 / 数字 / 下划线 / 短横**，改名等于搬历史目录，先定好 | 从 `user.name` 推一个（转小写、非法字符换 `_`），让用户确认或改 |
| display_name | 给人看的名字，可用中文 | `git config user.name` 的原值 |
| role | `admin` / `developer` / `artist`。admin 可改 team 配置、可编辑他人 session-state（`validate-git.sh` 据此决定是否告警） | 单人项目 `admin`；多人项目发起人 `admin` |
| 邮箱怎么办 | 见下 | 问，不要猜 |

`git_users` 与 `git_emails` **两个字段都要填**：只填 `git_users`，换机器或改 git 配置
必断；邮箱是跨机器唯一稳定的那个键。

这份文件会进版本库。**若仓库是公开的（或将来可能公开）**，真实邮箱就是公开的，写进
历史后删不掉。明确告诉用户，给两个选项，**不要替他决定**（尤其涉及别人的邮箱时）：

1. 照写 —— 全体成员都同意公开自己的邮箱时才选
2. 把 `.claude/team.json` 加进项目 `.gitignore`，每人各维护一份本地副本 —— 邮箱完全
   不入库，代价是新成员要手动建

（旧版这里还有「`git_emails: []`，只靠 `git_users` 匹配」的第三个选项，**已废弃** ——
它就是本节开头那个缺陷的来源。）

有其他成员就每人重复上表（他们的 `user.name` / `user.email` 需要用户提供，你读不到）；
只有一人也没关系，后续加人直接编辑文件，不必重跑本 skill。

写入前把完整内容展示给用户确认。写完自检三条：合法 JSON、不含任何 `<` `>` 残留、
**每个 identity 的 `git_emails` 非空**（除非用户选了方案 2）。

### 3. 复制其余模板（源：`${CLAUDE_PLUGIN_ROOT}/project-template/`）

| 模板文件 | 目标 | 处理 |
|---|---|---|
| `.claude/settings.json` | 同路径 | 原样复制；非 UE 项目删掉 `"unreal-pack@XGameHarness"` 行。**Codex 分支已跑过 `harness.py` 的项目此文件已存在且 `enabledPlugins` 已按已装 pack 写好，核对即可，不要覆盖**（团队可能已改 permissions） |
| `.claude/harness-config.json` | 同路径 | 默认 `excludedAgents: []`；单人游戏可填 `["unreal-pack:ue-replication-specialist"]`，非 UE 项目无需填（hook 已按 enabledPlugins 自动跳过 unreal-pack agents）。**`syncedHarnessCommit` 必须替换成真实短 SHA**（取 `~/.claude/plugins/installed_plugins.json` 里本插件的 `gitCommitSha` 前 7 位），别留 `<harness short SHA>` 占位；同时删掉 `_syncedHarnessCommit` 说明字段 |
| `.gitignore` | 项目根 | 已有则合并两行（`.claude/state/`、`.claude/settings.local.json`），不覆盖。第 2.3 步若选了方案 2，再补一行 `.claude/team.json` |
| `CLAUDE.md` | 项目根 | 替换 `<ProjectName>` 占位；按项目类型填 Technology Stack 骨架 |

`.claude/team.json.template` **不复制** —— 第 2 步已经取得（或按 2.3 手写了）真实文件。

**已存在的文件一律先展示 diff 征求确认，不静默覆盖**（目标项目可能已有配置）。

### 4. 同步 rules

调用 `/sync-rules`（本插件 skill）把 core + unreal-pack（若启用）的 path-scoped
rules 实例化到 `.claude/rules/`，并按其报告提醒用户哪些 `paths:` 需要按本项目
目录结构调整。

### 5. 目录约定骨架（可选，问用户）

harness 项目契约目录按需 lazy 创建即可，但若用户愿意现在建好（`{identity}` 用
第 2 步解析出的 identity key，多人则每人各一份，`.gitkeep` 放最底层目录）：

```
design/gdd/
design/digest/         ← 读本，跟 GDD 同名一一对应（2026-09-14 从 GDD 里搬出来的）
plan/
plan/stage.md          ← 必建，拷模板（见下）
team/session-state/{identity}/
team/session-logs/{identity}/
team/memo/{identity}/open/
team/memo/{identity}/closed/
docs/architecture/
```

memo 必须是 `team/memo/{recipient}/{open,closed}/` 两层 —— 平铺一层 `team/memo/` 不符合
CLAUDE.md 契约，`/start` 的 `team/memo/{identity}/open/*.md` 会扫不到任何东西。

**`plan/stage.md` 不是可选项**，即使用户跳过其余目录也要建：拷
`${CLAUDE_PLUGIN_ROOT}/docs/templates/stage.md` 到 `plan/stage.md`，frontmatter 的
`current_stage` 保持 `Concept`，History 首行填今天日期。它是 `/gate-check`、
`/project-stage-detect`、`/start`、`/how-to-do` 四个消费方的唯一真相源；缺了它它们
只能退化到启发式猜测。提醒用户：模板只给了 sub-phase 的**种类**，「本项目含义」
列需要他们自己填（可以晚点填，但跑第一道 gate 前要填完）。

### 6. 仓库怎么摆（**接工作室服务器的项目才有这一步**）

前面五步建的全是**本地文件**。到这儿要回答的是另一个问题：
**这些东西放在哪个仓里、服务器上要配什么。**
不交代的话，新项目的发起人手上有一堆文件却不知道往哪儿推。

**先问一句：这个项目接不接工作室服务器（XGameHarnessUI 那台）？**

- **不接** —— 到此为止。一个仓、一次 `git init`，前面建的东西全在那个仓里。
  **这是完全正常的用法，不是简化版。** 直接走第 7 步。
- **接** —— 照 `${CLAUDE_PLUGIN_ROOT}/docs/repo-and-deploy.md` 走。要点：

  | | 装什么 |
  |---|---|
  | **游戏工程仓** | `client/ art/ tools/ docs/ .claude/ CLAUDE.md …`，**不含** `plan/ design/ team/` |
  | **文档仓** | 只有 `plan/ design/ team/` + `.claude/team.json`，**只有服务器和管理员写** |

  拆的理由：策划在客户端里改一个任务状态是**服务器代为提交**的，
  那些提交不该落在游戏工程仓的历史里。
  客户端那边**看不见这件事** —— 所有人一样 `git clone` 游戏工程仓，
  那三个目录由客户端从服务器取回来放到同一个位置。

  ⚠ **顺序不许颠倒**（那份文档第三节）：先建仓 → `/project-init` → 首次提交
  （**这时候那三个目录还在游戏工程仓里，是对的**）→ 建文档仓 → 配服务器 →
  **验一次下发真的通** → **最后**才从游戏工程仓里去掉那三个目录。
  反过来做的话，那段时间里谁都拿不到它们。

  ⚠ **这一步本 skill 不替用户执行任何 git 或服务器操作** —— 它跨两个仓、
  要令牌、还会动全队的工作区。把要点和那份文档指给用户，由他自己做。

### 7. 收尾清单（输出给用户）

- [ ] `git init`（若尚未）+ 首次提交（须用户明确要求才执行）
- [ ] **接服务器的项目**：仓库怎么摆、服务器上配什么 ——
      `${CLAUDE_PLUGIN_ROOT}/docs/repo-and-deploy.md` 末尾那份检查单逐条过。
      ⚠ 里面有一条是**动全队工作区**的（从游戏工程仓去掉那三个目录），
      **验过下发真的通之后才做**
- [ ] 确认 `.gitignore` 含 `.claude/state/`、`.claude/settings.local.json`（模板已带）
- [ ] 确认 `plan/stage.md` 已生成，`current_stage: Concept`
- [ ] 确认 `.claude/team.json` 是合法 JSON 且无 `<...>` 残留（跑一次 `/start`
      看 Developer 是否解析成 identity key 而不是 `unknown`）
- [ ] **仓库若公开**：确认 `team.json` 里的邮箱都经过本人同意。已经提交过再删是没用的
      —— 历史里删不掉，只能重写历史 + force push
- [ ] 重启 Claude Code session → 信任目录 → 按提示安装 XGameHarness marketplace
- [ ] 每台新机器一次性：`gh auth setup-git` + 环境变量
      `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1`（私有仓库自动更新）
- [ ] UE 项目：跑 `/setup-engine` 钉引擎版本并生成 engine-reference 文档
- [ ] 跑 `/start` 验证 dashboard；查 `/handbook` 了解全部能力
- [ ] 记住：**harness 有更新时回来跑 `/harness-upgrade`**（插件本体不保证自动更新，
      且 harness 后续新增的项目侧必需文件不会自己出现）

## 注意

- 本 skill 不执行 git 提交/推送（遵循协作协议：No commits without user instruction）
- 模板里的 permissions 是团队基线，项目可自行增删
