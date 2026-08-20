---
name: design-review
description: "Reviews a game design document for completeness, internal consistency, implementability, and adherence to project design standards. Run this before handing a design document to programmers."
argument-hint: "[path-to-design-doc]"
user-invocable: true
allowed-tools: Read, Glob, Grep
---

When this skill is invoked:

1. **Read the target design document** in full.

2. **Read the master CLAUDE.md** to understand project context and standards.

3. **Read related design documents** referenced or implied by the target doc
   (check `design/gdd/` for related systems).

4. **Read the document's rigor level, then check completeness against that rigor level.**

   Look for a `Rigor: Lite` / `Rigor: Full` field in the header. A document with no
   rigor field predates the grading rule — grade it yourself using the triggers in
   `${CLAUDE_PLUGIN_ROOT}/docs/templates/game-design-document.md`, and note in the
   review which rigor level you assumed.

   A document marked `Status: Reverse-Documented` follows its own template
   (`design-doc-from-implementation.md`) — review it against that structure, not
   against either checklist below.

   **Do not review a Lite document against the 8-section checklist.** Lite is a
   deliberate choice, not an incomplete Full — reporting "3/8 sections" on a Lite
   doc is a false finding.

   **Both rigor levels — the three opening sections**:
   - [ ] `## 设计前提` present, and the document still matches it. **A document that
         drifted off its premise is a finding, and the premise is the approved
         thing** — never resolve the mismatch in the document's favour
   - [ ] `## 已定决策摘要` present, cites source files, and nothing in the body
         contradicts it. Check that normative constraints and illustrative data
         examples are labelled as such
   - [ ] `## 本篇用到的新词` present (无 is a valid value) and complete — scan the
         body for terms the user has not used and verify each appears in the table.
         **Any coined term used in an Open Question but missing from the table is a
         finding**: it means the user is being asked to decide in words nobody
         introduced to them

   **Lite checklist**:
   - [ ] 意图 — why this change exists
   - [ ] 改动 — only what changes (新增 / 修改 / 移除), not a restatement of the system.
         **For a brand-new system downgraded to Lite this section is named 构成**
         with no delta sub-headings; that is correct, not a defect
   - [ ] 非目标 — explicitly out of scope, and not empty
   - [ ] 验收 — 3-5 testable conditions
   - [ ] The four body sections above stay under ~50 lines. **The three opening
         sections and any appendix do not count toward it** — that ambiguity
         previously turned appendices into a relief valve, with a core design
         decision ending up filed as an "assumption" because the body had no room.
         If core design is sitting in an appendix or an assumptions list, report it:
         the tier is wrong, not the writing

   **Full checklist**:
   - [ ] Has Overview section (one-paragraph summary)
   - [ ] Has Player Fantasy section (intended feeling)
   - [ ] Has Detailed Rules section (unambiguous mechanics)
   - [ ] Has Formulas section (all math defined with variables)
   - [ ] Has Edge Cases section (unusual situations handled)
   - [ ] Has Dependencies section (other systems listed)
   - [ ] Has Tuning Knobs section (configurable values identified)
   - [ ] Has Acceptance Criteria section (testable success conditions)
   - [ ] Header names the escalation trigger that justified Full

   **Rigor misfit is itself a finding**: a Lite doc that touches three systems'
   interfaces or the economy should have been Full — say so. A Full doc written for
   a two-line tweak is over-ceremony — say that too.

4b. **Check for implementation detail that does not belong in a GDD.**

   Test: **实现可以变、而玩家可感知的行为不变的，就不属于 GDD。**

   Flag and name a better home for each hit:

   | Found in the doc | Belongs in |
   |---|---|
   | Concrete class / function names (`ARoomBase`, `CalcDamage()`) | code; the architectural choice → ADR |
   | Blueprint node wiring, component trees | code |
   | Library / framework / plugin selection | ADR |
   | Number tables (per-item values) | data files — the GDD keeps formula shape and safe ranges |
   | Step-by-step implementation plans | sprint plan / task tracker |

   This is the main driver of document rot: implementation detail goes stale as soon
   as the code moves, and nothing marks which half of the doc still holds. Report
   these under Recommendations, not as blockers, unless the doc is mostly
   implementation notes — in that case it is not a GDD and the verdict should say so.

5. **Check for internal consistency**:
   - Do the formulas produce values that match the described behavior?
   - Do edge cases contradict the main rules?
   - Are dependencies bidirectional (does the other system know about this one)?

6. **Check for implementability**:
   - Are the rules precise enough for a programmer to implement without guessing?
   - Are there any "hand-wave" sections where details are missing?
   - Are performance implications considered?

7. **Check for cross-system consistency**:
   - Does this conflict with any existing mechanic?
   - Does this create unintended interactions with other systems?
   - Is this consistent with the game's established tone and pillars?

8. **Output the review** in this format:

```
## Design Review: [Document Title]

### Rigor: [Lite / Full] ([declared in header] / [assumed — no rigor field])
[If the rigor level looks wrong for the change, say so and why]

### Completeness: [X/5 Lite items] or [X/8 Full sections present]
[List missing sections]

### Premise / Constraints / Vocabulary
- 设计前提: [present and matched / drifted — how / missing]
- 已定决策摘要: [sourced / unsourced / contradicted by body / missing]
- 新词表: [complete / missing N terms — list them / absent]

### Out-of-Scope Content
[Implementation detail that belongs elsewhere, with the destination for each.
"None" is a valid and common answer.]

### Consistency Issues
[List any internal or cross-system contradictions]

### Implementability Concerns
[List any vague or unimplementable sections]

### Balance Concerns
[List any obvious balance risks]

### Recommendations
[Prioritized list of improvements]

### Verdict: [APPROVED / NEEDS REVISION / MAJOR REVISION NEEDED]
```

9. **Contextual next step recommendations**:
   - If the document being reviewed is `game-concept.md` or `game-pillars.md`:
     - Check if `design/gdd/systems-index.md` exists
     - If it does NOT exist, add to Recommendations:
       > "This concept is ready for systems decomposition. Run `/map-systems`
       > to break it down into individual systems with dependencies and priorities,
       > then write per-system GDDs."
   - If the document is an individual system GDD:
     - Check if the systems index references this system
     - If verdict is APPROVED: suggest "Update the systems index status for
       this system to 'Approved'."
     - If verdict is NEEDS REVISION or MAJOR REVISION NEEDED: suggest "Update
       the systems index status for this system to 'In Review'."
     - Note: This skill is read-only. The user (or `/design-system`) must
       perform the actual status update in the systems index.
