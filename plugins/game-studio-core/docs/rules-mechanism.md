# Path-Scoped Rules Mechanism

本机制在编辑指定 path 的文件时自动向 agent 注入对应规则。基于 Claude Code hooks 实现，**非官方 API**（属 RichLethe 自定义 convention）。

---

## 工作原理

### 两路注入

| 时机 | Hook | 行为 |
|---|---|---|
| **Session 启动** | `.claude/hooks/session-start.sh` 末尾段 | 全量加载 `.claude/rules/*.md` 完整内容到 SessionStart context，**首次编辑也有规则可遵守** |
| **每次 Edit / Write / MultiEdit 后** | `.claude/hooks/inject-rules.py`（PostToolUse） | 解析 frontmatter `paths:` glob，命中目标文件则注入对应 rule 到 `additionalContext` |

PostToolUse 是 Claude Code 官方仅支持 `additionalContext` 注入的 hook 事件（PreToolUse 不支持），所以注入是**事后的**。SessionStart 路径补充"首次编辑前空窗"。

### Session marker 防重复

每个 session × 每条 rule 只 PostToolUse 注入一次。marker 文件：

```
.claude/state/rules-injected/{session_id}/{rule_name}
```

二次 Edit 同一 path → marker 已存在 → skip 注入。这控制 token 浪费，但仍保证规则在首次 Edit 时已生效。

`.claude/state/` 已加入 `.gitignore`。

---

## Rule 文件 schema

`.claude/rules/{rule-name}.md`：

```markdown
---
paths:
  - "design/gdd/**"
  - "design/_drafts/**"
---

# {Rule Title}

- 规则 1
- 规则 2
- ...
```

### Frontmatter

| 字段 | 必填 | 说明 |
|---|---|---|
| `paths` | 必填 | YAML 列表 of POSIX glob patterns（仓库相对路径） |

### Glob 语法

| Pattern | 含义 | 示例匹配 |
|---|---|---|
| `foo/**` | foo 目录及任意深度子内容 | `foo/a.md`, `foo/x/y.md` |
| `foo/*.md` | foo 一级 `.md` 文件 | `foo/a.md`（不含 `foo/x/a.md`） |
| `**/foo.md` | 任意位置的 `foo.md` | `a/foo.md`, `b/c/foo.md` |
| `*.md` | 仓库根 `.md` 文件 | `README.md`（不含 `src/x.md`） |

由 `inject-rules.py` 内置 regex 转换实现（不依赖系统 glob）；语义参照 gitignore-style，**Windows 路径自动规范化**为 POSIX 比较。

---

## 加新 rule 的步骤

1. **写规则文件** — `.claude/rules/{name}.md`，含 frontmatter `paths:`
2. **确认目标目录存在** — 若 `paths` 指向不存在目录，hook 不会出错但永远不触发
3. **下一个 session 自动生效** — 无需修改 hooks 或 settings.json
4. **可选：在受影响 GDD/doc 加 prose cite**，方便人类 reviewer 追溯规则来源

### 删除 rule

直接 `git rm .claude/rules/{name}.md`。已注入过的 session 中残留的 marker 文件可不清理（无害）。

---

## 当前 active rules + 历史

完整索引（含 active / 已删 / 不引入原因）见 [rules-reference.md](rules-reference.md)。

---

## 调试

### 端到端测试

新开 session → 观察启动输出应含 `=== Path-Scoped Rules ===` 段。`Edit design/gdd/permadeath.md` 后观察 tool result 应含 `additionalContext` 段。`Edit client/Source/Foo.cpp` 应无注入。

### 日志

`.claude/state/inject-rules.log` 记录每次 hook 决策（命中 / skip / 异常）。

### Debug 模式

`claude --debug` 显示 hook stdout JSON。

### Marker 清理

如要强制重新注入（用于测试）：删除 `.claude/state/rules-injected/{session_id}/` 即可。

---

## 局限与权衡

| 局限 | 接受理由 / 缓解 |
|---|---|
| **PostToolUse 是事后注入** | SessionStart 全量加载兜底；RichLethe incremental 写 GDD 工作流，首次注入后后续 section 已合规 |
| **Python 依赖** | RichLethe `tools/` 已有 Python 脚本；只这 1 个 hook 用 Python，其他 hook 保持 bash |
| **frontmatter 协议是自定义 convention** | 非 Claude Code 官方 API，未来若有更优官方机制可弃用本 hook |
| **SessionStart 全量加载占 token** | 当前 1 个 active rule (~500 token) 可接受；若未来超 1500 token 考虑按 git status / session-state 启发式选择性加载 |
| **重复加载（SessionStart + 首次 PostToolUse）** | 接受 — "兜底 + 强化"代价低 |
| **Hook 失败不阻断 Edit** | 异常 silent exit 0；timeout 8s 兜底；查 `.claude/state/inject-rules.log` 排查 |

---

## 历史背景

RichLethe 从上游模板 [`Claude-Code-Game-Studios`](https://github.com/) fork 来。上游 `.claude/rules/` 含 11 个文件 + frontmatter `paths:`，但**模板的 `rules-reference.md` 错误声称"automatically enforced when editing files in matching paths"**，实际 Claude Code 官方不支持该机制。本机制是 RichLethe 单边补全的真正实现（PostToolUse hook + SessionStart 兜底），不回流上游。

详见 `docs/architecture/`（未来若需 ADR 化）和本文档自身的修订历史。

---

## 修订历史

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-22 | 初稿 | P29 激活 rules 机制 + 裁剪 narrative/data-files |
| 2026-05-22 | 拆出索引到 rules-reference.md | P30 从上游补 5 个 rules，单一文档承载机制+索引开始臃肿 |
