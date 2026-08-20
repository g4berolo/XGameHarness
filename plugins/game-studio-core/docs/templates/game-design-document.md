# 系统策划案模板（GDD）

本文件包含 **两档模板**。先定级，再挑对应的那一档往下抄。
`/design-system` 会自动帮你定级；手写时按下面的判据自己定。

---

## 定级：Lite 还是 Full

**默认 Lite。** 只有命中下列任意一条才升 Full：

- [ ] 改动会动到 **2 个以上已有系统的接口**
- [ ] 改动**核心循环**（30 秒循环 / 5 分钟循环的结构本身）
- [ ] 涉及**经济系统**，或任何付费 / 变现相关内容
- [ ] 影响**存档兼容**（存档格式、迁移）
- [ ] 涉及**联机同步**或服务器权威判定
- [ ] 这是一个**全新系统**（`systems-index.md` 里还没有的条目）

一条都没中 → Lite。

**为什么要分级**：调一个掉率和加一套元素反应系统，如果付同样的仪式成本，结果不是
文档变好，而是人**跳过流程**。Lite 的存在是为了让小改动**也愿意留下记录**。

**Lite 可以随时升 Full**（发现改动比预想的大就升，把 Lite 内容并进 Full 的对应
section）。**Full 不要降级** —— 已经写出来的约束不要为了省事丢掉。

---

## 判据：什么不该写进 GDD

> **实现可以变、而玩家可感知的行为不变的，就不属于 GDD。**

这条判据两档都适用。GDD 是**行为契约**，不是实现计划。

**不要写进来**（会随代码变化过期，是文档漂移的主要来源）：

| 不该写 | 该去哪 |
|---|---|
| 具体类名 / 函数名（`ARoomBase`、`CalcDamage()`） | 代码；架构层面的选择写 ADR |
| Blueprint 节点连法、组件树结构 | 代码 / 实现笔记 |
| 库、框架、插件的选型 | ADR（`architecture-decision-record.md`） |
| **数值表本体**（每把武器的具体伤害） | 数据表。GDD 只写公式结构和安全区间 |
| 分步实现计划、任务拆解 | sprint 计划 / 任务系统 |

**该写进来的**：玩家能观察到的行为、输入与输出、失败与边界情况、
外部约束（性能预算、平台限制）、可被测试或明确验证的条件。

---

## 两档共有的三节（写在最前面）

不管 Lite 还是 Full，开头都要有这三节。它们不是背景介绍，是**约束载体**。

| 节 | 写什么 | 为什么必须在文件里 |
|---|---|---|
| `## 设计前提` | 动笔前跟用户确认过的那段大白话原话，一字不改 | 索引里的一行系统描述**不等于**一个被批准的设计前提。「承诺的显式表示」看着中性，展开出来是「游戏里要有可强制的契约」——那是重大玩法主张。写在这里，后来人才知道这篇是站在什么假设上 |
| `## 已定决策摘要` | 上游锁死的约束，逐条注明出处文件 | 简报随任务结束就没了，**文件不会**。三周后改这个系统的人（或压缩后的你）读的是文件。缺了它就得把上游约束重推一遍，或者默默违反它 |
| `## 本篇用到的新词` | 本篇造的、用户此前没用过的词。没有就写「无」，**不留空** | 设计写作会造词，这正常；**造完词再用这套词问用户拿主意**不正常。实测：一篇文档造了 9 个新词 + 一套符号 + 三套编号，然后用它们写待裁定项，用户对自己游戏的核心机制回了句「听不懂」 |

**新词表的用法**：造一个记一条（词 / 含义 / 为什么现成的词不够用）。向用户提问时
必须换成他已经用过的词重述 —— 换不掉就先花一行介绍这个词，再问。

标注「数据实例的示意，不是规范」的东西，**下游会当硬依赖用**。在
`## 已定决策摘要` 里把「哪些是规范、哪些是示例」标清楚。

---

# 【Lite】模板

> 目标：**30 行以内**。写不完说明该升 Full 了。

```markdown
# [系统名 / 改动名]

> **Status**: Draft | In Review | Approved | Implemented
> **Rigor**: Lite
> **Author**: [Agent or person]
> **Last Updated**: [Date]

## 设计前提

[动笔前跟用户确认过的原话]

## 已定决策摘要

[上游锁死的约束，逐条注明出处]

## 本篇用到的新词

| 词 | 含义 | 为什么需要它 |
|---|---|---|

## 意图

[为什么要做这个改动？解决什么问题，或者想让玩家多感受到什么？2-3 句。
如果理由是「试玩里发现 X」，把那次试玩的结论链接过来。]

## 改动

[只写变化的部分，不重写整个系统。用下面三段中用得上的那几段。]

### 新增
- [新增的行为]

### 修改
- [原行为] → [新行为]

### 移除
- [被删掉的行为，以及为什么它可以被删]

> **全新系统被降级到 Lite 时，本节改名为 `## 构成`**，只写系统由什么组成，
> 不用「新增 / 修改 / 移除」三个子标题 —— 对一个还不存在的系统，「修改」和
> 「移除」天然是空的，delta 语义不成立。
>
> 升级判据 #6（全新系统 → Full）本来就是为了避免这种情况。走到这一步说明用户
> 知情豁免了它，那就把结构一起换掉，**不要每篇各自发明办法**。

