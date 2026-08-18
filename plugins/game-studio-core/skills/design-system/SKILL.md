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

Use `AskUserQuestion`:
- "Ready to start designing [system-name]?"
  - Options: "Yes, let's go", "Show me more context first", "Design a dependency first"

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
| 6 | Is a **brand-new system** (not yet listed in `systems-index.md`) |

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

Use `AskUserQuestion`:
- "按 [Lite/Full] 写？"
  - Options: "就按建议的来", "升到 Full（我觉得比看起来重）", "降到 Lite（我知道风险）"

If the user downgrades a Full to Lite, **record which trigger was waived** in the
document's frontmatter (`> **降级说明**: 命中判据 #N，用户判断 [理由] 后按 Lite 写`).
Don't silently drop it — the next person reading the doc needs to know a known
risk was accepted.

Hold the chosen rigor level for the rest of this skill. **Lite can be upgraded mid-flight**
if the design turns out bigger than expected (merge what's written into the matching
Full sections); a Full should not be downgraded once written.

---

## 3. Create File Skeleton

Once the user confirms, **immediately** create the GDD file with empty section
headers. This ensures incremental writes have a target.

The template at `${CLAUDE_PLUGIN_ROOT}/docs/templates/game-design-document.md`
(bundled with this plugin) carries **both rigor levels** plus the shared "what does not
belong in a GDD" test. Read it and use the skeleton matching the rigor level chosen in 2e.

### Lite skeleton

```markdown
# [System Name]

> **Status**: In Design
> **Rigor**: Lite
> **Author**: [user + agents]
> **Last Updated**: [today's date]

## 意图

[To be designed]

## 改动

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

### 5b: Offer Design Review

Present a completion summary:

> **GDD Complete: [System Name]** ([Lite] / [Full])
> - Sections written: [list]
> - Provisional assumptions: [list any assumptions about undesigned dependencies]
> - Cross-system conflicts found: [list or "none"]

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

**When delegating via Agent tool**:
- Provide: system name, game concept summary, dependency GDD excerpts, the specific
  section being worked on, and what question needs expert input
- The agent returns analysis/proposals to the main session
- The main session presents the agent's output to the user via `AskUserQuestion`
- The user decides; the main session writes to file
- Agents do NOT write to files directly — the main session owns all file writes

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
