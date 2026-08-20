---
name: design-system
description: "Guided GDD authoring for a single game system. Grades the change first (Lite by default, Full only for high-risk changes), then walks through the required sections collaboratively, cross-references dependencies, and writes incrementally to file."
argument-hint: "<system-name> (e.g., 'combat-system', 'inventory', 'dialogue')"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Skill
---

When this skill is invoked:

## 1. Parse Arguments & Validate

A system name argument is **required**. If missing, fail with:
> "Usage: `/design-system <system-name>` — e.g., `/design-system combat-system`
> Run `/map-systems` first to create the systems index, then use this skill
> to write individual system GDDs."

Normalize the system name to kebab-case for the filename (e.g., "combat system"
becomes `combat-system`).

**If the argument is not ASCII** (a Chinese system name, say), kebab-case does not
apply. Derive the filename in this order, and state which one you used:

1. An English filename already recorded for that system in `systems-index.md`
   (the Design Doc column, or an English name in the row)
2. The convention the project's existing GDD filenames follow — Glob
   `design/gdd/*.md` and match it
3. If neither settles it, ask the user for the filename before creating anything

Never transliterate silently: a filename nobody can predict is worse than one
question. The document *title* stays in the user's language regardless.

---

## 2. Gather Context (Read Phase)

Read all relevant context **before** asking the user anything. This is the skill's
primary advantage over ad-hoc design — it arrives informed.

### 2a: Required Reads

- **Game concept**: Read `design/gdd/game-concept.md` — fail if missing:
  > "No game concept found. Run `/brainstorm` first."
- **Systems index**: Read `design/gdd/systems-index.md` — fail if missing:
  > "No systems index found. Run `/map-systems` first to map your systems."
- **Target system**: Find the system in the index. If not listed, warn:
  > "[system-name] is not in the systems index. Would you like to add it, or
  > design it as an off-index system?"

### 2b: Dependency Reads

From the systems index, identify:
- **Upstream dependencies**: Systems this one depends on. Read their GDDs if they
  exist (these contain decisions this system must respect).
- **Downstream dependents**: Systems that depend on this one. Read their GDDs if
  they exist (these contain expectations this system must satisfy).

For each dependency GDD that exists, extract and hold in context:
- Key interfaces (what data flows between the systems)
- Formulas that reference this system's outputs
- Edge cases that assume this system's behavior
- Tuning knobs that feed into this system

### 2c: Optional Reads

- **Game pillars**: Read `design/gdd/game-pillars.md` if it exists
- **Existing GDD**: Read `design/gdd/[system-name].md` if it exists (resume, don't
  restart from scratch)
- **Related GDDs**: Glob `design/gdd/*.md` and read any that are thematically related
  (e.g., if designing "status-effects", also read "combat-system" even if it's not
  a direct dependency)

### 2d: Present Context Summary

Before starting design work, present a brief summary to the user:

> **Designing: [System Name]**
> - Priority: [from index] | Layer: [from index]
> - Depends on: [list, noting which have GDDs vs. undesigned]
> - Depended on by: [list, noting which have GDDs vs. undesigned]
> - Existing decisions to respect: [key constraints from dependency GDDs]
> - Pillar alignment: [which pillar(s) this system primarily serves]

If any upstream dependencies are undesigned, warn:
> "[dependency] doesn't have a GDD yet. We'll need to make assumptions about
> its interface. Consider designing it first, or we can define the expected
> contract and flag it as provisional."

End the summary with a **read list** — every file you actually opened in 2a-2c:

> 已读：`game-concept.md`、`systems-index.md`、`game-pillars.md`(1-80 行)、
> `<上游>.md`、`<下游>.md`

This exists because the 2a required reads have no other checkpoint. § 5a checks the
*output*, never whether the *input* was read, so a skipped required read can travel
all the way to delivery unnoticed. Printing the list makes the gap visible to the
user at the moment the summary appears. If a 2a required file is not on your list,
go read it before continuing.

**Do not ask "ready to start?" here.** Everything the user needs to decide is
gathered into one question in 2f, after grading — asking twice with no new
information in between is pure noise.

### 2e: Grade the Change (Lite / Full)

