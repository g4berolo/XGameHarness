# 一次跑 —— 基线 B0 和 V1 都照这份

| | B0（基线） | V1 |
|---|---|---|
| 引擎 | Claude | Codex |
| 跑几次 | 3 | 2，**B0 跑完再跑** |
| run-id | `r01-B0-claude-0916a` `r02-…b` `r03-…c` | `r04-V1-codex-0916a` `r05-…b` |

每次约一小时，大半是等它写。**中途不即兴** —— 它写得不好正是要看的。

## 1. 铺项目

```
cd D:\work\GameStudio\XGameHarness
node labs/digest-lab/make-project.mjs D:\work\GameStudio\RichLethe-lab
```

输出里的短 SHA 记下来（RUNLOG「技能版本」那格）。
不是第一次跑：先在客户端左栏把开着的对话关掉（×），铺完点顶栏项目名 → 换项目 → 重新打开这个目录。

## 2. 客户端（只在第一次跑做）

- 左下角齿轮 → 设置 → 「工作室服务器」→ **换服务器** → 最底下 **不接服务器，本地使用** → **确定** →
  开场屏 **浏览…** 选 `D:\work\GameStudio\RichLethe-lab` → **打开**
- 设置 → 「我的改动怎么发给大家」→ **我自己按**

## 3. 引擎

顶栏写着模型名的药丸 → 点开 → 选 **Claude**（B0）或 **Codex**（V1）。先切引擎再开对话。
V1 时 Codex 显示「没装」或「起不来」先解决（`npm i -g @openai/codex`，账号浮层里登录一次）。

## 4. 让它写

左栏 **+ 开新对话**，贴这一行，回车：

```
/game-studio-core:design-system 体力（文件名用 stamina.md）
```

之后只按 `answers.md` 答：

- 它弹「想问几个问题」的卡：前提对得上选「就这么写」，建议 Lite 选「前提对，但档位改成 Full」，
  各节选它推荐的；要开子 agent 答「不用，你自己写」；问评审选「I'll review it myself first」；最后「Stop here」
- 审批卡（它要写文件）：**批准**，嫌多点 **批准，本次对话不再问**
- **V1**：Codex 不弹问询卡，它把问题写在回复里，你照上面那些话打字答。它不认斜杠命令的话改贴
  `用 game-studio-core 的 design-system 技能给「体力」写 GDD，文件名用 stamina.md`，并记进看法卡

写完确认 `RichLethe-lab\design\digest\stamina.md` 在。

## 5. 看 —— 这一步才是判据

看板 → **GDD** → 点「体力」。打开默认停在 **读本**。
**让开发人员看**（不是跑的人自己看）。看完填三个分和两句话（第 6 步生成的 `看法.md`）。
看的时候顺手 Win+Shift+S 截两三张自己觉得好或差的地方。

## 6. 收

```
node labs/digest-lab/collect.mjs <run-id> --project D:\work\GameStudio\RichLethe-lab --shots
```

`runs/<run-id>/` 里会有 GDD、读本、客户端深浅两档截图、一张 `看法.md` 模板。把分和两句话填进去。
（`--shots` 要 UI 仓的 `app/dist` 在；没有先在 `XGameHarnessUI` 里 `cd app; node node_modules/vite/bin/vite.js build`。）

## 7. RUNLOG 一行

`RUNLOG.md` 按表头加一行：三个分、最好 / 最差的一节、一句话。

## 回看旧的一次

```
node labs/digest-lab/make-project.mjs D:\work\GameStudio\RichLethe-lab-view --view labs/digest-lab/runs/<run-id>
```

客户端换项目打开 `RichLethe-lab-view`，看板 → GDD → 体力。

## 五次都跑完

设置 → 「工作室服务器」→ **连一台服务器** → `http://124.222.151.22` → 登录回 RichLethe。
