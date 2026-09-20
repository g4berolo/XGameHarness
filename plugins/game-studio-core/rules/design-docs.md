---
managed-by: XGameHarness/game-studio-core
paths:
  - "design/gdd/**"
  # 读本 2026-09-14 从 GDD 里搬到这儿了 —— 不写进来的话，
  # 改读本的时候这份规则不会注入，而「读本怎么写」那一整节就在这份规则里
  - "design/digest/**"
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

- **MUST have a companion 读本 file** at `design/digest/<same filename>.md` —
  **一份完整的、能从头读到尾的策划案**，不是导语、不是摘要。详见下面「读本怎么写」。
  它**不在 GDD 文件里**（2026-09-14 改的，理由在那一节开头）
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
- **每一条规则都要能指回三处之一**：`## 设计前提`、`## 已定决策摘要` 里某个上游文件、
  用户在对话里的回答。三处都指不回的，写进 `## Open Questions` 标「建议」，
  **不许写成规范**。自己编的规则没有任何地方会核对它，而它会长出新的边界情况、
  再长出新的旋钮。2026-09-15 实测：六句话的设计前提写出 533 行，
  其中起手扣一口、爬分两档、缓过来的刻度、缩圈、扩容硬帽、走路也回、
  游比跑贵、不做永久成长，八条全是 agent 自己加的
- **句子按下面「句子怎么写」那十条写，GDD 和读本同一套。**
  契约那几节需要精确，不需要文学 —— 精确靠把条件和结果说全，不靠加粗和破折号

## 读本怎么写

读本是给不做这块的人看的那份策划案。判据：只读读本，能懂这个系统怎么运转。

### 这一节改过三次，改之前先看这里

- 2026-09-07 把读本从「几句导语」改成完整策划案。
- 2026-09-14 把读本搬到 `design/digest/`，标题一律编号，加「名词对照」那一节。
- 2026-09-15 用户在客户端里读了一篇真写出来的体力系统读本，推翻了五条：
  十三节固定标题、「打个比方」要说失效点、「只记三句话」、每段开头加粗、标题里写数目。
  他的原话是「整体的冗长原因可能是源于文档的编写本身就比较啰嗦复杂」。
  留下的是编号和「名词对照」，那两条是他 09-14 要的。本节的节名和句子规矩按那次意见重写。
  **这五条是读完真东西之后推翻的，不是拍脑袋定的** —— 想改回去，先拿这几条规矩
  写一篇出来读一遍，别只看规矩本身像不像话。

### 读本住在哪儿

文件是 `design/digest/<跟 GDD 同名>.md`。头部三行，客户端靠它们判读本旧没旧。

```markdown
# <跟 GDD 一样的标题> — 读本

> **文档**：design/gdd/<文件名>.md
> **写于文档的最后更新**：<原样照抄那篇 GDD 头部的 Last Updated>
> **最后更新**：<今天>

### 1. 概括
```

「写于文档的最后更新」要原样照抄 GDD 的 `Last Updated`。写错或者漏写，客户端判不出旧没旧，而且不报错。
改了 GDD 的正文就要改它的 `Last Updated`，读本旧没旧全靠那一格。

2026-09-14 之前的读本写在 GDD 正文里，是一个叫「读本」的二级小节。客户端两种都认，只会提示挪出去。
改到那一篇时跑一次 `/game-studio-core:move-digest`，不要专门开一轮去搬。

### 九节（Full 文档）

一律三级标题，从 1 连排到 9。标题照抄，不改字，不加数目。

| 节 | 写什么 | 长度 |
|---|---|---|
| 1. 概括 | 这个系统管什么、跟哪几个系统有关、玩家在哪儿会碰到它 | 三到五句 |
| 2. 机制构成 | 每一条会影响玩家决策的规则。按玩家在做什么分小节。**至少一张图**，见下面「图」那一节 | 最长的一节 |
| 3. 例子 | 从头到尾走一遍一次具体的交互 | 五到十步 |
| 4. 非目标 | 读者可能以为它管、其实不管的事 | 三到六条 |
| 5. 关键决定 | 设计时真做过的取舍：定成了什么、另一种是什么、为什么没选那种 | 有几条写几条 |
| 6. 容易搞错的地方 | 没读过这篇的人会想当然以为是另一个样子的地方 | 有几条写几条 |
| 7. 名词对照 | 读本里的说法对应文档和代码里的真名，一张表。没有就写「无」 | 一张表 |
| 8. 旋钮 | 旋钮叫什么、管什么、调大调小分别会怎样，一张表 | 一张表 |
| 9. 对接 | 按角色分，各自最少要知道什么。末尾一小节写还没定的事 | 每个角色一段 |