**Do this before creating any file.** Not every change deserves the same ceremony.
Forcing all 8 sections onto a drop-rate tweak is what makes people skip the process
entirely, and a skipped process records nothing at all.

**Default is Lite.** Escalate to Full only if the change hits **any** of these:

| # | Escalation trigger |
|---|---|
| 1 | Touches the interface of **more than 2 existing systems** |
| 2 | Changes the **core loop** itself (the 30-second or 5-minute loop structure) |
| 3 | Involves the **economy**, or anything monetization-related |
| 4 | Affects **save compatibility** (save format, migration) |
| 5 | Involves **network replication** or server authority |
| 6 | Is a **brand-new system** — one that has never been designed before. Being listed in `systems-index.md` does **not** disqualify it: `/map-systems` registers every system at once, so "listed" means enumerated, not designed |

Evaluate the triggers **from the context you just gathered**, not by asking the user
to self-assess — the dependency reads in 2b already tell you how many interfaces are
in play, and the systems index tells you whether the system is new.

Present the verdict with its reason, then let the user override:

> **建议档位：Lite** — 没有命中升级判据（改动只涉及 [system] 自身，
> 依赖接口不变，不涉及经济/存档/联机）。
> Lite = 意图 / 改动 / 非目标 / 验收，目标 30 行以内。

or

> **建议档位：Full** — 命中判据 #3（涉及经济系统）和 #1（会改动 [A]、[B]、[C]
> 三个系统的接口）。Full = 完整 8 段。

Hold the verdict — it goes into the single question in 2f, together with the design
premise. Do not ask about the rigor level on its own.

If the user downgrades a Full to Lite, **record which trigger was waived** in the
document's frontmatter (`> **降级说明**: 命中判据 #N，用户判断 [理由] 后按 Lite 写`).
Don't silently drop it — the next person reading the doc needs to know a known
risk was accepted.

**A brand-new system downgraded to Lite needs a structural swap, not just a note.**
Lite's 改动 section is a delta — 新增 / 修改 / 移除 — and for a system that does not
exist yet, 修改 and 移除 are empty by construction, leaving 新增 to carry the entire
design. That is trigger #6's whole purpose: keep new systems out of a section shape
that cannot hold them. When the user waives it anyway, rename the section:

| Lite section | For a brand-new system |
|---|---|
| `## 改动`（新增 / 修改 / 移除） | `## 构成` — what the system is made of, no delta sub-headings |

Everything else about Lite is unchanged. Do not let each document invent its own
workaround — that is how the first eight GDDs on this project ended up with a
`改动` section containing only a `新增` child and no rule behind it.

Hold the chosen rigor level for the rest of this skill. **Lite can be upgraded mid-flight**
if the design turns out bigger than expected (merge what's written into the matching
Full sections); a Full should not be downgraded once written.

### 2f: Confirm the Design Premise — the last cheap moment

**This is the single most valuable question in this skill. Do not skip it, and do
not merge it into the writing phase.**

A one-line system description in `systems-index.md` is **not** an approved design
premise. The user approved a twelve-row table; they did not approve what those
words expand into. "Explicit representation of promises, observable defection"
reads as a neutral system name in an index — and expands into ritual, collateral
and enforceable contracts once someone writes it out. That is a major gameplay
claim the user never agreed to, and by the time it is visible it is several hundred
lines deep.

Every step in that chain can be individually correct and the outcome still wrong.
Confirming here costs one question. Not confirming costs the document.

**Write the premise in plain language:**

- 3-6 sentences, in the user's own words
- **Zero coined terms.** If you need a word the user has not used, you are
  describing the design, not the premise — cut it
- Say what the system *is* and what it *is not*
- Name the one assumption most likely to be wrong

Then ask **one** `AskUserQuestion` carrying premise and rigor together:

> **#9 打算做成这样**（写之前先对一下，避免写完才发现方向不对）：
>
> 玩家之间可以结盟，但游戏**不提供**任何强制手段 —— 没有仪式、没有押金、
> 没有系统托管的契约。约束力只来自"谁看见了" ……
>
> **不做**：自动执行的协议、系统判定的违约惩罚。
>
> **最可能错的假设**：结盟需要一个显式的表示动作。
>
> 档位建议 **Full**（命中判据 #1 —— 触及 4 个系统接口）。

