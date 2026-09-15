# 读本实验室 —— 控制变量调 `/design-system` `/write-digest` 和几个子 agent

拿一个凭空捏的小游戏（《山脊》：翻山送信，四个系统），反复让 harness 写同一个「体力」系统的
GDD 和读本。每次只改一个变量，用一把不花钱的尺子、客户端截图和二十道固定题量产出。
**全流程走客户端** —— 跑的人就是一个用客户端做开发的策划，脚本只负责铺项目、收产物、量。

方案正本在 `XGameHarnessUI/docs/DIGEST-LAB-PLAN.md`，这里只放操作。

## 目录

```
fixtures/            实验项目的固定输入（假游戏概念 · 四行系统索引 · 两篇 Lite 夹具 · 一份 ADR · 项目配置）
brief/               设计前提 · 每张问询卡怎么答 · 四份提示词（P1 写 GDD · P2 单独写读本 · P3 评审 · P4 答题）
qa/                  二十道题（questions.md 进答题项目）· 答案（key.md 只给批卷的人）
make-project.mjs     铺实验项目 / 答题项目，重跑 = 重置
lint.mjs             尺子：红（硬规矩）· 黄（要人判）· 数字
collect.mjs          跑完一次收产物 + 跑尺子 + 客户端截图
runs/<run-id>/       每次的产物
RUNLOG.md            一行一次。没写进去的跑等于没跑
```

## 先说清一件事：贴内容，不是贴文件名

`brief/` 里的四份提示词**在 harness 仓里**，客户端里那个 agent 看不到这个仓。
每份文件里那个代码块就是要贴进输入框的东西 —— **复制代码块里的那一行（或那一段），
粘贴到客户端输入框，回车**。贴 `brief/P1-design-system.md` 这几个字，模型只会问你「这是什么」。

斜杠命令要**独占一行、放在开头**；输入框里回车就是发送，Shift+Enter 才换行。
所以 P1 / P2 / P3 都做成了一行，P4 是普通多行文本，粘贴时换行会保留。

## 只做一次的准备

1. 三个仓并排：`D:\work\GameStudio\XGameHarness`（这个）、`…\XGameHarnessUI`（客户端）、
   实验项目会生成在 `D:\work\GameStudio\RichLethe-lab`
2. 截图要用客户端的产物：在 `XGameHarnessUI` 里 `cd app; node node_modules/vite/bin/vite.js build` 一次
   （客户端代码没变就不用再构建）
3. 装着的客户端要 ≥ 1.0.15（左栏能开多个对话的那版）

## 一次跑 —— 逐步

跑一次大约一小时，其中等模型写的时间占大半。**中途不即兴**，它做错了正是要量的东西。

### 第 1 步 铺项目

```
cd D:\work\GameStudio\XGameHarness
node labs/digest-lab/make-project.mjs D:\work\GameStudio\RichLethe-lab
```

看到「实验项目已铺好」和 harness 的短 SHA。**每次跑之前都重铺**，哪怕上一次只跑了一半。

### 第 2 步 客户端切到本地模式，打开实验项目

只在第一次和最后一次切，中间几次跑不用动。

1. 左下角齿轮 → 设置 → 「工作室服务器」那一段 → **换服务器**
2. 那一屏最底下 → **不接服务器，本地使用** → **确定，用本地模式**
3. 开场那一屏变成「指一个目录」：点 **浏览…** 选 `D:\work\GameStudio\RichLethe-lab`，
   或者把这个路径贴进输入框 → **打开**

看板左栏应该看得到「GDD 2 篇」（角色移动、攀爬与滑翔）。

### 第 3 步 设置两处

- 设置 → 「我的改动怎么发给大家」→ **我自己按**（本地 git 没远端，不关的话顶栏每次都报推不上去）
- 顶栏那个写着模型名的药丸 → 点开 → 选引擎：B0 是 **Claude**，V1 是 **Codex**。模型名记进 notes

### 第 4 步 新开对话，贴 P1

1. 左栏 **+ 开新对话**
2. 打开 `brief/P1-design-system.md`，复制代码块里那一行：
   ```
   /game-studio-core:design-system 体力（文件名用 stamina.md）
   ```
3. 粘贴进输入框，回车

### 第 5 步 按 `brief/answers.md` 点卡

跑的过程中会弹两种卡，都在对话面中间：

- **「Claude 想问几个问题」**（顶上写着「需要你定」）：每题是单选或多选，最下面有一个自填框。
  按 `answers.md` 那张表选；它推荐了哪个就选哪个，没推荐就选第一个。选完点底下那个主按钮
- **审批卡**（它要写 / 改文件）：点 **批准**。嫌点得多就点 **批准，本次对话不再问** ——
  只在这次对话里记住，不写进任何配置

它每一步选了什么、第一版前提写了什么、建议了哪个档位，**当场记进 `runs/<run-id>/notes.md`**
（目录还没有就先记在别处，第 8 步 collect 会建）。跑完再回忆记不准。