Lite 文档写 1、2、3、4、7 五节，编号重排成 1 到 5，不要沿用 Full 的原编号。

**第 5 节和第 6 节只写 GDD 里已经有的东西。** GDD 里没有的取舍，读本不许补一条出来。

**第 4 节不写谁都不会误会的事。** 「体力不是生命值」这种谁都不会搞错的，不占一条。

**第 8 节末尾写一句「具体数值见规则表」。** 那是指出唯一真值在哪儿，不算省略。

### 句子怎么写

规矩来自阮一峰《中文技术文档的写作规范》和 yikeke《中文技术文档写作风格指南》。
2026-09-15 用户看完第一版读本之后挑定了这十条。

1. 一句话只说一件事，不超过 30 字。
2. 用陈述句、肯定句、主动语态。
3. 规则写成「什么情况下，发生什么」。写「普通行走不消耗体力，并且缓慢回复」，
   不写「走路是免费的，而且还在回。这是整套规则的地基」。
4. 事物用它的名字。写「体力」，不写「那一圈」。
5. 不打比方，不用文学化的词。「那一口气」「心跳」「白嫖」「算命」这类不用。
6. 不用破折号。转折写「但」，补充另起一句。
7. 正文不加粗。术语第一次出现可以加粗一次。
8. 机制构成那一节只写规则，不写理由和评论。「这是故意的」「否则会怎样」
   「没有任何地方会报错」这类话放第 5 节，或者不写。
9. 一段不超过四行，一段只说一件事。
10. 同一件事只写一次。

写完挑一段读出来。读着像跟同事说话就对了，像在演讲就重写。

### 标题怎么写

编号是硬的。2026-09-14 用户原话：

> 所有读本中的标题前都要加 1234 的序号，方便我定位一共有多少条、读到了多少条。

- 三级标题带序号：`### 2. 机制构成`。四级标题跟父节号：`#### 2.3 见底的时候`。
- 从 1 连排，不跳号，不重号。删掉一节就把后面的重排。
- 四级标题写清这一小节讲的是哪种情况，短。写 `#### 2.3 见底的时候`，
  不写 `#### 2.3 圈见底那一瞬间人就脱手`。
- 读本里不用 `##`。GDD 正文用 `##`，读本里再用会让客户端的目录多一层空壳。
- 正文引用别的节只写「见第 5 节」，不写「见 5.2」。读本会被重排，精确引用重排后是悬空的。

写完回头核一遍连号，这一步不许省。编号写在标题文字里，改结构时没有任何东西会提醒你重排。
漏排一个不报错，而症状正好是「目录里数不出总数」，也就是编号本来要解决的那个问题。

### 三条硬规矩

**一、正文里不许出现标识符。** 系统编号、类名、函数名、文件路径、代号、本篇之外没解释过的术语，
一个都不许有。

> 例外是第 7 节「名词对照」，那一节就是用来放真名的。
> 这条豁免是 2026-09-14 加的。读者是要跟这个系统对接的开发者，
> 他读完回到代码里看见真名却对不上号，这篇读本对他就白写了。
> 分界线是正文用白话、对照表给真名。正文一旦直接用真名，豁免就被滥用了。

**二、不许写具体数值和公式。** 写「买通一个 AI 的价钱随着关卡推进变少」，
不写「叛价 = 合作余利 × 0.6」。

> 这条防的是走散，不是嫌数字难读。同一个数在读本和规则表各写一遍，
> 改了其中一处不会有任何地方报错，而下游会照着过期的那份做下去。数值只有规则表那一份。
> 这条没有例外，名词对照也不行。想做数字速查就写第 8 节「旋钮」：
> 旋钮叫什么、管什么、调大调小会怎样，末尾一句「具体数值见规则表」。

**三、不许省。** 「详见下文」「具体规则见 Detailed Rules」这类句子在读本里是失败信号，
读本的读者正是那个不会往下翻的人。唯一的例外是「具体数值见规则表」。

### 排版

- **并列的几种情况写成列表。** 同一个句式重复三次以上，或者句子里数了数
  （「有三种失败」「分四步」），那几项就该看得见。
  「因为 A 所以 B，于是 C」这种因果链不是列表，那是一段话。