- Options: `就这么写` / `前提要改（我说哪里）` / `前提对，但档位改成 X`

If the premise is rejected, **rewrite it and ask again**. Do not start the skeleton
on a premise the user has not accepted — that is the entire point of this step.

Record the confirmed premise; it goes into the skeleton in § 3 and into any
delegation brief in § 6.

---

## 3. Create File Skeleton

Once the user confirms, **immediately** create the GDD file with empty section
headers. This ensures incremental writes have a target.

The template at `${CLAUDE_PLUGIN_ROOT}/docs/templates/game-design-document.md`
(bundled with this plugin) carries **both rigor levels** plus the shared "what does not
belong in a GDD" test. Read it and use the skeleton matching the rigor level chosen in 2e.

### Both rigor levels: seed the skeleton with the constraints

**Write the upstream constraints into the file, not just into your own context.**
Put two blocks at the top of the skeleton before anything else:

```markdown
## 设计前提

[2f 里用户确认过的那段原话，一字不改]

## 已定决策摘要

[从 Phase 2 提取，逐条注明出处文件。这一节是**写作前的锁**，不是背景介绍：]
- <上游文件> 已锁死 <约束>，本篇不得重划
- <支柱 N> 推论：<对本系统意味着什么>
- <某条边界> 属规范 / 属数据实例示意 —— 标清楚，下游会当硬依赖用
```

Why this and not just a good delegation brief: **a brief dies the moment the task
ends; the file outlives everyone.** Whoever edits this system in three weeks — a
different agent, a different session, you after a compaction — reads the file, not
your brief. Without these blocks they re-derive the upstream constraints from
scratch, or worse, silently contradict them.

This was the highest-rated mechanic in the `/idea-to-gdd` field trial: the
subagent that had it reported that its direction was pinned before it wrote a
line, which removed a whole round of trial and error and made conflict with
upstream nearly impossible. The run that lacked it produced a good document that
carries none of its own constraints forward.

Keep both blocks in the finished document. They are not scaffolding.

### Lite skeleton

```markdown
# [System Name]

> **Status**: In Design
> **Rigor**: Lite
> **Author**: [user + agents]
> **Last Updated**: [today's date]

## 设计前提

[2f 确认过的原话]

## 已定决策摘要

[Phase 2 提取的上游约束，逐条注明出处]

## 本篇用到的新词

[本文档引入的、用户此前没用过的词。没有就写"无"——不要留空]

| 词 | 含义 | 为什么需要它 |
|---|---|---|

## 意图

[To be designed]

## 改动
<!-- 全新系统降级到 Lite 时，本节改名为「构成」，只写系统由什么组成，
     不用 新增/修改/移除 三个子标题 —— 见 § 2e -->

[To be designed]

## 非目标

[To be designed]

## 验收

[To be designed]
```

### Full skeleton

```markdown
# [System Name]

> **Status**: In Design
> **Rigor**: Full
> **Author**: [user + agents]
> **Last Updated**: [today's date]
> **Implements Pillar**: [from context]
> **升 Full 的理由**: [which escalation trigger fired, from 2e]

## 设计前提

[2f 确认过的原话]

## 已定决策摘要

[Phase 2 提取的上游约束，逐条注明出处]

## 本篇用到的新词

[本文档引入的、用户此前没用过的词。没有就写"无"——不要留空]

| 词 | 含义 | 为什么需要它 |
|---|---|---|

## Overview

[To be designed]

## Player Fantasy

[To be designed]

## Detailed Design

### Core Rules

[To be designed]

### States and Transitions

[To be designed]

### Interactions with Other Systems

[To be designed]

## Formulas

[To be designed]

## Edge Cases

[To be designed]

## Dependencies

[To be designed]

## Tuning Knobs

[To be designed]

## Visual/Audio Requirements

[To be designed]

## UI Requirements

[To be designed]

## Acceptance Criteria

[To be designed]

## Open Questions

[To be designed]
```

