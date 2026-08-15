---
name: sync-rules
description: "同步 XGameHarness 各 pack 内置的 path-scoped rules 到当前项目 .claude/rules/。managed-by 标记的文件跟随插件更新；项目定制过的（已去除标记）不覆盖。新项目接入和 harness rules 更新后运行。"
argument-hint: "[--dry-run]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion
---

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