- **一节超过十段就用四级标题分小节**，按玩家在做什么分，不按代码模块分。
  客户端的目录认到四级，分了小节读的人才跳得过来。
- **矩阵、对照、参数表用表格**，不要用图硬画。
- **围栏外面不许写 HTML**，包括直接写进正文的 `<svg>`。客户端故意不装 `rehype-raw`，
  写了会被转义成一屏尖括号，不报错，就是没法读。

### 图：读本必须有

**判据：读者只扫标题和图，就该知道这个系统大致怎么转。**

> 这条 2026-09-16 从「该画就画」改成「必须有」。原来那句是建议，
> 结果是读本一张图都没有，而用户在客户端里读完第一句话就是「但是没有图」。
> **一句建议和一条硬规矩，在这儿的区别是零张图和一张图。**

**下面三种情况必须画，一个都不许省：**

1. **系统有状态**（此刻处于哪一档：在减 / 在回 / 见底 / 用不了）→ 画一张流转图
2. **一件事有几种去向**（见底那一刻，在爬的松手、在滑的收伞、在跑的变走）→ 画一张分支图
3. **讲位置、朝向、怎么接上** → 画 ```svg 图解

资源变化、动作结果、前后对照和空间布局优先用 `svg` 图解，画出体力条、角色动作或其他实际对象。
状态和分支可以画成 SVG 分镜；复杂关系和调用时序可用 Mermaid。
SVG 不限于空间图，也不要把文字框和箭头换成 SVG 就当作改善。
构图示例、绘图词表和兼容限制在 `docs/diagrams.md`。

**图要好看、易懂，文字仍需完整。** 保留条件、例外和解释，不以少字或固定图数为目标。
前后画面使用一致尺度和参照物，变化有标签，不能只靠颜色辨认。
示意比例不能冒充设计数值；图中规则必须能在 GDD 找到依据。

**Lite 文档同样要画。** 五节里 `机制构成` 该有的那张图，不会因为档位低就不需要。

**一张图要讲一个变化或者一组对比，不是罗列。** 动笔前先答一句
「这张图要让读者看出什么差别」，答不上来就别画，写一句话更省事。

> ⚠ **画出来了不等于画对了。** 2026-09-15 实测：一篇重写过的读本里，
> 唯一那张图解是四个空方框，用户的反应是「并没有更好看的那种图」。
> 并排的几格里每一格都要有参照物，不然就是罗列。

**图放在它讲的那一节里**，不要集中堆在开头。

**图里不写颜色，不写数值。** 上色用绘图词表里的名字，mermaid 写 `class C ok`，
图解写 `class="box ok"`。写死的色值客户端一律拿掉并提示 ——
一个浅绿在深色档下就是浅底浅字。

### 它跟别的几节的关系

| 哪一份 | 是什么 | 谁说的 |
|---|---|---|
| `design/digest/<同名>.md` | 白话，不带数值，给不做这块的人 | 我们写给读者的 |
| `## 设计前提` | 用户当初确认的原话，一个字不许编辑 | 用户说的 |
| Detailed Rules / Formulas 那几节 | 精确、可判定、带数值，给实现和 QA | 给实现和 QA 的 |

读本说发生什么，契约说精确到什么程度。

### 还差很多篇

这条规则 2026-09-07 才立，现存文档大多还没有读本。它们要等下次修订，
或者专门跑一次 `/reverse-document` 才补得上。客户端没有读本时明说这一篇还没有，不假装。

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

- MUST contain these 6 sections: Detailed Rules, Formulas, Edge Cases,
  Dependencies, Tuning Knobs, Acceptance Criteria
- **`Overview` 和 `Player Fantasy` 并进读本了**（2026-09-07；读本 2026-09-14 搬去了
  `design/digest/`，见「读本怎么写」那一节）。
  读本的第 1 段和第 2 段说的正是这两件事 —— 留着的话同一个系统会被写两遍，
  而**两处说法走散时不会有任何地方报错**，正是这份规则刚在
  「不许写具体数值」那条里警告的东西。
  这六节是**契约**：精确、可判定、带数值
- Formulas must include variable definitions, expected value ranges, and example
  calculations — but the formula *shape* and safe ranges only; the concrete values
  live in data files
- Edge cases must explicitly state what happens, not just "handle gracefully"
- Dependencies must be bidirectional — if system A depends on B, B's doc must mention A
- Tuning knobs must specify safe ranges and what gameplay aspect they affect
- Balance values must link to their source formula or rationale
