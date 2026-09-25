---
name: sync-rules
description: "同步 XGameHarness 各 pack 内置的 path-scoped rules 到当前项目 .claude/rules/。managed-by 标记的文件跟随插件更新；项目定制过的（已去除标记）不覆盖。新项目接入和 harness rules 更新后运行。"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion
---

参数：[--dry-run]


> **运行时适配**：先按需读取本插件 [`docs/codex-runtime.md`](../../docs/codex-runtime.md)。
> Codex 用 `$技能名` 或读取 SKILL.md；共享流程中的 Claude 工具名按宿主现有能力执行。
> `${CLAUDE_PLUGIN_ROOT}` 是本 SKILL.md 向上两级的插件根，不假定它在普通终端里存在。

## Codex 分支（在 Claude 专属步骤之前执行）

当前宿主是 Codex 时，从已加载技能的真实插件路径运行：

```text
python <core-root>/scripts/harness.py sync-rules --project <project-root> --dry-run
python <core-root>/scripts/harness.py sync-rules --project <project-root>
python <core-root>/scripts/harness.py doctor --project <project-root>
```

UE 项目传当前启用的 `--unreal-root <unreal-pack-root>`；不要按缓存 mtime 选择版本。
`sync-rules` 不检查身份表（它只碰 `.claude/rules/`）；名册归服务器／管理员下发，本地不自注册。
脚本保留已有配置及定制文件，输出 PRESERVE 项由本次任务范围决定是否手工合并。
`init/sync` 安装项目级 agents 和 AGENTS.md 入口，并在缺失时按已装 pack 写
`.claude/settings.json`；`sync-rules` 仅更新共享规则及同步记录。
技能／hook 版本需要从 Codex 插件界面更新；命令支持时使用 `codex plugin marketplace upgrade`
和 `codex plugin add <plugin>@XGameHarness`，检查实际 CLI help。变更 hooks 后用 `/hooks` 审阅信任。
完成后结束本分支，不执行以下 Claude 插件缓存更新、重启 Claude 等专属步骤。

# /sync-rules — pack rules 同步到项目

path-scoped rules 必须存放在项目 `.claude/rules/` 才能被注入 hook 读取，且 `paths:`
glob 需按项目目录结构定制（例：RichLethe 把 test-standards 的 path 从 `tests/**`
改为 `client/Source/clientTests/**`）。因此 rules 以「pack 分发源 + 项目实例」双层
管理，本 skill 负责两层间同步。

## 同步协议

每个源 rule 文件 frontmatter 带 `managed-by: XGameHarness/<pack>` 标记：

| 项目侧状态 | 动作 |
|---|---|
| `.claude/rules/<name>.md` 不存在 | 复制（保留 managed-by 标记）|
| 存在且仍含 `managed-by` 标记 | 内容与源不同 → 用源覆盖（跟随插件更新）|
| 存在但**无** `managed-by` 标记 | **跳过**（项目已定制）；若源有更新，报告 diff 摘要供手动合并 |

**项目定制方式**：改完 `paths:` 或规则内容后，**删除 frontmatter 里的
`managed-by` 行**，即固定为项目版本，后续同步不再覆盖。

## 执行步骤

1. **定位 rules 源**（两处）：
   - core：`${CLAUDE_PLUGIN_ROOT}/rules/*.md`
   - unreal-pack：Glob `${CLAUDE_PLUGIN_ROOT}/../../unreal-pack/*/rules/*.md`
     （**不要写 `~/...`** —— Glob 不展开 `~`，写了永远零命中。
     缓存按 commit SHA 分版本目录；Glob 结果按修改时间排序，取最新版本目录那组。
     非 UE 项目未装 unreal-pack 时此步为空，跳过即可）
2. **逐文件按上表对比**项目 `.claude/rules/`。若用户传了 `--dry-run`，只报告不写入。
3. **写入后自检**：新复制的 rule 的 `paths:` glob 是否在本项目命中任何现存目录
   （Glob 验证）。不命中的列为「占位规则」提醒用户：等对应目录首次出现自动生效，
   或按项目结构改 `paths:`（改后记得删 managed-by 标记）。
4. **输出同步报告**：新增 / 已更新 / 跳过（定制）/ 占位 四类清单；若有「定制版落后
   于源」的文件，附三行以内的 diff 要点。
5. 提醒：项目有 `.claude/docs/rules-reference.md` 索引的（如 RichLethe），新增 rule
   后在该索引补一行。

## 注意

- 本 skill 只动 `.claude/rules/`，不碰其他项目文件。
- 写入前对每个将被覆盖的文件展示变更摘要（遵循项目协作协议）。