Ask: "May I create the skeleton file at `design/gdd/[system-name].md`?"

After writing, update `team/session-state/{identity}/active.md` with:
- Task: Designing [system-name] GDD
- Current section: Starting (skeleton created)
- File: design/gdd/[system-name].md

---

## 4. Section-by-Section Design

### Applies to both rigor levels: what does NOT go in a GDD

> **实现可以变、而玩家可感知的行为不变的，就不属于 GDD。**

Before writing any section, filter the content against this test. A GDD is a
**behavior contract**, not an implementation plan. Keep out:

- Concrete class/function names (`ARoomBase`, `CalcDamage()`) → code; the
  architectural choice goes in an ADR
- Blueprint node wiring, component trees → code
- Library / framework / plugin选型 → ADR (`architecture-decision-record.md`)
- **The number tables themselves** (each weapon's damage) → data files. The GDD
  carries the formula shape and safe ranges; `/balance-check` reads the data,
  not this document
- Step-by-step implementation plans → sprint plan / task tracker

This is the single biggest source of GDD rot: implementation detail goes stale the
moment the code changes, and nothing tells the reader which half of the document
still holds. If the user supplies such detail during design, capture it — then say
where it actually belongs and route it there instead of writing it into the GDD.

### Applies to both rigor levels: a word the user has not met cannot appear in a question

Design writing coins vocabulary — that is normal and often necessary. What is not
acceptable is **coining a word silently and then asking the user to make a decision
in it.** Observed failure: a delivered document introduced nine new terms plus a
symbol set and three internal numbering schemes, internally consistent and perfectly
serviceable between designers; every open decision was then phrased in those terms;
the user's answer was "I don't understand any of this" — about the core mechanic of
their own game.

Note where this comes from. When an agent could interrupt to ask, each coinage
surfaced one at a time, in context. Agents now take a defensible default and keep
writing, which is the right trade — a deadlock delivers nothing — but it makes the
coining **silent**, and the whole vocabulary arrives at once, at the end, several
hundred lines in. The document being well-formed hides it: an Open Questions section
makes the handoff *look* complete. Format compliance is not comprehension.

Two rules:

1. **Log every new term** in the `## 本篇用到的新词` table as you coin it — word,
   meaning, why an existing word would not do. Empty is not allowed; write 无 if
   there genuinely are none. Introducing a term is an event, not a private move.
2. **Translate before asking.** Any decision put to the user is restated in words
   the user has already used, even if that costs a sentence of setup. If a decision
   cannot be stated without a coined term, introduce the term first, in one line,
   then ask.

This applies with double force to anything a subagent returns: it wrote for
designers, and the user never read the file.

### Applies to both rigor levels: outsourcing a section (or the whole document)

The cycle below assumes you write. When a `specialist` agent writes instead
(§ 6 Author mode), the seven steps do not run per section — a subagent delivers
once and cannot stop for approval. Compress to:

```
主 agent 备简报（含 2f 前提 + 已定决策摘要 + 禁止触碰的文件）
  → agent 一次交付
  → 主 agent 校验（§ 5a 自检 + 简报边界是否被越过）
  → 把 agent 的决策清单翻译成用户词汇，一次性求裁定
```

**The approval gate moves; it does not disappear.** One approval covering the whole
delivery replaces one approval per section. What you must not do is let the outsourced
path quietly skip approval altogether because the per-section loop had nowhere to fit.

### Lite path

For a Lite doc, walk the four sections below in one pass. Same cycle as Full
(question → options → decision → draft → approval → write), just far fewer rounds —
a Lite doc should usually finish in a single sitting.

| Section | Goal | Watch for |
|---|---|---|
| 意图 | Why this change, 2-3 sentences | If the reason is "playtest showed X", link that report |
| 改动 | Only what changes: 新增 / 修改 / 移除 | Do **not** restate the whole system. If you find yourself rewriting it, that is a signal to escalate to Full |
| 非目标 | What this explicitly does not do | The most-skipped and most valuable section — it is the scope-creep brake. Do not let the user skip it |
| 验收 | 3-5 testable conditions | Untestable ("手感更好") does not go here — that belongs to `/playtest-report` |

If during the Lite pass any escalation trigger from 2e turns out to apply after all,
stop and offer the upgrade rather than quietly writing a 200-line "Lite" doc.

Then skip to **§ 5. Post-Design Validation**.

### Full path

Walk through each section in order. For **each section**, follow this cycle:

### The Section Cycle

```
Context  ->  Questions  ->  Options  ->  Decision  ->  Draft  ->  Approval  ->  Write
```

1. **Context**: State what this section needs to contain, and surface any relevant
   decisions from dependency GDDs that constrain it.

2. **Questions**: Ask clarifying questions specific to this section. Use
   `AskUserQuestion` for constrained questions, conversational text for open-ended
   exploration.

3. **Options**: Where the section involves design choices (not just documentation),
   present 2-4 approaches with pros/cons. Explain reasoning in conversation text,
   then use `AskUserQuestion` to capture the decision.

4. **Decision**: User picks an approach or provides custom direction.

5. **Draft**: Write the section content in conversation text for review. Flag any
   provisional assumptions about undesigned dependencies.

6. **Approval**: Ask "Approve this section, or would you like changes?"

7. **Write**: Use the Edit tool to replace the `[To be designed]` placeholder with
   the approved content. Confirm the write.

After writing each section, update `team/session-state/{identity}/active.md` with the
completed section name.

### Section-Specific Guidance

Each section has unique design considerations and may benefit from specialist agents:

---

### Section A: Overview

**Goal**: One paragraph a stranger could read and understand.

**Questions to ask**:
- What is this system in one sentence?
- How does a player interact with it? (active/passive/automatic)
- Why does this system exist — what would the game lose without it?

**Cross-reference**: Check that the description aligns with how the systems index
describes it. Flag discrepancies.

---

### Section B: Player Fantasy

**Goal**: The emotional target — what the player should *feel*.

**Questions to ask**:
- What emotion or power fantasy does this serve?
- What reference games nail this feeling? What specifically creates it?
- Is this a "system you love engaging with" or "infrastructure you don't notice"?

**Cross-reference**: Must align with the game pillars. If the system serves a pillar,
quote the relevant pillar text.

---

### Section C: Detailed Design (Core Rules, States, Interactions)

**Goal**: Unambiguous specification a programmer could implement without questions.

This is usually the largest section. Break it into sub-sections:

1. **Core Rules**: The fundamental mechanics. Use numbered rules for sequential
   processes, bullets for properties.
2. **States and Transitions**: If the system has states, map every state and
   every valid transition. Use a table.
3. **Interactions with Other Systems**: For each dependency (upstream and downstream),
   specify what data flows in, what flows out, and who owns the interface.

**Questions to ask**:
- Walk me through a typical use of this system, step by step
- What are the decision points the player faces?
- What can the player NOT do? (Constraints are as important as capabilities)

**Agent delegation**: For complex mechanics, use the Agent tool to delegate to
`game-studio-core:game-designer` for high-level design review, or `game-studio-core:systems-designer` for detailed
mechanical modeling. Provide the full context gathered in Phase 2.

**Cross-reference**: For each interaction listed, verify it matches what the
dependency GDD specifies. If the dependency says "damage is calculated as X" and
this system expects something different, flag the conflict.

---

### Section D: Formulas

**Goal**: Every mathematical formula, with variables defined, ranges specified,
and edge cases noted.

**Questions to ask**:
- What are the core calculations this system performs?
- Should scaling be linear, logarithmic, or stepped?
- What should the output ranges be at early/mid/late game?

**Agent delegation**: For formula-heavy systems (combat, economy, progression),
delegate to `game-studio-core:systems-designer` via the Agent tool. Provide:
- The Core Rules from Section C (already written to file)
- Tuning goals from the user
- Balance context from dependency GDDs

The agent should return proposed formulas with variable tables and expected output
ranges. Present these to the user for review before approving.

**Cross-reference**: If a dependency GDD defines a formula whose output feeds into
this system, reference it explicitly. Don't reinvent — connect.

---

### Section E: Edge Cases

**Goal**: Explicitly handle unusual situations so they don't become bugs.

**Questions to ask**:
- What happens at zero? At maximum? At negative values?
- What happens when two effects trigger simultaneously?
- What happens if the player tries to exploit this? (Identify degenerate strategies)

**Agent delegation**: For systems with complex interactions, delegate to
`game-studio-core:systems-designer` to identify edge cases from the formula space.
For narrative systems, consult `game-studio-core:narrative-director` for
story-breaking edge cases. (The plugin prefix is mandatory — a bare name is
rejected with `Agent type not found`.)

**Cross-reference**: Check edge cases against dependency GDDs. If combat says
"damage cannot go below 1" but this system can reduce damage to 0, that's a
conflict to resolve.

---

### Section F: Dependencies

**Goal**: Map every system connection with direction and nature.

This section is partially pre-filled from the context gathering phase. Present the
known dependencies from the systems index and ask:
- Are there dependencies I'm missing?
- For each dependency, what's the specific data interface?
- Which dependencies are hard (system cannot function without it) vs. soft
  (enhanced by it but works without it)?

**Cross-reference**: This section must be bidirectionally consistent. If this system
lists "depends on Combat", then the Combat GDD should list "depended on by [this
system]". Flag any one-directional dependencies for correction.

