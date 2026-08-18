# 项目契约 —— 一个「当前版本」的项目该有什么

本文件是**唯一真相源**，回答一个问题：一个接入了 XGameHarness 的项目，在当前
harness 版本下必须有哪些文件和目录。

两个消费方：

- `/project-init` —— 新项目按此清单建全
- `/harness-upgrade` —— 老项目按此清单查缺，补上 harness 后来新增的东西

**改动 harness 时新增了任何项目侧必需文件，必须同时在这里加一行**，否则老项目
永远不会知道它的存在。这条规则的存在本身就是因为踩过：`plan/stage.md` 在
2026-08-17 成为必需项，而所有已接入项目都没有补上的路径。

---

## 分发方式：三档

理解这三档，才能理解为什么需要 `/harness-upgrade`。

| 档 | 内容 | 怎么更新 |
|---|---|---|
| **A. 插件本体** | skills / agents / hooks / docs / templates | `claude plugin marketplace update XGameHarness` + `claude plugin update <plugin>@XGameHarness` + **重启**。缓存按 commit SHA 分目录钉版本，**不要假设它会自己更新** |
| **B. rules 实例** | `.claude/rules/*.md` | `/sync-rules`（带 `managed-by` 标记的跟随更新，删了标记的固定为项目版） |
| **C. 项目文件** | 下面的清单 | `/harness-upgrade`（本文件驱动） |

A 档是插件缓存，B / C 档是项目仓库里的真实文件。**C 档没有任何自动机制** —— 这
正是本文件存在的理由。

---

## 必需项清单

`{identity}` = `.claude/team.json` 里的 identity key。多人项目每人一份。

| # | 路径 | 来源 | 缺了会怎样 | 引入版本 |
|---|---|---|---|---|
| 1 | `.claude/team.json` | 由 `/project-init` 第 2 步**问询生成**（模板是 `project-template/.claude/team.json.template`，不可直接复制） | `resolve-identity.sh` 映射不上 git 账号，全流程退化成 `unknown`，多人协作互相踩目录 | 初始 |
| 2 | `.claude/settings.json` | `project-template/.claude/settings.json` | 插件市场订阅和 `enabledPlugins` 缺失，harness 整个不加载 | 初始 |
| 3 | `.claude/harness-config.json` | `project-template/.claude/harness-config.json` | `suggest-subagent` 钩子无法读 `excludedAgents`；`syncedHarnessCommit` 水位丢失 | 初始 |
| 4 | `.claude/rules/*.md` | `/sync-rules` | path-scoped 规则不注入 | 初始 |
| 5 | `CLAUDE.md` | `project-template/CLAUDE.md` | 项目上下文、协作协议、语言规则缺失 | 初始 |
| 6 | `.gitignore` 含 `.claude/state/` 与 `.claude/settings.local.json` | `project-template/.gitignore` | 钩子运行时状态和本机私有配置被提交 | 初始 |
| 7 | **`plan/stage.md`** | `docs/templates/stage.md` | `/gate-check`、`/project-stage-detect`、`/start`、`/how-to-do` 四个消费方失去阶段真相源，只能退化为启发式猜测 | **2026-08-17** |
| 8 | `design/gdd/` | 目录 | GDD 类 skill 无处落盘 | 初始 |
| 9 | `plan/` | 目录 | sprint / milestone 无处落盘 | 初始 |
| 10 | `docs/architecture/` | 目录 | ADR 无处落盘 | 初始 |
| 11 | `team/session-state/{identity}/` | 目录 | 会话状态恢复失效 | 初始 |
| 12 | `team/session-logs/{identity}/` | 目录 | `session-stop` / `pre-compact` 钩子无处写 | 初始 |
| 13 | `team/memo/{identity}/open/` 与 `closed/` | 目录（**必须两层**） | `/start` 扫不到任何 memo。平铺一层 `team/memo/` 不符合契约 | 初始 |

### 可选项（按项目类型）

| 路径 | 条件 | 来源 |
|---|---|---|
| `docs/engine-reference/unreal/` | UE 项目 | `/setup-engine` |
| `.claude/docs/technical-preferences.md` | 定过技术偏好的项目 | `docs/templates/technical-preferences.md`，`/setup-engine` 首建 |
| `team/memo/harness/{open,closed}/` | 把本项目当 harness 试验田时 | 目录。用来收「harness 该改什么」的反馈，`/start` 会自动浮出 |

---

## 同步水位

`.claude/harness-config.json` 里的 `syncedHarnessCommit` 记录**上一次 C 档项目文件
同步到的 harness commit**。

```json
{
  "excludedAgents": [],
  "syncedHarnessCommit": "4a6c3f0"
}
```

- `/project-init` 写入初始值
- `/harness-upgrade` 读它决定要看哪一段区间的变化，完成后写回
- 字段缺失 = 该项目早于本机制（2026-08-18 之前接入），按「全量核对本清单」处理

**它只描述 C 档。** A 档插件版本以
`~/.claude/plugins/installed_plugins.json` 里的 `gitCommitSha` 为准，B 档 rules 以
文件内容比对为准 —— 三档各有各的判据，不要用一个水位号去代表另外两档。
