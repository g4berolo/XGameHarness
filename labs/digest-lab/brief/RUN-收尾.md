# 收尾 —— 把一次跑的产物收回来、答题、批卷、看、记

每次跑完都做，B0 和 V1 一样。约三十分钟，其中答题两段对话各几分钟。

## 一、收产物 + 尺子 + 客户端截图

```
cd D:\work\GameStudio\XGameHarness
node labs/digest-lab/collect.mjs <run-id> --project D:\work\GameStudio\RichLethe-lab --shots
```

（`--shots` 要 UI 仓的 `app/dist` 在；没有的话先在 `XGameHarnessUI` 里
`cd app; node node_modules/vite/bin/vite.js build` 一次。）

跑完 `labs/digest-lab/runs/<run-id>/` 里有：

| 文件 | 是什么 |
|---|---|
| `gdd.md` `digest.md` | 这次写出来的 GDD 和读本 |
| `systems-index.md` | 跑完之后的系统索引（看它改没改「体力」那行） |
| `session-state-zhouxinyu.md` | 它写的会话状态 |
| `lint.txt` `lint.json` | 尺子：红 / 黄 / 数字 |
| `shots/dark/` `shots/light/` | 客户端深浅两档的截图；`dark.txt` `light.txt` 说每张图画没画出来、读本有没有提示 |
| `notes.md` | 模板，你来填 |

末尾印一行 RUNLOG 的骨架，红黄和图数已经填好。

然后手动放两样东西进去：

- `review.md`：评审那段对话的原文（第五步复制的那段）
- `notes.md`：变量、它选了什么、花费和时间、你读完读本的一句话

## 二、答题 —— 两段对话，都用 Claude

### 只读读本那组

```
node labs/digest-lab/make-project.mjs D:\work\GameStudio\RichLethe-lab-qa --qa labs/digest-lab/runs/<run-id>
```

1. 客户端：点顶栏项目名 → 换项目 → 开场屏 **浏览…** 选 `D:\work\GameStudio\RichLethe-lab-qa` → **打开**
2. 顶栏药丸确认引擎是 **Claude**（V1 那组这时要切回来）
3. 左栏 **+ 开新对话**，贴 `P4-qa.md` 里那一段（多行，粘贴保留换行），回车
4. 它答完，整段复制，存到 `runs/<run-id>/qa.md`

### 只读 GDD 那组（对照）

```
node labs/digest-lab/make-project.mjs D:\work\GameStudio\RichLethe-lab-qa --qa labs/digest-lab/runs/<run-id> --mode gdd
```

1. 客户端：先把刚才那个对话关掉（左栏 ×），顶栏项目名 → 换项目 → 重新打开 `RichLethe-lab-qa`
   （目录重铺过，要重开一次）
2. **+ 开新对话**，贴 P4 那一段，**第一句里的 `design/digest/stamina.md` 改成 `design/gdd/stamina.md`**
3. 答完存到 `runs/<run-id>/qa-gdd.md`

## 三、批卷

打开 `qa/key.md`，对着 `qa.md` 批：

- 1–12 题对固定答案
- 13–20 题打开这次的 `gdd.md`，看读本讲的跟 GDD 对不对得上
- 每题记一个：**对 / 错 / 读本没说**。「读本没说」不算错，单独数

数出三个数，写成 `讲错 / 没说 / 后8题得分`，例 `1 / 3 / 6`。
再把 `qa-gdd.md` 同样批一遍 —— 读本那组的分不该比它低。

## 四、看

- **尺子**：`runs/<run-id>/lint.txt`。红是硬规矩，一条就是一条；黄要你判（数字那几条尤其是）
- **截图**：`shots/dark/` 和 `shots/light/` 逐张看。断言全绿也可能是四个空方框
- **原文**：`gdd.md` `digest.md`
- **在客户端里回看**（实验项目下次一重铺旧产物就没了，要看旧的用这条）：
  ```
  node labs/digest-lab/make-project.mjs D:\work\GameStudio\RichLethe-lab-view --view labs/digest-lab/runs/<run-id>
  ```
  客户端换项目打开 `RichLethe-lab-view` → 看板 → GDD → 体力。读本 / 文档两档都在

## 五、RUNLOG 加一行

把第一步印的骨架拷进 `RUNLOG.md`，填：问答三个数、评审 verdict（`review.md` 末尾那行）、
花费和时间（V1 花费写 `—`）、**你在客户端里读完读本的一句话**。这一格不许空。

## 六、下一次跑之前

- 客户端左栏把开着的对话全关掉
- 重铺 `RichLethe-lab`（`RUN-B0.md` 第一节），顶栏项目名 → 换项目 → 重新打开
- B0 三次 + V1 两次都跑完，再设置 → 「工作室服务器」→ **连一台服务器** → 填 `http://124.222.151.22` 登录回 RichLethe