它说「GDD Complete」并问下一步时选 **Stop here**。
在资源管理器里确认两个文件都在：`RichLethe-lab\design\gdd\stamina.md`、`RichLethe-lab\design\digest\stamina.md`。

### 第 6 步（只有 V3 那一组做）删读本，单独重写

在资源管理器里删掉 `design\digest\stamina.md` → 左栏 **+ 开新对话** → 贴 `brief/P2-write-digest.md` 里那一行。

### 第 7 步 评审

左栏 **+ 开新对话** → 贴 `brief/P3-design-review.md` 里那一行。等它输出整段评审，
在转录里拖选复制，存到 `runs/<run-id>/review.md`（第 8 步 collect 之后再存也行）。

### 第 8 步 在看板里看，截图，记读数

1. 左栏 **看板** → **GDD** → 点「体力」那一行。打开默认停在 **读本**
2. 看：左边目录能不能认到四级、编号连不连；正文里的图画没画出来；顶上有没有「这份读本写在文档上次改动之前」
   之类的提示（**不该有**）；切到 **文档** 看 GDD
3. Win+Shift+S 截几张，存到 `runs/<run-id>/shots/manual/`
4. 切回对话面，右下状态栏那格 `$…` 是这次对话的累计花费，记进 notes；Codex 不显示，只记时间

### 第 9 步 收产物 + 尺子 + 客户端截图

```
node labs/digest-lab/collect.mjs r01-B0-claude-main-0916a --project D:\work\GameStudio\RichLethe-lab --shots
```

run-id 的写法：`r<两位序号>-<组>-<引擎>-<执笔>-<月日><字母>`。
它会收 GDD、读本、跑完后的系统索引、session-state，跑尺子（`lint.txt` / `lint.json`），
再用客户端的 `docshot.mjs` 深浅两档各截一轮（`shots/dark` `shots/light`，每档约一分钟）。
末尾印一行 RUNLOG 的骨架。

### 第 10 步 答题（两个项目，各一个对话）

```
node labs/digest-lab/make-project.mjs D:\work\GameStudio\RichLethe-lab-qa --qa labs/digest-lab/runs/r01-B0-claude-main-0916a
```

1. 客户端：点顶栏的项目名 → 换项目 → 开场屏打开 `D:\work\GameStudio\RichLethe-lab-qa`
2. **+ 开新对话** → 贴 `brief/P4-qa.md` 里那一段（多行，粘贴会保留换行）→ 回车
3. 答完整段复制到 `runs/<run-id>/qa.md`
4. 对照组：再铺一次加 `--mode gdd`（同一个目录，它会先删再建）→ 客户端换项目重新打开 →
   再贴一次 P4（第一句改成读 `design/gdd/stamina.md`）→ 存 `qa-gdd.md`
5. 打开 `qa/key.md` 批：前 12 题对固定答案，后 8 题对着这次的 `gdd.md` 批。
   数三个数：讲错几题 / 「读本没说」几题 / 后 8 题得几分

### 第 11 步 RUNLOG 加一行

把第 9 步印的那行骨架拷进 `RUNLOG.md`，填上问答三个数、评审 verdict、花费和时间，
以及**你在客户端里读完读本的那一句话** —— 这一格不许空。

### 第 12 步 收工换回服务器

设置 → 「工作室服务器」→ **连一台服务器** → 填 `http://124.222.151.22` → 连接 → 登录 → 回 RichLethe。

## 变量（一次只动一个）

| 组 | 动什么 | 次数 | 跟基线比多做什么 |
|---|---|---|---|
| B0 | 基线：Claude · 主 agent 自己写 · 当前技能 · 读本走 `/design-system` 内嵌那条路 | 3 | — |
| V1 | 引擎换 Codex | 2 | 第 3 步选 Codex；P1 认不认斜杠命令记进 notes |
| V2 | 交给 `systems-designer` / `game-designer` Author 模式写 | 各 2 | 第 4 步贴 P1 里 V2 那一行；它要开子 agent 时答「开」 |
| V3 | 拿 B0 的 GDD，删读本，单独 `/write-digest` | 3 | 做第 6 步 |
| V4 | 每改一次技能，按 B0 重跑 | 每次 2 | 第 1 步重铺时会带上当前 harness 的 rules；RUNLOG 记短 SHA |

## 尺子借了客户端两样东西

- 「读本旧没旧」的判据是 `XGameHarnessUI/sidecar/src/board.mjs` 的 `readGddDoc`，不另写
- mermaid 里写死的颜色数用 `app/src/lib/drawing.ts` 的 `stripMermaidColors`

UI 仓默认在 `../XGameHarnessUI`，不在就 `--ui <目录>`；借不到会退回自己的简陋解析并在输出里说一声。

## 不做的

- 不动 RichLethe 真项目；不修「客户端里写的 GDD 进不了文档仓」那个洞
- 不做自动批卷；不比模型
