# Technical Preferences

> Project-side file. Lives at `.claude/docs/technical-preferences.md`.
> First created by `/setup-engine` (§ 5); afterwards it is the project's own file —
> edit it freely, the harness never overwrites it.
>
> Read by: `/gate-check` (performance checks), `game-studio-core:technical-director`
> (performance budgets), `/start` (as a secondary signal only — the engine's source
> of truth is the `- **Engine**:` line in the project root `CLAUDE.md`).

**Last updated**: [date]

---

## Engine & Language

| Field | Value |
|---|---|
| **Engine** | [TO BE CONFIGURED] |
| **Engine version** | [TO BE CONFIGURED] |
| **Primary language** | [TO BE CONFIGURED] |
| **Secondary language** | [none / …] |
| **Build system** | [TO BE CONFIGURED] |
| **Asset pipeline** | [TO BE CONFIGURED] |

---

## Naming Conventions

Fill from the engine's own conventions — `/setup-engine` § 5 carries the defaults
for Godot / Unity / Unreal.

| Kind | Convention | Example |
|---|---|---|
| Classes | [ ] | [ ] |
| Functions / methods | [ ] | [ ] |
| Variables | [ ] | [ ] |
| Constants | [ ] | [ ] |
| Booleans | [ ] | [ ] |
| Files | [ ] | [ ] |

---

## Performance Budgets

Leave `[TO BE CONFIGURED]` until there is a real profiling baseline — an invented
budget is worse than none, because `/gate-check` will compare against it.

| Metric | Target | Hard limit | Measured on |
|---|---|---|---|
| Frame time | [TO BE CONFIGURED] | | |
| Frame rate | [TO BE CONFIGURED] | | |
| Memory (peak) | [TO BE CONFIGURED] | | |
| Load time (cold) | [TO BE CONFIGURED] | | |
| Draw calls / frame | [TO BE CONFIGURED] | | |
| Package size | [TO BE CONFIGURED] | | |

**Target platform(s)**: [TO BE CONFIGURED]

---

## Testing

| Field | Value |
|---|---|
| **Framework** | [GUT (Godot) / NUnit (Unity) / UAutomationTest (Unreal) / …] |
| **Test location** | [ ] |
| **What must have tests** | [e.g. all pure-logic systems; formula/balance code] |
| **What need not** | [e.g. engine glue, UI layout] |
| **How to run** | [command] |

---

## Forbidden Patterns

Things reviewers and agents should reject on sight in this project.

- [ ]

---

## Allowed Libraries / Plugins

Anything not listed needs explicit approval (see
`game-studio-core:technical-director`).

| Name | Version | Purpose | Approved by / date |
|---|---|---|---|
| | | | |

---

## Revision History

| Date | Change | Reason |
|---|---|---|
| [date] | Created from harness template | `/setup-engine` |
