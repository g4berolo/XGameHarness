---
name: gate-check
description: "Validate readiness to advance between development phases. Produces a PASS/CONCERNS/FAIL verdict with specific blockers and required artifacts."
argument-hint: "[target-phase: pre-production | first-playable | vertical-slice | alpha | beta | release]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash, Write
---

# Phase Gate Validation

This skill validates whether the project is ready to advance to the next development
phase. It checks for required artifacts, quality standards, and blockers.

**Distinct from `/project-stage-detect`**: That skill is diagnostic ("where are we?").
This skill is prescriptive ("are we ready to advance?" with a formal verdict).

## Stage Taxonomy (7 stages / 6 gates, linear)

```
Concept → Pre-Production → First Playable → Vertical Slice → Alpha → Beta → Release
```

Sub-phases live in the project's own `plan/stage.md`, **not in this skill**.
Which sub-phases exist, what they mean here, and which are Critical is a
per-project decision — a farming sim and a roguelike do not share a definition
of "vertical slice content complete". This skill supplies the stage vocabulary,
the universal artifact floor, and the advance rule; the project supplies the
specifics.

`plan/stage.md` carries the current stage in its frontmatter (`current_stage:`).
There is no `plan/stage.txt` — a separate single-line file only ever drifted
from the table beside it.

**Advance rule**: a stage is passable when **every Critical row of the current
stage in `plan/stage.md` is ✅ Done** and the universal artifact floor for that
gate (§ 2) is met.

---

## 1. Parse Arguments

- **With argument**: `/gate-check first-playable` — validate readiness for that
  specific phase
- **No argument**: read `current_stage` from the `plan/stage.md` frontmatter,
  then validate the NEXT stage transition

---

## 2. Phase Gate Definitions

### 2.0 First: is there a stage SoT?

Before anything else, read `plan/stage.md`.

**If it does not exist**, stop and offer to create it — do not invent a checklist
and do not report FAIL (a project with no stage file has not failed a gate, it
simply has not set one up):

> "本项目还没有 `plan/stage.md`（阶段 SoT）。没有它我只能判通用工件，判不了
> 子阶段。要我从 harness 模板 `${CLAUDE_PLUGIN_ROOT}/docs/templates/stage.md`
> 生成一份吗？生成后你再把「本项目含义」列按本项目填一遍。"

If the user declines, continue with the universal floor below only, and say
plainly in the verdict that the sub-phase check was skipped for lack of a SoT.

### 2.1 Universal artifact floor

These hold for any game project regardless of engine, genre or content. They are
the *floor*, not the whole gate — the project's Critical rows are the rest.

| Gate | Universal artifacts | Universal quality checks |
|---|---|---|
| Concept → Pre-Production | `design/gdd/game-concept.md` with real content; pillars recorded (in the concept doc or `design/gdd/game-pillars.md`) | Core loop described; target audience identified; concept reviewed (`/design-review` verdict not MAJOR REVISION NEEDED) |
| Pre-Production → First Playable | Engine pinned (the `- **Engine**:` line in the root `CLAUDE.md` is filled, not the `<engine + version>` placeholder); ≥1 ADR under `docs/architecture/`; ≥1 approved GDD in `design/gdd/`; ≥1 sprint plan in `plan/sprints/` | Thinnest end-to-end playable path runs; MVP GDDs cross-checked against each other |
| First Playable → Vertical Slice | ≥1 playtest report in `plan/playtests/` | Core loop playable start to finish; no defect blocking that loop; playtest feedback triaged |
| Vertical Slice → Alpha | Slice-scope systems exist in code, not only in `design/gdd/` (cross-reference the two) | The slice stands alone as a demo; playtest shows the pillars actually land |
| Alpha → Beta | Test suite present and runnable; performance baseline recorded in `.claude/docs/technical-preferences.md` | Tests pass; no missing MVP feature blocking a full playthrough |
| Beta → Release | Performance targets in `technical-preferences.md` met and measured on target platforms | No critical or high-severity defects; accessibility basics covered; localization done or explicitly waived by the user |
| Release → Live | Packaged build produced; store metadata drafted; legal/compliance items recorded | Full QA sign-off; build compiles and packages cleanly |

### 2.2 Project sub-phases

Read the `plan/stage.md` matrix. For the **target** gate's originating stage:

- Collect every row whose Tier is `Critical`.
- `✅ Done` counts as met. `➖ N/A` counts as met **only if** the 本项目含义 column
  explains why — an unexplained N/A is a gap, ask about it.
- `⏳` / `🔄` are blockers.
- `Should` rows that are not Done become CONCERNS, never FAIL.
- Rows the project added are treated exactly like the ones from the template.

Never substitute your own idea of what a stage requires for what the table says.
If a Critical row's meaning is unclear, ask the user rather than guessing.

---

## 3. Run the Gate Check

For each item in the target gate:

### Artifact Checks
- Read `plan/stage.md` for sub-phase status (Critical rows of the originating stage)
- Use `Glob` and `Read` to verify supporting files exist with real content
- For code checks: look under the project's own source root (`client/Source/` on
  the UE layout; read `CLAUDE.md` / `.claude/docs/directory-structure.md` rather
  than assuming). If the layout is unknown, ask.
