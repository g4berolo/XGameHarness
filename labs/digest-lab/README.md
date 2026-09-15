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

## 一次跑（照着做，不即兴）

```
# 0. 重置实验项目（目录里有 .digest-lab 标记才会被删，别的目录它不碰）
node labs/digest-lab/make-project.mjs D:\work\GameStudio\RichLethe-lab

# 1. 客户端：换项目 → 「不接服务器，本地使用」→ 选 RichLethe-lab
#    设置里把「自动发」关掉；选引擎；新开一个对话
# 2. 贴 brief/P1-design-system.md，问询卡按 brief/answers.md 点；它选了什么记进 notes.md
# 3. （V3 才做）删掉 design/digest/stamina.md，新开对话贴 brief/P2-write-digest.md
# 4. 新开对话贴 brief/P3-design-review.md，输出整段拷到 runs/<run-id>/review.md
# 5. 看板里打开「体力」：读本 / 文档开关、目录、图、顶上的提示。截图留着

# 6. 收产物 + 尺子 + 客户端截图（--shots 要 UI 仓先构建过：cd app; node node_modules/vite/bin/vite.js build）
node labs/digest-lab/collect.mjs r01-B0-claude-main-0916a --project D:\work\GameStudio\RichLethe-lab --shots

# 7. 答题：只有读本的项目 + 只有 GDD 的对照项目，各开一个对话贴 brief/P4-qa.md，按 qa/key.md 批
node labs/digest-lab/make-project.mjs D:\work\GameStudio\RichLethe-lab-qa --qa labs/digest-lab/runs/r01-B0-claude-main-0916a
node labs/digest-lab/make-project.mjs D:\work\GameStudio\RichLethe-lab-qa --qa labs/digest-lab/runs/r01-B0-claude-main-0916a --mode gdd

# 8. RUNLOG.md 加一行（collect 末尾印了骨架）
```

跑完实验记得把客户端换回服务器（设置 → 换服务器 → 填地址登录）。

## 变量（一次只动一个）

| 组 | 动什么 | 次数 |
|---|---|---|
| B0 | 基线：Claude · 主 agent 自己写 · 当前技能 · 读本走 `/design-system` 内嵌那条路 | 3 |
| V1 | 引擎换 Codex | 2 |
| V2 | 交给 `systems-designer` / `game-designer` Author 模式写 | 各 2 |
| V3 | 拿 B0 的 GDD，删读本，单独 `/write-digest` | 3 |
| V4 | 每改一次技能，按 B0 重跑 | 每次 2 |

## 尺子借了客户端两样东西

- 「读本旧没旧」的判据是 `XGameHarnessUI/sidecar/src/board.mjs` 的 `readGddDoc`，不另写
- mermaid 里写死的颜色数用 `app/src/lib/drawing.ts` 的 `stripMermaidColors`

UI 仓默认在 `../XGameHarnessUI`，不在就 `--ui <目录>`；借不到会退回自己的简陋解析并在输出里说一声。

## 不做的

- 不动 RichLethe 真项目；不修「客户端里写的 GDD 进不了文档仓」那个洞
- 不做自动批卷；不比模型