---

### Section G: Tuning Knobs

**Goal**: Every designer-adjustable value, with safe ranges and extreme behaviors.

**Questions to ask**:
- What values should designers be able to tweak without code changes?
- For each knob, what breaks if it's set too high? Too low?
- Which knobs interact with each other? (Changing A makes B irrelevant)

**Agent delegation**: If formulas are complex, delegate to `game-studio-core:systems-designer`
to derive tuning knobs from the formula variables.

**Cross-reference**: If a dependency GDD lists tuning knobs that affect this system,
reference them here. Don't create duplicate knobs — point to the source of truth.

---

### Section H: Acceptance Criteria

**Goal**: Testable conditions that prove the system works as designed.

**Questions to ask**:
- What's the minimum set of tests that prove this works?
- What performance budget does this system get? (frame time, memory)
- What would a QA tester check first?

**Cross-reference**: Include criteria that verify cross-system interactions work,
not just this system in isolation.

---

### Optional Sections: Visual/Audio, UI Requirements, Open Questions

These sections are included in the template but aren't part of the 8 required
sections. Offer them after the required sections are done:

Use `AskUserQuestion`:
- "The 8 required sections are complete. Do you want to also define Visual/Audio
  requirements, UI requirements, or capture open questions?"
  - Options: "Yes, all three", "Just open questions", "Skip — I'll add these later"

