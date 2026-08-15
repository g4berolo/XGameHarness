#!/usr/bin/env python3
"""
UserPromptSubmit hook: inject the R2 language self-check trigger.

Fires on every prompt, so it carries only the trigger and the decision
procedure — roughly 150 tokens. The full R2 rule set (per-word-class tables,
worked counter-examples, trigger history) is injected once per session by
session-start.sh from docs/agent-process-rules.md § R2, and does not need
restating each turn.

Sizing matters here: this text is charged once per user turn for the whole
session. The previous full-table version measured ~900 tokens/turn — about
45k tokens across a 50-turn session, spent re-teaching a rule the model had
already received twice (SessionStart § R2, and the project CLAUDE.md).
Keep this block short; put new rule detail in agent-process-rules.md § R2.
"""
from __future__ import annotations

import io
import json
import sys

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REMINDER = """=== R2 输出语言自检（发送前扫一遍）===

默认中文输出。对回复里每个英文 token 走一次判定：

1. 是路径 / 类名 / API 签名 / 任务 ID / commit hash / 文件扩展名 / 模型名 /
   引擎编辑器界面标签吗 → 原文保留，不翻译不注解。
2. 否则是首次出现吗 → 写成「中文(English)」；后续段落可只用英文。
3. 是可以直接用中文说的普通动词吗（提交 / 推送 / 合并 / 构建…）→ 用中文。
   反例："跑 commit" / "走 push" / "Compile + Save"。

不在自检范围：commit message / PR 标题 / 资产文件名 / 日志原文，保持英文。
被用户指出违规时：承认 + 重写违规段 + 不辩解。

完整词表、反例与触发历史已在本 session 开头随 agent-process-rules.md § R2 注入。"""


def main() -> int:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": REMINDER,
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
