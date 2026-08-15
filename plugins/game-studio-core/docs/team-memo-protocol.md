# Team Memo Protocol

跨开发者轻量异步协作机制。Memo = 便条；sender 写给 recipient，recipient 在下次 session start 由 `/start` skill 自动 surface。

## 路径结构

```
team/memo/
├── {recipient}/
│   ├── open/     <- /start 扫这里；未处理的 memo
│   └── closed/   <- recipient 处理完 mv 进来；本地审计
```

身份按 `.claude/team.json` 解析 git config user.name。

## Memo 文件命名

`{YYYY-MM-DD}-{kebab-case-topic}.md`

例：`2026-05-21-gdd-layered-scene-line-207-typo.md`

## Memo 文件 schema

```markdown
---
from: zhouxinyu
to: fro
date: 2026-05-21
priority: low | medium | high
related: ADR-0005, design/gdd/layered-scene-switching.md
---

# {一行标题}

{背景 / 问题描述}

## 完成条件

- [ ] xxx
- [ ] yyy

## 引用

- file:line
- 其他 memo / commit reference
```

字段说明：

- `from` / `to`: identity（必填，与 `.claude/team.json` 注册一致）
- `date`: 写入日期 ISO-8601
- `priority`: 优先级（必填）— low / medium / high
- `related`: 关联 artifact 路径或系统编号（可选，强烈建议）

## 工作流

### 发送

1. Sender 写 `team/memo/{recipient}/open/{date}-{topic}.md`
2. Commit（可与其他工作合并 commit，不强求独立）

### 接收

1. Recipient 启动 session → `/start` 自动扫 `team/memo/{recipient}/open/` 并 dashboard 显示 `📬 待处理 memo (N 条)` + 首行预览
2. Recipient 决定本 session 是否处理；不处理则保留 open，下次再 surface
3. Recipient 处理完 → `git mv team/memo/{recipient}/open/{file}.md team/memo/{recipient}/closed/{file}.md` + commit "close memo: {topic}"

### 撤回

Sender 撤回未处理 memo → `git rm team/memo/{recipient}/open/{file}.md` + commit "cancel memo: {topic}"

### 本地审计

```bash
ls team/memo/{identity}/closed/      # 本地查历史，无需联网
git log -- team/memo/                # 全 memo 历史
```

## 边界

**不适用场景**:

- Sprint task 分配 → `plan/sprints/sprint-XXX.md`
- 里程碑级 handoff → `team/handoff/HANDOFF.md`
- 即时讨论 → IM 工具
- 给自己留备忘 → `team/session-state/{identity}/active.md` 或 personal memory files

**适用场景**:

- 跨开发者 typo / bug flag（如 "GDD line 207 措辞 fix"）
- 跨开发者问题 / 决策征询
- 跨开发者轻量 task ping
- 单条对话能完结的事项

## /start 行为

详 `${CLAUDE_PLUGIN_ROOT}/skills/start/SKILL.md`（随插件分发，项目侧无 .claude/skills/）。

简版：

- 步骤 1（silent detect）glob `team/memo/{identity}/open/*.md`（忽略 `.gitkeep`）列出
- 步骤 2（dashboard）若 N > 0 → 加段 `📬 待处理 memo (N 条)` + 每条 `from` + 一行标题预览
- 用户可选 "处理 memo" 路由直接开始处理

## 修订

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-21 | 初稿 | P26 zhouxinyu/fro 跨开发者 ping gap 触发 |
