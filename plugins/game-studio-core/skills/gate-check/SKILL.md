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

Each stage has sub-phases by theme (Engineering / Art / Design / Production)
listed in `plan/stage.md`. Stage advances when **all Critical sub-phases** in
the current stage are Done.

**When a gate passes**, write the new stage name to `plan/stage.txt` (single
line, e.g. `First Playable`) and update `plan/stage.md` (mark previous-stage
phases as Done, list next-stage sub-phases). This updates the status line for
all future sessions.

---

## 1. Parse Arguments

- **With argument**: `/gate-check first-playable` — validate readiness for that
  specific phase
- **No argument**: Read `plan/stage.txt` for current stage, then validate the
  NEXT stage transition

---

## 2. Phase Gate Definitions

Each gate uses `plan/stage.md` as the SoT for sub-phase status. Sub-phase tier
classification (Critical / Should / Optional) is defined per stage in
`plan/stage.md`. The gate-check reads tier from the table and applies the rule
"all Critical Done" for PASS verdict.

### Gate: Concept → Pre-Production

**Required Artifacts:**
- [ ] `design/gdd/game-concept.md` exists and has content
- [ ] Game pillars defined (in concept doc or `design/gdd/game-pillars.md`)

**Quality Checks:**
- [ ] Game concept has been reviewed (`/design-review` verdict not MAJOR REVISION NEEDED)
- [ ] Core loop is described and understood
- [ ] Target audience is identified

---

### Gate: Pre-Production → First Playable

**Required (Critical sub-phases from `plan/stage.md` Pre-Production):**

Engineering theme:
- [ ] PP-E1 Engine Setup — UE 引擎 pinned + tech-prefs + engine-reference + ≥1 ADR
- [ ] PP-E2 至 PP-E6 Walking Skeleton S0-S4 — L1+L2+L3 切换 + Loop 闭环

Art theme:
- [ ] PP-A1 Style Direction & Mood Board — 视觉风格 lock
- [ ] PP-A4 Art Pipeline POC — 1 角色端到端 pipeline 验证

Design theme:
- [ ] PP-D1 Systems Design MVP — MVP-tier GDDs APPROVED

Production theme:
- [ ] PP-P1 Sprint Bootstrap — 第一份 sprint plan in `plan/sprints/`

**Quality Checks:**
- [ ] Walking Skeleton 跑通可演示（L1→L2→L3→L2→L1→RunEnd 完整 loop）
- [ ] MVP GDDs cross-system consistency 已校核（reciprocal sweep）
- [ ] 1 角色已通过 art pipeline 全 4 stage (Illustration → Modeling → Rigging → Animation)

---

### Gate: First Playable → Vertical Slice

**Required (Critical sub-phases from `plan/stage.md` First Playable):**

- [ ] FP-E1 Core Loop Walkthrough — RunStart→RunEnd 完整跑通
- [ ] FP-D1 First Encounter Tuning — 首轮数值平衡 pass
- [ ] FP-A1 Placeholder→Final 第一波 — 主角 + 1 英雄 + 1 怪 + 1 房间 final art
- [ ] FP-P1 First Internal Playtest — `/playtest-report` 已 run

**Quality Checks:**
- [ ] Core loop playable end-to-end
- [ ] No critical bugs blocking the core loop
- [ ] Playtest feedback collected and triaged

---

### Gate: Vertical Slice → Alpha

**Required (Critical sub-phases from `plan/stage.md` Vertical Slice):**

- [ ] VS-E1 Single Floor Feature Complete — 1 楼层全 MVP 系统真实装
- [ ] VS-D1 Single Floor Content Pass — 1 楼层完整内容
- [ ] VS-A1 Vertical Slice Art Quality Pass — 该楼层 ship-quality
- [ ] VS-A2 Audio First Pass — SFX 真实装
- [ ] VS-P1 Vertical Slice Playtest — 外部 playtester

**Quality Checks:**
- [ ] 1 完整 floor 可独立 ship quality demo
- [ ] All MVP systems referenced by this floor are implemented (not just GDD)
- [ ] Playtest demonstrates pillar fulfillment

---

### Gate: Alpha → Beta

**Required (Critical sub-phases from `plan/stage.md` Alpha):**

