# Systems Index: 山脊（代号）

> **Status**: Approved
> **Created**: 2026-09-16
> **Last Updated**: 2026-09-16
> **Source Concept**: design/gdd/game-concept.md

---

## Overview

这个游戏没有战斗，机制全部围绕「用一圈体力翻过一座山」。四个系统：
一个管怎么动（角色移动），一个管动的代价（体力），一个管两种最贵的动法（攀爬与滑翔），
一个管把代价补回来（食物与增益）。核心循环是「看地形 → 选路线 → 管体力 → 到了或掉了 → 补给」。

---

## Systems Enumeration

| # | System Name | Category | Priority | Status | Design Doc | Depends On |
|---|-------------|----------|----------|--------|------------|------------|
| 1 | 角色移动 | Core | MVP | Approved | design/gdd/character-movement.md | — |
| 2 | 体力 | Gameplay | MVP | Not Started | — | 角色移动 |
| 3 | 攀爬与滑翔 | Gameplay | MVP | Approved | design/gdd/climb-glide.md | 角色移动、体力 |
| 4 | 食物与增益 | Economy | Vertical Slice | Not Started | — | 体力 |

---

## Categories

| Category | Description | Typical Systems |
|----------|-------------|-----------------|
| **Core** | Foundation systems everything depends on | 角色移动 |
| **Gameplay** | The systems that make the game fun | 体力、攀爬与滑翔 |
| **Economy** | Resource creation and consumption | 食物与增益 |

---

## Priority Tiers

| Tier | Definition | Target Milestone | Design Urgency |
|------|------------|------------------|----------------|
| **MVP** | Required for the core loop to function | First playable prototype | Design FIRST |
| **Vertical Slice** | Required for one complete, polished area | Vertical slice / demo | Design SECOND |

---

## Dependency Map

### Foundation Layer (no dependencies)

1. 角色移动 — 五种移动方式是一切的底

### Core Layer (depends on foundation)

1. 体力 — depends on: 角色移动（它要知道玩家此刻在做哪种动作）

### Feature Layer (depends on core)

1. 攀爬与滑翔 — depends on: 角色移动、体力
2. 食物与增益 — depends on: 体力

---

## Recommended Design Order

| Order | System | Priority | Layer | Agent(s) | Est. Effort |
|-------|--------|----------|-------|----------|-------------|
| 1 | 角色移动 | MVP | Foundation | game-designer | S |
| 2 | 体力 | MVP | Core | game-designer + systems-designer | M |
| 3 | 攀爬与滑翔 | MVP | Feature | game-designer | S |
| 4 | 食物与增益 | Vertical Slice | Feature | economy-designer | S |

---

## Circular Dependencies

- None found

---

## High-Risk Systems

| System | Risk Type | Risk Description | Mitigation |
|--------|-----------|-----------------|------------|
| 体力 | Design | 三条路线（绕 / 爬 / 滑）能不能真的都可选，全靠体力和地形一起调 | 先写清规则，数值留给数据表 |

---

## Progress Tracker

| Metric | Count |
|--------|-------|
| Total systems identified | 4 |
| Design docs started | 2 |
| Design docs reviewed | 2 |
| Design docs approved | 2 |
| MVP systems designed | 2/3 |
| Vertical Slice systems designed | 0/1 |

---

## Next Steps

- [x] Review and approve this systems enumeration
- [ ] Design 体力（use `/design-system 体力`）
- [ ] Run `/design-review` on each completed GDD
