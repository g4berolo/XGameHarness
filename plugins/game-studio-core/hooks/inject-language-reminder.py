#!/usr/bin/env python3
"""
UserPromptSubmit hook: inject R2 language self-check reminder.

Each time the user submits a prompt, this hook outputs a concise R2 cheat
sheet into the conversation context via hookSpecificOutput.additionalContext.
This complements the CLAUDE.md top "⚠ R2 输出语言协议" section by giving
the agent a fresh in-context reminder right before composing a response.

Token cost ~200 tokens per prompt. See .claude/docs/agent-process-rules.md
§ R2 for the full rule set and rationale.
"""
from __future__ import annotations

import io
import json
import sys

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REMINDER = """=== R2 输出语言自检（每次回复发送前必扫）===

默认中文输出。发送前 2 秒扫描所有英文 token：

1. **专业名词** 首次出现 → "中文(英文)" 注解，后续段落可只用英文。
   高频：Component / Subsystem / Blueprint / Decal / Shading Model / Material Domain / material master / material instance / Subsurface Scattering (SSS) / Subsurface Profile / Lumen / Niagara / Nanite / PBR / trim sheet / vertex color / curvature / edge wear / roughness / emissive / translucency / opacity / Fresnel / wrap diffuse / normal / specular / bloom / bake / mask

2. **状态形容词 / 概念词** → "中文(英文)" 注解形式。
   高频：staged / untracked / stale / pending / blocked / raw / blob / pointer / forward-only / fresh clone / working tree / quota / gap / session / hook / over-engineering / blocker / trade-off

3. **普通操作动词** → 中文为主，括号 optional 注英文。
   高频：commit / push / pull / merge / rebase / stash / diff / stage / checkout / clone / fetch / build / compile / save / load / spawn / trigger
   **反例**："跑 commit" / "Compile + Save" / "走 push"

4. **原文保留**（不要翻译，不要注解）：
   路径 / 类名 / API 签名 / 任务 ID / commit hash / 文件扩展名 / 模型名 / UE Editor UI label / BP 节点名
   例：`client/Source/...` / `ARoomBase` / `PP-E3` / `2ec44da` / `*.uasset` / `M_StoneUnderworld_Master` / `Get Subsystem` / `Details` 面板

**违规自检**：扫每个英文 token，问"是路径/类名/API/任务ID/UE 内置概念吗？" 否 → "首次出现注解了吗？" 否 → 修。

**被用户指出违规时**：立即承认 + 重写违规段 + 不辩解。

**不在自检范围**：commit message / PR title / 资产文件名 / 日志原文 — 按既有惯例保持英文。

完整规则 + 反例 + 触发历史见 CLAUDE.md 顶部 ⚠ R2 段 + .claude/docs/agent-process-rules.md § R2。"""


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
