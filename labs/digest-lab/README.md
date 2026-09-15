# 读本实验室 —— 开发人员在客户端里看读本，能不能一下子懂，好不好看

拿一个凭空捏的小游戏（《山脊》：翻山送信，四个系统），反复让 harness 写同一个「体力」系统的读本。
每次只改一个变量，**评判只有一条：开发人员在客户端里打开读本，能不能一下子懂这个系统、看着舒不舒服。**
GDD 准不准、读本有没有讲错，这轮不管（那一半的材料收在 `later/`）。

方案正本在 `XGameHarnessUI/docs/DIGEST-LAB-PLAN.md`。操作只有一份：`brief/RUN.md`。

## 目录

```
brief/RUN.md         一次跑怎么做，基线和 V1 都在里面
brief/P1-design-system.md   贴进客户端的那一行
brief/answers.md     它问问题时怎么答
brief/premise.md     体力系统的设计前提（它写的前提跟这段对不上时贴回去）
fixtures/            实验项目的固定输入，生成器每次原样铺出来
make-project.mjs     铺实验项目；--view 回看某一次
collect.mjs          跑完一次收产物 + 客户端截图 + 一张看法卡
runs/<run-id>/       每次的产物：gdd.md · digest.md · shots/ · 看法.md
RUNLOG.md            一行一次
later/               这轮不用的：答题、评审、单独写读本
```

## 贴的是内容，不是文件名

`brief/P1-design-system.md` 里那个代码块的那一行，复制，粘贴进客户端输入框，回车。
这个仓客户端里的 agent 看不到，贴文件名它只会问你这是什么。

## 一次跑（`brief/RUN.md` 是完整版）

```
node labs/digest-lab/make-project.mjs D:\work\GameStudio\RichLethe-lab       # 铺项目
# 客户端本地模式打开它 → 药丸选引擎 → + 开新对话 → 贴 P1 那一行 → 按 answers 点卡
# 看板 → GDD → 体力 → 读本：让开发人员看，填 runs/<run-id>/看法.md
node labs/digest-lab/collect.mjs <run-id> --project D:\work\GameStudio\RichLethe-lab --shots   # 收
# RUNLOG.md 加一行
```

## 评判怎么填（`看法.md`，collect 会生成模板）

三个分，1 到 5，外加两句话。填的人是**看的那个开发人员**，不是跑的人。

| 分 | 问的是 |
|---|---|
| 一眼懂 | 读完前三节，知不知道这东西是干什么的、跟自己有什么关系 |
| 读得下去 | 有没有哪一节是一堵墙，读到一半想放弃 |
| 好看 | 目录、编号、图、表，看着舒不舒服 |

两句话：**最好的一节是哪节、为什么**；**最差的一节是哪节、为什么**。
