---
managed-by: XGameHarness/game-studio-core
paths:
  - "design/gdd/**"
---

# Design Document Rules

## Scope of these rules

These rules govern **per-system design documents** — the output of `/design-system`
and `/reverse-document design`. Other documents that live under `design/gdd/`
(game-concept, game-pillars, systems-index, economy model, faction and character
sheets, art/sound bible) have their own templates and are NOT graded or checked
against the section lists below.

## Rigor first

- Every per-system design document MUST declare a rigor level in its header:
  `Rigor: Lite` or `Rigor: Full`
- **Lite is the default.** Escalate to Full only when the change hits one of these:
  touches more than 2 existing systems' interfaces; changes the core loop; involves
  the economy or monetization; affects save compatibility; involves network
  replication; or is a brand-new system that has never been designed before
  (being enumerated in `systems-index.md` does not make it designed)
- A Full document MUST state which trigger justified the escalation
- Grading exists so small changes still get written down. Do NOT apply the Full
  checklist to a Lite document — that is not a finding, it is the point

## Every document, both rigor levels

- MUST open with three sections, before any tier-specific content:
  - `## 设计前提` — the plain-language premise the user confirmed before writing
    started, unedited. A one-line system description in `systems-index.md` is NOT
    an approved premise; approving an index approves the enumeration, not what
    those words expand into
  - `## 已定决策摘要` — upstream constraints with their source files, and for each,
    whether it is normative or an illustrative data example (downstream treats
    examples as hard dependencies unless told otherwise). A delegation brief dies
    with the task; the file is what the next reader has
  - `## 本篇用到的新词` — every term this document coins that the user has not used
    before, with meaning and why an existing word would not do. Write 无 if there
    are none; never leave it empty
- **A term the user has not met MUST NOT appear in a question put to them.**
  Restate decisions in vocabulary the user has already used, or introduce the term
  first. A well-formed Open Questions section makes a handoff look complete;
  format compliance is not comprehension
- A design document is a **behavior contract, not an implementation plan**.
  Test: if the implementation can change without changing player-observable
  behavior, it does not belong here
- MUST NOT contain: concrete class/function names, Blueprint node wiring, library or
  framework selection (those go in an ADR), per-item number tables (those go in data
  files), or step-by-step implementation plans (those go in the sprint plan)
- Acceptance criteria must be testable — a QA tester must be able to verify pass/fail
- No hand-waving: "the system should feel good" is not a valid specification.
  Feel and pacing are validated by playtest, not asserted in a design document
- MUST be written incrementally: create the skeleton first, then fill each section one
  at a time with user approval between sections. Write each approved section to the
  file immediately to persist decisions and manage context

## Lite documents

- MUST contain: 意图 (why), 改动 (only what changes — 新增 / 修改 / 移除),
  非目标 (explicitly out of scope), 验收 (3-5 testable conditions)
- 非目标 MUST NOT be empty — it is the scope-creep brake
- 改动 describes the delta, not the whole system. Restating the entire system is the
  signal that this should have been Full
- **A brand-new system downgraded to Lite renames 改动 to 构成** and drops the
  新增/修改/移除 sub-headings — for a system that does not exist yet, two of the
  three are empty by construction. Trigger #6 exists to prevent this shape; when it
  is waived, swap the structure rather than letting each document improvise
- Keep it short. Past roughly 50 lines, restructure as Full

## Full documents

- MUST contain these 8 sections: Overview, Player Fantasy, Detailed Rules, Formulas,
  Edge Cases, Dependencies, Tuning Knobs, Acceptance Criteria
- Formulas must include variable definitions, expected value ranges, and example
  calculations — but the formula *shape* and safe ranges only; the concrete values
  live in data files
- Edge cases must explicitly state what happens, not just "handle gracefully"
- Dependencies must be bidirectional — if system A depends on B, B's doc must mention A
- Tuning knobs must specify safe ranges and what gameplay aspect they affect
- Balance values must link to their source formula or rationale