- For asset checks: same — the project states where assets live

### Quality Checks
- For test checks: run whatever `technical-preferences.md` names as the test command
- For design review checks: `Read` the GDD and check for 8 required sections
- For performance checks: `Read` `.claude/docs/technical-preferences.md` and
  compare against profiling data
- For localization checks: `Grep` for hardcoded user-facing strings in the source root

### Cross-Reference Checks
- Compare `design/gdd/` documents against the actual implementation
- Verify sprint plans in `plan/sprints/` reference real work items
- Check `plan/stage.md` History section for stage-advance audit trail

---

## 4. Collaborative Assessment

For items that can't be automatically verified, **ask the user**:

- "I can't automatically verify that the core loop plays well. Has it been playtested?"
- "No playtest report found in `plan/playtests/`. Has informal testing been done?"
- "性能剖析数据不可用。本 harness 无性能剖析 skill —— 可以提供引擎 profiler 输出，或 spawn `game-studio-core:technical-director` 评估性能预算，你倾向哪个？"

**Never assume PASS for unverifiable items.** Mark them as MANUAL CHECK NEEDED.

---

## 5. Output the Verdict

```
## Gate Check: [Current Phase] → [Target Phase]

**Date**: [date]
**Checked by**: gate-check skill

### Universal artifact floor: [X/Y met]
- [x] Engine pinned in CLAUDE.md
- [ ] No ADR under docs/architecture/

### Required Sub-Phases (Critical tier, per plan/stage.md): [X/Y Done]
- [x] [ID] [sub-phase name] — Done [date]
- [ ] [ID] [sub-phase name] — In Progress
- [ ] [ID] [sub-phase name] — Not Started

### Quality Checks: [X/Y passing]
- [x] GDD has 8/8 required sections
- [ ] Tests — FAILED ([N] failures)
- [?] Core loop playtested — MANUAL CHECK NEEDED

### Blockers
1. **[ID] [sub-phase] incomplete** — [what the project's 本项目含义 column says
   it needs, and the concrete next action]
2. **[missing universal artifact]** — [how to produce it]

### Recommendations
- [Priority actions to resolve blockers]
- [Optional improvements that aren't blocking]

### Verdict: [PASS / CONCERNS / FAIL]
- **PASS**: All Critical sub-phases Done, all quality checks passing
- **CONCERNS**: Minor gaps exist but can be addressed during the next phase
- **FAIL**: Critical blockers must be resolved before advancing
```

---

## 6. Update Stage on PASS

When the verdict is **PASS** and the user confirms they want to advance, edit
`plan/stage.md` — one file, three edits:

1. Set `current_stage:` in the frontmatter to the new stage name.
2. In the matrix, set the originating stage's rows to ✅ Done **where they truly
   are**. Do not mass-mark: a row that is still open stays open and the History
   note records that the gate passed with it outstanding.
3. Append a History row: date, which gate, previous → new stage, and any
   Critical row that was waived (with the user's reason).

`current_stage` is what `/start`, `/project-stage-detect` and `/how-to-do` read,
so this single edit updates every downstream view.

**Always ask before writing**: "Gate passed. May I set `current_stage` to
'[新阶段]' in `plan/stage.md` and append the History entry?"

---

## 7. Follow-Up Actions

Based on the verdict, suggest specific next steps:

- **No game concept?** → `/brainstorm` to create one
- **No systems index?** → `/map-systems` to decompose the concept into systems
- **Missing design docs?** → `/reverse-document`, or spawn `game-studio-core:game-designer`
- **Missing ADRs?** → spawn `game-studio-core:technical-director`, writing to
  `docs/architecture/` per the architecture-decision-record template
- **Walking Skeleton incomplete?** → continue per the project's prototype plan
- **No sprint plan?** → `/sprint-plan new`
- **Tests failing?** → no QA agent in this harness; report the failures to the
  user. On UE projects `unreal-pack:unreal-specialist` can advise on the test module
- **No playtest data?** → `/playtest-report`
- **Performance unknown?** → spawn `game-studio-core:technical-director` (perf budget),
  or on UE `unreal-pack:unreal-specialist`
- **Not localized?** → no localization skill in this harness; surface it as a gap
- **Ready for release?** → 本 harness 无 launch-checklist skill；按 § Release 的 R-* 子阶段手工过清单，或 spawn `game-studio-core:producer` 生成发布清单

---

## Collaborative Protocol

This skill follows the collaborative design principle:

1. **Scan first**: Check all artifacts and quality gates
2. **Ask about unknowns**: Don't assume PASS for things you can't verify
3. **Present findings**: Show the full checklist with status
4. **User decides**: The verdict is a recommendation — the user makes the final call
5. **Get approval**: "May I write this gate check report to `plan/gate-checks/`?"

**Never** block a user from advancing — the verdict is advisory. Document the
risks and let the user decide whether to proceed despite concerns.