- [ ] A-E1 Feature Complete — 全 MVP 系统真实装
- [ ] A-D1 Content Complete — 全英雄/士兵/装备/敌人/房间/Boss in
- [ ] A-A1 All Assets In (允许占位)
- [ ] A-P1 Alpha Playtest Rounds — 多轮 playtest + feedback iteration

**Quality Checks:**
- [ ] No missing MVP feature blocking play
- [ ] Content可以走通完整 run
- [ ] Tests passing (run test suite via Bash)
- [ ] Performance baseline measured

---

### Gate: Beta → Release

**Required (Critical sub-phases from `plan/stage.md` Beta):**

- [ ] B-E1 Performance Pass — 性能/帧率/内存达标
- [ ] B-D1 Balance Final Pass — 数值终调
- [ ] B-A1 Polish Asset Pass — final art + VFX + 音乐
- [ ] B-Q1 Bug Fixing — content/feature lock + 0 critical bug
- [ ] B-L1 Localization Pass — 文本外化 + 翻译 + LQA

**Quality Checks:**
- [ ] All features from milestone plan are implemented
- [ ] No critical/high-severity bugs
- [ ] Performance targets met on target platforms
- [ ] Accessibility basics covered

---

### Gate: Release → Live (post-launch)

**Required (Release stage sub-phases):**

- [ ] R-Q1 Full QA Sign-off — QA 全 pass / 0 中高 bug
- [ ] R-L1 Legal & Compliance — EULA / 隐私政策 / 评级
- [ ] R-S1 Store Metadata — Steam 页 / 商品描述 / 截图 / trailer
- [ ] R-S2 Launch Build — 终版 build + 渠道分发包

**Quality Checks:**
- [ ] Full QA pass signed off
- [ ] Build compiles and packages cleanly
- [ ] Legal/compliance verified
- [ ] Store page ready

---

## 3. Run the Gate Check

For each item in the target gate:

### Artifact Checks
- Read `plan/stage.md` for sub-phase status (look for ✅ Done in target stage Critical rows)
- Use `Glob` and `Read` to verify supporting files exist with real content
- For code checks: verify `client/Source/` directory has expected modules
- For asset checks: verify `client/Content/` has imported assets

### Quality Checks
- For test checks: Run UAutomationTest suite via `Bash` if configured
- For design review checks: `Read` the GDD and check for 8 required sections
- For performance checks: `Read` `.claude/docs/technical-preferences.md` and
  compare against profiling data
- For localization checks: `Grep` for hardcoded strings in `client/Source/`

### Cross-Reference Checks
- Compare `design/gdd/` documents against `client/Source/` implementations
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

### Required Sub-Phases (Critical tier): [X/Y Done per plan/stage.md]
- [x] PP-E1 Engine Setup — Done 2026-04-13
- [ ] PP-E2 Walking Skeleton S0 — In Progress
- [ ] PP-A1 Style Direction — Not Started

### Quality Checks: [X/Y passing]
- [x] GDD has 8/8 required sections
- [ ] Tests — FAILED (3 failures in tests/unit/)
- [?] Core loop playtested — MANUAL CHECK NEEDED

### Blockers
1. **PP-E2..E6 (Walking Skeleton S0-S4) incomplete** — Continue Walking Skeleton
   per `prototypes/walking-skeleton-S0-S4.md`.
2. **PP-A1 Style Direction missing** — Start mood board + style keyword lock.

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

When the verdict is **PASS** and the user confirms they want to advance:

1. Write the new stage name to `plan/stage.txt` (single line, no trailing newline)
2. Update `plan/stage.md`:
   - Set previous stage sub-phases to ✅ Done (where they truly are)
   - Add next-stage sub-phase rows with ⏳ Not Started
   - Append History entry with date, gate, previous→new stage
3. This immediately updates the status line for all future sessions

Example: passing the "Pre-Production → First Playable" gate:
```bash
echo -n "First Playable" > plan/stage.txt
```
+ Edit `plan/stage.md` to reflect new stage and history.

**Always ask before writing**: "Gate passed. May I update `plan/stage.txt` to
'First Playable' and update `plan/stage.md` history?"

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
