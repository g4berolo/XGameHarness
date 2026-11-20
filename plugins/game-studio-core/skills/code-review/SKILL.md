---
name: code-review
description: "Performs an architectural and quality code review on a specified file or set of files. Checks for coding standard compliance, architectural pattern adherence, SOLID principles, testability, and performance concerns."
allowed-tools: Read, Glob, Grep, Bash
---

参数：[path-to-file-or-directory]


> **运行时适配**：先按需读取本插件 [`docs/codex-runtime.md`](../../docs/codex-runtime.md)。
> Codex 用 `$技能名` 或读取 SKILL.md；共享流程中的 Claude 工具名按宿主现有能力执行。
> `${CLAUDE_PLUGIN_ROOT}` 是本 SKILL.md 向上两级的插件根，不假定它在普通终端里存在。

When this skill is invoked:

1. **Read the target file(s)** in full.

2. **Locate the project's coding standards.** Read the applicable project instructions and the
   rules in `.claude/rules/` whose `paths` match the reviewed files. For UE C++, use the project's
   `ue-cpp-readability.md` and applicable formatter configuration. If the rule has not been synced,
   consult `rules/ue-cpp-readability.md` in the enabled unreal-pack. In a change review, report
   formatting findings on added or modified code.

3. **Identify the system category** (engine, gameplay, AI, networking, UI, tools)
   and apply category-specific standards.

4. **Evaluate against coding standards**:
   - [ ] Public methods and classes have doc comments
   - [ ] Cyclomatic complexity under 10 per method
   - [ ] Each method has a clear responsibility. Beyond roughly 40 lines of logic, check whether
         the steps belong together. Cite the specific responsibilities if a split would help.
   - [ ] Changed code makes independent operations and control flow easy to follow. For UE C++,
         check short branches, intermediate names, and the layout of reflection macros against
         the applicable rule. Flag compressed statements even in short methods.
   - [ ] Dependencies are injected (no static singletons for game state)
   - [ ] Configuration values loaded from data files
   - [ ] Systems expose interfaces (not concrete class dependencies)

5. **Check architectural compliance**:
   - [ ] Correct dependency direction (engine <- gameplay, not reverse)
   - [ ] No circular dependencies between modules
   - [ ] Proper layer separation (UI does not own game state)
   - [ ] Events/signals used for cross-system communication
   - [ ] Consistent with established patterns in the codebase

6. **Check SOLID compliance**:
   - [ ] Single Responsibility: Each class has one reason to change
   - [ ] Open/Closed: Extendable without modification
   - [ ] Liskov Substitution: Subtypes substitutable for base types
   - [ ] Interface Segregation: No fat interfaces
   - [ ] Dependency Inversion: Depends on abstractions, not concretions

7. **Check for common game development issues**:
   - [ ] Frame-rate independence (delta time usage)
   - [ ] No allocations in hot paths (update loops)
   - [ ] Proper null/empty state handling
   - [ ] Thread safety where required
   - [ ] Resource cleanup (no leaks)

8. **Output the review** in this format:

```
## Code Review: [File/System Name]

### Standards Compliance: [passed / applicable checks]
[List failures with line references]

### Architecture: [CLEAN / MINOR ISSUES / VIOLATIONS FOUND]
[List specific architectural concerns]

### SOLID: [COMPLIANT / ISSUES FOUND]
[List specific violations]

### Game-Specific Concerns
[List game development specific issues]

### Positive Observations
[What is done well -- always include this section]

### Required Changes
[Must-fix items before approval]

### Suggestions
[Nice-to-have improvements]

### Verdict: [APPROVED / APPROVED WITH SUGGESTIONS / CHANGES REQUIRED]
```