For **Visual/Audio**: There is no art or audio agent in this harness (see the § 6
routing table). Ask the user directly for any detail you need. A brief note usually
suffices at the GDD stage.

For **UI Requirements**: There is no UX agent either — gather requirements from the
user. On a UE project, `unreal-pack:ue-umg-specialist` can advise on UMG/CommonUI
feasibility once the requirements exist.

For **Open Questions**: Capture anything that came up during design that wasn't
fully resolved. Each question should have an owner and target resolution date.

---

## 5. Post-Design Validation

After all sections are written:

### 5a: Self-Check

Read back the complete GDD from file (not from conversation memory — the file is
the source of truth).

**Both rigor levels**:
- No `[To be designed]` placeholders remain
- The `Rigor` field in the header matches what was actually written
- Acceptance criteria are testable
- No implementation detail leaked in (class names, node wiring, number tables) —
  see the filter at the top of § 4
- `## 设计前提` still matches what the user confirmed in 2f. **If the document
  drifted off its premise, say so — do not quietly reconcile the premise to the
  document.** The premise is the approved thing; the document is not
- `## 已定决策摘要` cites its sources, and nothing in the body contradicts them
- `## 本篇用到的新词` covers every term the document coined. Scan the body for
  words the user never used and check each one is in the table

**Lite only**:
- 非目标 is filled in, not empty or "无"
- The whole document is still short. If it grew past ~50 lines, tell the user it
  outgrew Lite and offer to restructure it as Full

