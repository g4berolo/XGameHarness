---
name: project-init
description: "新项目接入 XGameHarness：问询生成团队身份注册表 team.json、复制项目模板（settings.json / harness-config.json / CLAUDE.md / .gitignore）、填充项目名、同步 path-scoped rules、初始化目录约定。在新项目根目录（空目录或已有代码）运行一次即可。"
argument-hint: "[项目名]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Skill
---

# /project-init — 新项目接入 XGameHarness

在**新项目根目录**运行。完成后重启 session，harness（skills / agents / hooks）
即随 XGameHarness marketplace 自动加载并持续更新。

## 执行步骤

### 1. 收集信息（缺什么问什么，AskUserQuestion）

- **项目名**（PascalCase，如 RichLethe）：优先用参数；否则默认当前目录名，向用户确认
- **是否 UE 项目**：决定 `enabledPlugins` 是否保留 `unreal-pack@XGameHarness`，
  以及同步哪些 rules

团队身份单独走第 2 步 —— 那一步要问的东西多，且是**唯一**会把真人信息落盘的环节。

### 2. 团队初始化（生成 `.claude/team.json`）

harness 仓库里**没有**可用的 `team.json`，只有
`${CLAUDE_PLUGIN_ROOT}/project-template/.claude/team.json.template`。它是模板，
**不要原样复制** —— 本步骤按问询结果在项目本地现场生成真实文件。

身份注册表决定 `resolve-identity.sh` 能否把 git 账号映射成 identity key；映射不上
则全流程退化为 `unknown`（session-state / session-logs / memo 全部写进
`team/*/unknown/`，多人协作时会互相踩）。

**2.1 先读，不要问**

```bash
git config user.name
git config user.email
```

读不到（新机器没配过）就提示用户先跑 `git config --global user.name/user.email`，
本步骤挂起等待 —— 拿不到 git 身份，生成出来的 team.json 必然匹配不上。

**2.2 问当前用户这几项（AskUserQuestion，一次问完）**

| 要问的 | 说明 | 建议默认值 |
|---|---|---|
| identity key | 会成为目录名 `team/session-state/<key>/`。**只能用小写字母 / 数字 / 下划线**，定了之后改名等于搬历史目录，先定好 | 从 `user.name` 推一个（转小写、非法字符换 `_`），让用户确认或改 |
| display_name | 给人看的名字，可用中文 | `git config user.name` 的原值 |
| role | `admin` / `developer` / `artist`。admin 可改 team 配置、可编辑他人 session-state（`validate-git.sh` 据此决定是否告警） | 单人项目 `admin`；多人项目发起人 `admin` |
| 是否公开仓库 | 决定 `git_emails` 要不要写真值，见 2.4 | 问，不要猜 |

**2.3 再问是否登记其他成员**

有就对每人重复 2.2 的四项（他们的 `user.name` / `user.email` 需要用户提供，你读不到）。
没有就只写一条 —— 后续加人直接编辑 `.claude/team.json` 即可，不必重跑本 skill。

**2.4 邮箱与公开仓库**

生成的 `team.json` 会进项目的版本库。**若项目仓库是公开的（或将来可能公开）**，
真实邮箱就是公开的，而且写进历史后删不掉。明确告诉用户这一点，给三个选项：

1. 照写 —— 全体成员都同意公开自己的邮箱时才选
2. `git_emails: []` —— 只靠 `git_users` 匹配。绝大多数情况够用，是公开仓库的推荐值
3. 把 `.claude/team.json` 加进项目 `.gitignore` —— 每人各自维护一份本地副本，
   邮箱完全不入库；代价是新成员要手动建

**不要替用户做这个决定**，尤其涉及别人的邮箱时。

**2.5 写文件**

以模板为骨架，替换全部 `<...>` 占位，**并删掉 `_template` / `_privacy` 两个说明字段**
（`_comment` 可留，对后来维护的人有用）。写入前把完整内容展示给用户确认。
写完自检：文件是合法 JSON，且不含任何 `<` `>` 残留。

### 3. 复制其余模板（源：`${CLAUDE_PLUGIN_ROOT}/project-template/`）

| 模板文件 | 目标 | 处理 |
|---|---|---|
| `.claude/settings.json` | 同路径 | 原样复制；非 UE 项目删掉 `"unreal-pack@XGameHarness"` 行 |
| `.claude/harness-config.json` | 同路径 | 默认 `excludedAgents: []`；单人游戏可填 `["unreal-pack:ue-replication-specialist"]`，非 UE 项目无需填（hook 已按 enabledPlugins 自动跳过 unreal-pack agents）|
| `.gitignore` | 项目根 | 已有则合并两行（`.claude/state/`、`.claude/settings.local.json`），不覆盖。第 2.4 步若选了方案 3，再补一行 `.claude/team.json` |
| `CLAUDE.md` | 项目根 | 替换 `<ProjectName>` 占位；按项目类型填 Technology Stack 骨架 |

`.claude/team.json.template` **不复制** —— 第 2 步已经生成了真实文件。

**已存在的文件一律先展示 diff 征求确认，不静默覆盖**（目标项目可能已有配置）。

### 4. 同步 rules

调用 `/sync-rules`（本插件 skill）把 core + unreal-pack（若启用）的 path-scoped
rules 实例化到 `.claude/rules/`，并按其报告提醒用户哪些 `paths:` 需要按本项目
目录结构调整。

### 5. 目录约定骨架（可选，问用户）

harness 项目契约目录按需 lazy 创建即可，但若用户愿意现在建好（`{identity}` 用
第 2 步定下的 identity key，多人则每人各一份，`.gitkeep` 放最底层目录）：

```
design/gdd/
plan/
team/session-state/{identity}/
team/session-logs/{identity}/
team/memo/{identity}/open/
team/memo/{identity}/closed/
docs/architecture/
```

memo 必须是 `team/memo/{recipient}/{open,closed}/` 两层 —— 平铺一层 `team/memo/` 不符合
CLAUDE.md 契约，`/start` 的 `team/memo/{identity}/open/*.md` 会扫不到任何东西。

### 6. 收尾清单（输出给用户）

- [ ] `git init`（若尚未）+ 首次提交（须用户明确要求才执行）
- [ ] 确认 `.gitignore` 含 `.claude/state/`、`.claude/settings.local.json`（模板已带）
- [ ] 确认 `.claude/team.json` 是合法 JSON 且无 `<...>` 残留（跑一次 `/start`
      看 Developer 是否解析成 identity key 而不是 `unknown`）
- [ ] **仓库若公开**：确认 `team.json` 里的邮箱都经过本人同意。已经提交过再删是没用的
      —— 历史里删不掉，只能重写历史 + force push
- [ ] 重启 Claude Code session → 信任目录 → 按提示安装 XGameHarness marketplace
- [ ] 每台新机器一次性：`gh auth setup-git` + 环境变量
      `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1`（私有仓库自动更新）
- [ ] UE 项目：跑 `/setup-engine` 钉引擎版本并生成 engine-reference 文档
- [ ] 跑 `/start` 验证 dashboard；查 `/handbook` 了解全部能力

## 注意

- 本 skill 不执行 git 提交/推送（遵循协作协议：No commits without user instruction）
- 模板里的 permissions 是团队基线，项目可自行增删
