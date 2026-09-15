# P4 —— 只读读本答题（在 `RichLethe-lab-qa` 那个项目里新开一个对话，贴下面整段的内容）

那个项目里只有一个文件可读，它想读别的也读不到。**这是判据的一部分，不是巧合。**

整段贴进输入框（换行用 Shift+Enter，或者直接从这里复制多行文本粘贴，粘贴会保留换行），回车：

```
读 design/digest/stamina.md，然后回答 qa/questions.md 里的全部问题。
规矩：每题先写答案，再写依据（引读本里的哪一节、哪一句）；读本里没说的写「读本没说」，不许猜，不许用常识补；不要读别的文件，也不要问我。
```

**对照组**（`--mode gdd` 生成的项目）把第一句里的 `design/digest/stamina.md` 换成 `design/gdd/stamina.md`，其余一样。

答完把整段复制到 `runs/<run-id>/qa.md`（对照组存 `qa-gdd.md`），按 `qa/key.md` 批。
