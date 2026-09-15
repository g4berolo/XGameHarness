# P1 —— 写 GDD

**贴的是下面这一行的内容，不是这个文件的路径。** 这个文件在 harness 仓里，客户端里那个 agent 看不到它；
就算看得到，斜杠命令也得出现在输入框里才会被当成命令。

新开一个对话，把这一行贴进输入框，回车：

```
/game-studio-core:design-system 体力（文件名用 stamina.md）
```

写成一行：输入框里回车就是发送（Shift+Enter 才换行），而且斜杠命令要独占开头。

之后按 `answers.md` 点卡。

## V2 那一组（交给子 agent 写）

```
/game-studio-core:design-system 体力（文件名用 stamina.md；Detailed Design 起的各节交给 game-studio-core:systems-designer 以 Author 模式写）
```

`game-designer` 那一组把 agent 名换掉即可。

## V1 那一组（Codex）

照样贴第一行。Codex 认不认这条斜杠命令、它有没有去读 `rules/design-docs.md` 和 GDD 模板，
**本身就是 V1 要看的** —— 不认的话记进 notes，然后改贴：

```
用 game-studio-core 的 design-system 技能给「体力」写 GDD，文件名用 stamina.md
```