## 非目标

[这次明确不做什么。这一段防的是范围蔓延(scope creep)，比「做什么」更容易被略过，
但往往更值钱。]

- 不做 [X]，因为 [理由]

## 验收

[3-5 条可测的条件。测不了的不要写。]

- [ ] [具体、可测]
- [ ] [具体、可测]
- [ ] [具体、可测]
```

---

# 【Full】模板

> 用于命中升级判据的高风险改动。以下 8 段是必需的，末尾三段可选。

# [Mechanic/System Name]

> **Status**: Draft | In Review | Approved | Implemented
> **Rigor**: Full
> **Author**: [Agent or person]
> **Last Updated**: [Date]
> **Implements Pillar**: [Which game pillar this supports]
> **升 Full 的理由**: [命中了哪一条判据 —— 写出来，方便后来人判断这份文档为什么这么重]

## 设计前提

[动笔前跟用户确认过的原话]

## 已定决策摘要

[上游锁死的约束，逐条注明出处]

## 本篇用到的新词

| 词 | 含义 | 为什么需要它 |
|---|---|---|

## Overview

[One paragraph that explains this mechanic to someone who knows nothing about
the project. What is it, what does the player do, and why does it exist?]

## Player Fantasy

[What should the player FEEL when engaging with this mechanic? What is the
emotional or power fantasy being served? This section guides all detail
decisions below.]

## Detailed Design

### Core Rules

[Precise, unambiguous rules. A programmer should be able to implement this
section without asking questions. Use numbered rules for sequential processes
and bullet points for properties.]

**注意**：「不需要提问就能实现」指的是**行为**没有歧义，不是把实现方式写死。
不要在这里指定类名或节点连法 —— 见开头的判据。

### States and Transitions

[If this system has states (e.g., weapon states, status effects, phases),
document every state and every valid transition between states.]

| State | Entry Condition | Exit Condition | Behavior |
|-------|----------------|----------------|----------|

### Interactions with Other Systems

[How does this system interact with combat? Inventory? Progression? UI?
For each interaction, specify the interface: what data flows in, what flows
out, and who is responsible for what.]

## Formulas

[Every mathematical formula used by this system. For each formula:]

### [Formula Name]

```
result = base_value * (1 + modifier_sum) * scaling_factor
```

| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| base_value | float | 1-100 | data file | The base amount before modifiers |
| modifier_sum | float | -0.9 to 5.0 | calculated | Sum of all active modifiers |
| scaling_factor | float | 0.5-2.0 | data file | Level-based scaling |

**Expected output range**: [min] to [max]
**Edge case**: When modifier_sum < -0.9, clamp to -0.9 to prevent negative results.

**这里写公式的结构和变量的安全区间，不写每个具体条目的数值。** 一把剑砍出多少
伤害属于数据表；「伤害 = 基础 ×(1+加成)×缩放」属于这里。数值体检走 `/balance-check`
读数据表，不读本文档。

## Edge Cases

[Explicitly document what happens in unusual situations. Each edge case
should have a clear resolution.]

| Scenario | Expected Behavior | Rationale |
|----------|------------------|-----------|
| [What if X is zero?] | [This happens] | [Because of this reason] |
| [What if both effects trigger?] | [Priority rule] | [Design reasoning] |

## Dependencies

[List every system this mechanic depends on or that depends on this mechanic.]

| System | Direction | Nature of Dependency |
|--------|-----------|---------------------|
| [Combat] | This depends on Combat | Needs damage calculation results |
| [Inventory] | Inventory depends on this | Provides item effect data |

## Tuning Knobs

[Every value that should be adjustable for balancing. Include the current
value, the safe range, and what happens at the extremes.]

| Parameter | Current Value | Safe Range | Effect of Increase | Effect of Decrease |
|-----------|--------------|------------|-------------------|-------------------|

## Acceptance Criteria

[Testable criteria that confirm this mechanic is working as designed.]

- [ ] [Criterion 1: specific, measurable, testable]
- [ ] [Criterion 2]
- [ ] [Criterion 3]
- [ ] Performance: System update completes within [X]ms
- [ ] No hardcoded values in implementation

---

**以下三段可选，不计入 8 段必需项。**

## Visual/Audio Requirements

[What visual and audio feedback does this mechanic need?]

| Event | Visual Feedback | Audio Feedback | Priority |
|-------|----------------|---------------|----------|

## UI Requirements

[What information needs to be displayed to the player and when?]

| Information | Display Location | Update Frequency | Condition |
|-------------|-----------------|-----------------|-----------|

## Open Questions

[Anything not yet decided. Each question should have an owner and deadline.]

| Question | Owner | Deadline | Resolution |
|----------|-------|----------|-----------|
