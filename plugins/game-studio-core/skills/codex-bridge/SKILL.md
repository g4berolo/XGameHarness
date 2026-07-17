---
name: codex-bridge
description: "调用本地 Codex CLI（headless exec）完成 Claude 不具备的能力，最典型是 gpt-image-2 生图（走 ChatGPT 订阅额度，无需 OPENAI_API_KEY）。触发场景：用户说'让 codex / 调 codex / codex 生图 / imagegen / 生成图片素材'，或任务需要把子问题委托给本地 codex 拿结果。"
argument-hint: "[任务描述或生图提示词]"
user-invocable: true
allowed-tools: Bash, Read, Glob
---

# /codex-bridge — 本地 Codex 桥接

把任务委托给本机 Codex CLI（`codex exec` 非交互模式）并取回结果。封装脚本：
`${CLAUDE_PLUGIN_ROOT}/skills/codex-bridge/scripts/run_codex.py`

## 两种模式

### ① 生图模式（主场景）

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/codex-bridge/scripts/run_codex.py" \
  --imagegen "<目标PNG绝对路径>" \
  --prompt "<生图提示词，无需自带 $imagegen 前缀>" \
  [--image <参考图绝对路径>]... [--timeout 900]
```

- 脚本自动给 prompt 加 `$imagegen` 前缀 + "把最终图保存到目标路径"契约。
- 结束后校验目标 PNG；若 codex 只落在 `~/.codex/generated_images/`，脚本兜底把
  本次运行期间新产出的最新图复制到目标路径并在报告中注明。
- 生图走用户 ChatGPT 订阅额度（与 Codex Desktop 共享），不消耗付费 API。
- 提示词规范（游戏 UI 素材场景）沿用项目 `art/style-guide/asset-standards.md` §6
  色键(chroma key)口径：纯色底、无文字、素材彼此分离。

### ② 通用委托模式

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/codex-bridge/scripts/run_codex.py" \
  --prompt "<任务>" [--workdir <目录>] [--sandbox read-only|workspace-write] \
  [--image <图>]... [--resume-last]
```

- `--resume-last` 续接上一个 codex 会话（多轮追问）。
- 结果 = codex 最终回复文本，脚本直接打印（内部经 `-o` 文件中转，天然规避
  Windows Bash 输出捕获 bug；若本机 Bash 有该 bug，外层照常用 `> 文件 2>&1` + Read）。

## 执行要点

1. **超时**：生图单张建议 `--timeout 900`；文本任务默认 600s 够用。
2. **workdir**：默认当前目录。项目仓库若含 `.codex/config.toml`，须与本机 codex
   版本兼容（字段失效会导致启动即失败，用 `codex doctor` 排查）。
3. **失败路径**：脚本非零退出时读它打印的诊断（常见：未登录 → 让用户开
   Codex Desktop 登录；额度尽；超时 → 加大 --timeout 或简化任务）。
4. **额度尊重**：批量生图前先跟用户确认张数；单张试错通过再放量。
5. 二进制自动发现（Desktop 更新换 hash 目录也能找到）；找不到时提示用户装
   Codex Desktop 或设 `CODEX_CLI_PATH` 环境变量。