**Full only**:
- All 8 required sections have real content
- Formulas reference defined variables
- Edge cases have resolutions
- Dependencies are listed with interfaces
- The `升 Full 的理由` field names the trigger that fired
- **Length is a smell, not a limit.** Lite has an explicit brake and Full has none,
  so Full is where a document can grow without anything noticing. Past roughly 400
  lines, ask once: is this one system, or two that should be split? Dense is fine —
  do not trim a document that earns its length. What you are checking for is a
  second system that grew inside the first.

### 5b: Offer Design Review

Before the summary, run a **decision-consistency check**. Every decision the user
made during this session — including the reasons they gave in conversation — gets
checked against the documents already locked down.

Why this is not covered elsewhere: `/design-review` reads documents, and a reason
given out loud is not in any document. A user who has locked several architectural
boundaries over the past weeks is not carrying all of them in working memory, and
nothing reminds them. Observed case: a user chose an option because it "saves
tokens", when a boundary they themselves froze two days earlier — all AI decisions
in the simulation layer, no LLM involved — meant that option had no token cost
either way. The choice was defensible; the reason was not. It was caught only
because that document happened to be an upstream dependency this time.

For each user decision this session:
- Does the **decision** contradict a locked document?
- Does the **stated reason** contradict one?

Report either as: *"你选了 X，理由是 Y。但 `<文件>` 已定 Z —— 按 Z，Y 不成立。
选择本身可能仍然对，但如果你是冲着 Y 去的，它不会给你那个收益。"* Then let the
user decide. Do not silently correct them, and do not silently let it pass.

Then present a completion summary:

> **GDD Complete: [System Name]** ([Lite] / [Full])
> - Sections written: [list]
> - **New terms introduced**: [from 本篇用到的新词, or "none"] ← say these out loud;
>   the user has not read the document
> - Provisional assumptions: [list any assumptions about undesigned dependencies]
> - Cross-system conflicts found: [list or "none"]
> - Decision-consistency check: [conflicts found, or "none"]

Use `AskUserQuestion`:
- "Run `/design-review` now to validate the GDD?"
  - Options: "Yes, run review now", "I'll review it myself first", "Skip review"

If yes, invoke the design-review skill on the completed file.

### 5c: Update Systems Index

After the GDD is complete (and optionally reviewed):

- Read the systems index
- Update the target system's row:
  - If design-review was run and verdict is APPROVED: Status → "Approved"
  - If design-review was run and verdict is NEEDS REVISION: Status → "In Review"
  - If design-review was skipped: Status → "Designed" (pending review)
  - If the user chose "I'll review it myself first": Status → "Designed"
  - Design Doc: link to `design/gdd/[system-name].md`
- Update the Progress Tracker counts

Ask: "May I update the systems index at `design/gdd/systems-index.md`?"

### 5d: Update Session State

Update `team/session-state/{identity}/active.md` with:
- Task: [system-name] GDD
- Status: Complete (or In Review if design-review was run)
- File: design/gdd/[system-name].md
- Rigor: [Lite / Full]; Sections: [all Lite sections / all 8 Full sections] written
- Next: [suggest next system from design order]

### 5e: Suggest Next Steps

Use `AskUserQuestion`:
- "What's next?"
  - Options:
    - "Design next system ([next-in-order])" — if undesigned systems remain
    - "Fix review findings" — if design-review flagged issues
    - "Stop here for this session"
    - "Run `/gate-check`" — if enough MVP systems are designed

---

## 6. Specialist Agent Routing

This skill delegates to specialist agents for domain expertise. The main session
orchestrates the overall flow; agents provide expert content.

Agent identifiers require their plugin prefix — a bare name is rejected with
`Agent type not found`. `unreal-pack:*` entries exist only on projects that
enabled that plugin. Where a column reads "(no agent)", this harness has no
specialist for that area: gather the input from the user instead of inventing
an agent name.

