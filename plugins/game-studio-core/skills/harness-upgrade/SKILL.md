---
name: harness-upgrade
description: "把一个已接入 XGameHarness 的老项目升级到当前 harness 版本：检查插件缓存是否过期、按项目契约查缺补漏、同步 rules、写回同步水位。harness 更新后在每个项目跑一次。触发词：harness 升级/更新 harness/项目落后了/插件是不是旧的/缺 stage.md"
argument-hint: "[--dry-run]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Skill
---

# /harness-upgrade — 老项目追上当前 harness

`/project-init` 管新项目接入，`/sync-rules` 只管 `.claude/rules/`。**两者之间有个
洞**：harness 后来新增的项目侧必需文件（例如 `plan/stage.md`），已接入的项目没有
任何机制知道它的存在。本 skill 补这个洞。

先读 `${CLAUDE_PLUGIN_ROOT}/docs/project-contract.md` —— 它是必需项清单的唯一
真相源，本 skill 不自带清单副本。

`--dry-run` 只报告不写入。

---

## 0. 判断这是不是一个已接入的项目

Glob `.claude/settings.json`。不存在 → 这不是升级场景：

> 本项目还没接入 XGameHarness（找不到 `.claude/settings.json`）。
> 要接入请跑 `/project-init`，不是本 skill。

存在则继续。

---

## 1. 先查 A 档：插件本体是否过期

**这一步必须在最前面。** 插件缓存按 commit SHA 钉版本，如果它落后了，你后面读到的
`project-contract.md`、各 skill、各模板**全是旧的** —— 拿旧清单去核对项目，结论必然
是错的。

**不要假设插件会自动更新。** 实测过一个案例：项目侧订阅配置完全正确，插件仍停在
一个月前的 commit。无论自动更新机制是否存在，都要显式核对。

读本机安装记录：

```bash
cat ~/.claude/plugins/installed_plugins.json
```

取 `game-studio-core@XGameHarness`（以及启用了的 `unreal-pack@XGameHarness`）的
`gitCommitSha` 与 `lastUpdated`。

再取 marketplace 本地克隆的最新提交：

```bash
git -C ~/.claude/plugins/marketplaces/XGameHarness fetch --quiet
git -C ~/.claude/plugins/marketplaces/XGameHarness log --oneline -1 origin/main
```

`fetch` 失败（离线 / 私有仓库无凭据）就跳过比对，如实告诉用户「无法确认插件是否
最新」，**不要**沉默地当作已是最新。

**若已安装的 SHA ≠ 远端最新**，输出并**停在这里**：

> 插件落后了：已安装 `<sha>`（<lastUpdated>），远端最新 `<sha>`。
>
> 请先更新再继续 —— 现在往下走，我读到的模板和清单都是旧版本：
>
> ```
> claude plugin marketplace update XGameHarness
> claude plugin update game-studio-core@XGameHarness
> claude plugin update unreal-pack@XGameHarness      # 仅 UE 项目
> ```
>
> 然后**重启 Claude Code**（更新需要重启才生效），再跑一次 `/harness-upgrade`。

本 skill 不代跑这三条命令：它们改的是**本机全局**插件安装，而且必须重启才生效，
跑完当前会话里的一切仍是旧版本，容易造成「以为升级了」的假象。

---

## 2. 读同步水位

读 `.claude/harness-config.json` 的 `syncedHarnessCommit`：

- **有值** → 报告「上次同步到 `<sha>`，现在是 `<sha>`」
- **无该字段** → 本项目早于水位机制，按**全量核对**处理，并在报告里说明

水位只描述 C 档项目文件。A 档看第 1 步，B 档看第 4 步，三档各有判据。

---

## 3. 按契约查缺（C 档）

逐条核对 `project-contract.md` 的必需项清单。对每一项：

- **存在** → 记为 OK，不动它
- **缺失** → 进待补清单，记下「缺了会怎样」那一列的后果

分两类处理，因为风险完全不同：

### 3a. 纯新增（项目里根本没有）

`plan/stage.md`、各契约目录属于这类。没有覆盖风险，可以一次性列出来批量确认：

> 缺以下 N 项，都是新增、不会覆盖你现有的任何文件：
> - `plan/stage.md` —— 缺了 `/gate-check` 等四个 skill 失去阶段真相源
> - `team/memo/zhouxinyu/open/` —— 缺了 `/start` 扫不到 memo
>
> 全部补上？

`plan/stage.md` 要特别说明：拷 `${CLAUDE_PLUGIN_ROOT}/docs/templates/stage.md`，
`current_stage` 按项目**实际**阶段填（不要一律写 `Concept` —— 老项目可能已经在
Production 了，问用户），History 首行填今天日期。并提醒模板只给了 sub-phase 的
**种类**，「本项目含义」列需要用户自己填。

### 3b. 模板已更新（项目里有，但和当前模板不一致）

`CLAUDE.md`、`.claude/settings.json`、`.claude/harness-config.json`、`.gitignore`
属于这类。**这些文件项目几乎一定改过**（权限白名单、技术栈、编码标准都写在里面）。

**逐个文件单独确认，永远不要批量覆盖。** 对每个差异：

1. 展示三行以内的差异要点：模板新增了什么、项目侧改了什么
2. 给三个选项：**合并模板的新增部分** / **保持项目现状** / **看完整 diff 再决定**
3. 默认倾向「保持项目现状」—— 项目的定制通常是有理由的，而模板的更新往往只是
   基线调整

`.gitignore` 是唯一可以放心自动合并的：它是行集合，追加缺失行不会破坏已有内容。

---

## 4. 同步 rules（B 档）

调用 `/sync-rules`（Skill tool）。它自带三态逻辑（新增 / 跟随更新 / 定制版跳过），
不要在本 skill 里重复实现。

把它的报告原样并入本 skill 的最终报告 —— 尤其是「定制版落后于源」那一类，用户
需要知道哪些规则因为定制过而停止了跟随。

---

## 5. 写回水位

C 档处理完（含用户选择「保持现状」的项）后，把 `.claude/harness-config.json` 的
`syncedHarnessCommit` 更新为第 1 步取到的远端最新短 SHA。

`--dry-run` 时不写。

**用户中途放弃了某些项也照样写回** —— 水位记录的是「核对到哪个版本」，不是「全部
应用了」。放弃的项写进报告，不要靠水位倒退来提醒（否则每次升级都会重复问同样的
问题，用户会开始无脑跳过）。

---

## 6. 报告

```
## harness 升级报告：<项目名>

### A 档 插件本体
已安装 <sha>（<date>）｜远端 <sha> → [最新 / 需更新，见上文命令]

### B 档 rules
新增 N ｜ 已更新 N ｜ 跳过（项目定制）N ｜ 占位 N
[定制版落后于源的清单]

### C 档 项目文件
补上：<清单>
保持现状：<清单，附用户的理由>
仍缺失：<清单，附后果>

### 水位
<旧 sha> → <新 sha>

### 下一步
[按实际情况给，例如「填 plan/stage.md 的『本项目含义』列」「跑 /start 验证身份解析」]
```

---

## 注意

- 本 skill **不执行 git 提交/推送**（协作协议：No commits without user instruction）
- 本 skill **不代跑插件更新命令**（第 1 步已说明理由）
- 只动项目文件，不动 harness 仓库。想改 harness 本身请到 harness 仓库单独开会话 ——
  在项目上下文里改 harness，容易把本项目的假设当成通用需求写进去
