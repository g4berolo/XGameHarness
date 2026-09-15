# 跑基线 B0 —— Claude · 主 agent 自己写 · 当前技能 · 读本走 `/design-system` 内嵌那条路

跑 **3 次**，run-id：`r01-B0-claude-main-<月日>a`、`r02-B0-claude-main-<月日>b`、`r03-B0-claude-main-<月日>c`。
三次之间的差就是噪声下限，后面比它小的差异一律不算数。

每次约一小时。**中途不即兴** —— 它做错了正是要量的东西。跑完照 `RUN-收尾.md`。

## 一、铺项目（每次都做）

```
cd D:\work\GameStudio\XGameHarness
node labs/digest-lab/make-project.mjs D:\work\GameStudio\RichLethe-lab
```

看到「实验项目已铺好」和 harness 的短 SHA（写进 RUNLOG 的「技能版本」那格）。

**不是第一次跑的话**：先在客户端左栏把上一次开着的对话全关掉（每条右边的 ×），
再铺目录，再点顶栏项目名 → 换项目 → 重新打开 `RichLethe-lab`。重铺过的目录客户端要重开一次才认。

## 二、客户端（第一次跑才做的两步）

1. 切本地模式：左下角齿轮 → 设置 → 「工作室服务器」→ **换服务器** → 那一屏最底下
   **不接服务器，本地使用** → **确定，用本地模式** → 开场屏 **浏览…** 选 `D:\work\GameStudio\RichLethe-lab` → **打开**。
   看板左栏应有 2 篇 GDD（角色移动、攀爬与滑翔）
2. 设置 → 「我的改动怎么发给大家」→ **我自己按**

## 三、引擎

顶栏那个写着模型名的药丸 → 点开 → 引擎选 **Claude**。模型名和 effort 记进 notes（三次要一样）。

## 四、写 GDD

1. 左栏 **+ 开新对话**
2. 把这一行贴进输入框，回车（贴内容，不是文件名）：
   ```
   /game-studio-core:design-system 体力（文件名用 stamina.md）
   ```
3. 之后只做两件事：按 `answers.md` 点卡、把它选了什么记下来。
   - **「Claude 想问几个问题」**那种卡：它写的前提跟 `premise.md` 对得上就选「就这么写」；
     它建议 Lite 就选「前提对，但档位改成 Full」；每一节的问题选它推荐的那个，没推荐选第一个
   - **审批卡**（它要写文件）：**批准**。嫌多就 **批准，本次对话不再问**
   - 它要开子 agent：答「不用，你自己写」（B0 是主 agent 自己写）
   - 它问「现在跑 design-review 吗」：**I'll review it myself first**
   - 它问「更新系统索引」：可以；问「下一步」：**Stop here**
4. 记进 `notes.md`（目录还没有就先记在别处）：它第一版前提写了什么、建议了哪个档位、
   每节选了什么、它想开哪个子 agent、开始和结束时间
5. 资源管理器里确认两个文件都在：
   `RichLethe-lab\design\gdd\stamina.md`、`RichLethe-lab\design\digest\stamina.md`

## 五、评审

左栏 **+ 开新对话**，贴这一行：

```
/game-studio-core:design-review design/gdd/stamina.md（只报，不改任何文件）
```

等它输出整段评审。在转录里从「Design Review」拖选到「Verdict」，复制，先存在记事本里
（收尾时放进 `runs/<run-id>/review.md`）。

## 六、在客户端里看一眼

左栏 **看板** → **GDD** → 点「体力」。打开默认停在 **读本**。看四样：
左边目录能不能认到四级、编号连不连；图画没画出来；顶上有没有「这份读本写在文档上次改动之前」
那类提示（**不该有**）；切 **文档** 看 GDD。Win+Shift+S 截几张。

切回对话面，右下状态栏 `$…` 那格是写 GDD 那段对话的累计花费，记进 notes。

然后照 `RUN-收尾.md`。
