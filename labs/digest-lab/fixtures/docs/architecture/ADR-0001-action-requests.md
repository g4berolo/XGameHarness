# ADR-0001: 动作请求走统一的一条结构

> **Status**: Accepted
> **Date**: 2026-09-16
> **Deciders**: 手写夹具（读本实验室）

## Context

角色移动有五种方式，体力、攀爬、食物都要知道「玩家此刻在做什么」。
如果每个系统各自去读输入，同一帧会出现不同的判断。

## Decision

每一帧玩家输入先变成一条 `ActionRequest`，字段固定：

| 字段 | 含义 |
|---|---|
| `Actor` | 谁在动，用 `ActorId` 标识 |
| `Mode` | 想进入或维持的移动方式，枚举 `MoveMode`：`Walk` `Sprint` `Swim` `Climb` `Glide` |
| `Burst` | 这一帧是否带一次瞬时动作（爬墙时的「蹦」），布尔 |

移动系统拿着这条请求逐个问关心它的系统 `CanContinue(ActionRequest)`，
任何一个回 `false` 就切回 `Walk`（空中则 `Fall`），并广播一次 `OnInterrupted(ActorId, MoveMode)`。

体力系统在体力扣光的那一帧**主动**广播 `OnStaminaDepleted(ActorId)`，不等下一次 `CanContinue` 询问。

## Consequences

- 所有「能不能继续」的判断都在同一帧、同一条请求上做，不会出现两个系统各说各话
- 新增一种移动方式只用加一个 `MoveMode` 枚举值，不改询问流程
- 代价：每帧多一轮询问；系统少于十个时可以忽略