| System Category | Primary Agent | Supporting Agent(s) |
|----------------|---------------|---------------------|
| Combat, damage, health | `game-studio-core:game-designer` | `game-studio-core:systems-designer` (formulas) |
| Economy, loot, crafting | `game-studio-core:economy-designer` | `game-studio-core:systems-designer` (curves), `game-studio-core:game-designer` (loops) |
| Progression, XP, skills | `game-studio-core:game-designer` | `game-studio-core:systems-designer` (curves), `game-studio-core:economy-designer` (sinks) |
| Dialogue, quests, lore | `game-studio-core:narrative-director` | `game-studio-core:game-designer` (systems side) |
| UI systems (HUD, menus) | `game-studio-core:game-designer` | `unreal-pack:ue-umg-specialist` (UE feasibility); UX flows — no agent |
| Audio systems | `game-studio-core:game-designer` | audio direction — no agent, ask the user |
| AI, pathfinding, behavior | `game-studio-core:game-designer` | `game-studio-core:systems-designer` (scoring); UE implementation — `unreal-pack:unreal-specialist` |
| Level/world systems | `game-studio-core:level-designer` | `game-studio-core:narrative-director` (world lore) |
| Camera, input, controls | `game-studio-core:game-designer` | `unreal-pack:unreal-specialist` (UE feasibility) |

**When delegating via Agent tool — pick a mode and say which in the brief.**

A subagent cannot ask the user anything: `AskUserQuestion` is stripped from
subagents, and no agent's message counts as user consent. Its agent definition
therefore tells it to take defensible defaults, deliver, and list every
overridable decision in its report. **A brief that demands approval before writing
deadlocks it.** Choose one of these instead:

| Mode | Use when | Who writes |
|---|---|---|
| **Consult** | You want expert input on a question or a single section, and you will fold it in yourself | Agent writes **nothing**. Main session writes. |
| **Author** | The task *is* to produce or fill a named file | **The agent writes that file.** Main session writes nothing into it. |

Both modes, always provide: system name, rigor level and why, the design premise
confirmed in 2f, the game concept summary, dependency GDD excerpts, and the
constraints the agent must not violate.

**Author mode additionally requires:**
- Name the exact file, and name what the agent must **not** touch (typically
  `systems-index.md`, `team/session-state/`, and the file header)
- State explicitly that writing that file is in scope and needs no approval
- Require the report to end with an overridable-decision list

**Silence in a brief is ambiguous — be explicit.** Observed behaviour: an agent
treated dependencies that were *named but not supplied* as "go read them yourself",
and a file that was *never mentioned at all* as "deliberately excluded" — and read
the first while skipping the second. If a file matters, name it. If it is
deliberately out of scope, say so.

**On receiving the agent's report** (both modes): before relaying any decision to
the user, apply the vocabulary rule in § 4 — restate each item in words the user
has already used. The agent writes for designers; the user did not read the file.

---

## 7. Recovery & Resume

If the session is interrupted (compaction, crash, new session):

1. Read `team/session-state/{identity}/active.md` — it records the current system,
   the chosen rigor level, and which sections are complete
2. Read `design/gdd/[system-name].md` — the `Rigor` field in the header is
   authoritative (session state can be stale, see R1); sections with real content
   are done, sections with `[To be designed]` still need work
3. Resume from the next incomplete section — no need to re-discuss completed ones,
   and do **not** re-run the 2e grading on a file that already declares a rigor level

This is why incremental writing matters: every approved section survives any
disruption.

---

## Collaborative Protocol

This skill follows the collaborative design principle at every step:

1. **Question -> Options -> Decision -> Draft -> Approval** for every section
2. **AskUserQuestion** at every decision point (Explain -> Capture pattern):
   - Phase 2: "Ready to start, or need more context?" and "Lite or Full?" (2e)
   - Phase 3: "May I create the skeleton?"
   - Phase 4 (each section): Design questions, approach options, draft approval
   - Phase 5: "Run design review? Update systems index? What's next?"
3. **"May I write to [filepath]?"** before the skeleton and before each section write
4. **Incremental writing**: Each section is written to file immediately after approval
5. **Session state updates**: After every section write
6. **Cross-referencing**: Every section checks existing GDDs for conflicts
7. **Specialist routing**: Complex sections get expert agent input, presented to
   the user for decision — never written silently

**Never** auto-generate the full GDD and present it as a fait accompli.
**Never** write a section without user approval.
**Never** contradict an existing approved GDD without flagging the conflict.
**Always** show where decisions come from (dependency GDDs, pillars, user choices).
