# 每一张问询卡怎么答 —— 固定脚本，跑的人不即兴

跑的人只做三件事：贴提示词、按这张表点卡、把它选了什么记进 `notes.md`。
**不给内容、不出主意、不纠正它。** 它写错了正是要量的东西。

| 技能问到 | 答 | 记什么 |
|---|---|---|
| 2f：前提 + 档位 | 它写的前提跟 `premise.md` 对得上 → 「就这么写」；对不上 → 把 `premise.md` 那段贴回去，选「前提要改」。它建议 Lite → 「前提对，但档位改成 Full」 | 它第一版前提写了什么、建议了哪个档位 |
| 「May I create the skeleton」 | 可以 | — |
| 每一节的问题 | 选它自己推荐的那个选项；没有推荐就选第一个。开放式问题回「按你的判断」 | 每节它选了什么 |
| 「Approve this section?」 | 通过 | — |
| 「May I write to …」 | 可以 | — |
| 三个可选节 | 「Just open questions」 | — |
| 「Run /design-review now?」 | 「I'll review it myself first」（P3 单独跑，读本先写完） | — |
| 「May I update the systems index」 | 可以 | — |
| 「What's next?」 | 「Stop here for this session」 | — |
| 它要开子 agent（V2 以外的组） | 「不用，你自己写」 | 它想开哪个 |
| 它要开子 agent（V2 那一组） | 「开，Author 模式，写 `design/gdd/stamina.md`」 | — |
| 任何别的问题 | 「按你的判断」 | 问了什么 |

## 只有两种情况允许跑的人说话

1. 它把文件写到了别的名字（不是 `stamina.md`）→ 说「文件名用 stamina.md」，并记进 notes
2. 它卡住超过五分钟没动静 → 记进 notes，这次作废，重跑
