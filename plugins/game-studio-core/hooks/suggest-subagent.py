#!/usr/bin/env python3
"""
UserPromptSubmit hook: suggest a relevant specialist subagent by keyword.

Claude Code does NOT auto-spawn subagents — the developer must explicitly name
the agent type (see .claude/docs/agent-process-rules.md § R4). This hook scans
each submitted prompt for task patterns that map to a specialist subagent and,
on a match, injects a gentle reminder (hookSpecificOutput.additionalContext)
telling the MAIN agent to OFFER that subagent to the user. It never auto-spawns.

Why a hook: the user reported repeatedly forgetting to invoke subagents. A
prompt-time reminder fires at the generation point, so the main agent surfaces
the option instead of silently self-handling.

Notes:
- Subagents cannot themselves spawn subagents (the Task/Agent primitive is
  filtered in nested contexts), so only the main agent acts on this hint.
- Conditional injection: outputs nothing when no keyword matches (≈0 token cost
  on non-matching prompts).
- Projects can suppress agents that don't apply via .claude/harness-config.json
  {"excludedAgents": ["ue-replication-specialist"]} (e.g. single-player games
  excluding the networking specialist).
- Suppressed when the prompt already says "spawn" / "subagent" (user remembered).
- Any failure exits 0 silently so prompt submission is never blocked.

Decisions are logged to .claude/state/suggest-subagent.log (gitignored).
"""
from __future__ import annotations

import io
import json
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# (agent, short label, design-doc hint, [keywords]). Order = priority.
AGENT_RULES = [
    ("producer", "sprint 规划 / 里程碑 / 估时 / 范围审查 / 复盘", "plan/", [
        "sprint", "里程碑", "milestone", "估时", "estimate", "工期", "排期",
        "范围审查", "scope creep", "风险登记", "risk register", "复盘",
        "retrospective", "进度风险",
    ]),
    ("systems-designer", "数值公式 / 算例 / 进阶曲线 / 交互矩阵", "design/gdd/", [
        "数值公式", "伤害公式", "公式 audit", "算例", "进阶曲线", "成长曲线",
        "数值平衡", "交互矩阵", "damage formula", "balance formula",
    ]),
    ("economy-designer", "商人 sink/faucet / 掉落表 / 经济曲线", "design/gdd/", [
        "经济曲线", "商人", "sink", "faucet", "掉落表", "掉率", "loot table",
        "drop rate", "金币产出", "经济平衡",
    ]),
    ("game-designer", "核心循环 / 系统拆解 / 顶层框架", "design/gdd/", [
        "核心循环", "core loop", "系统拆解", "玩法框架", "顶层框架",
        "战斗框架",
    ]),
    ("level-designer", "关卡布局 / encounter / 空间叙事 / pacing", "design/gdd/", [
        "关卡布局", "关卡设计", "encounter", "空间叙事", "关卡 pacing",
        "level layout", "level design",
    ]),
    ("narrative-director", "故事架构 / 角色背景 / 对话策略 / lore", "design/gdd/", [
        "故事架构", "叙事架构", "角色背景", "对话策略", "剧情", "世界观",
        "lore", "narrative arc",
    ]),
    ("creative-director", "游戏愿景 / pillar 冲突 / 基调裁决", "design/gdd/game-concept.md", [
        "游戏愿景", "pillar 冲突", "美术方向", "基调裁决", "creative direction",
        "vision pillar",
    ]),
    ("technical-director", "架构决策 / 技术选型 / 性能预算 / ADR", "docs/architecture/", [
        "架构决策", "技术选型", "性能预算", "performance budget", "技术风险",
        "技术债", "tech debt", "写 adr", "新建 adr", "新 adr",
    ]),
    ("ue-gas-specialist", "Gameplay Ability System（GA/GE/AttributeSet/Tag）", "client/Source/", [
        "gas ", "gameplay ability", "gameplayeffect", "gameplay effect",
        "attributeset", "attribute set", "gameplay tag", "技能系统",
    ]),
    ("ue-umg-specialist", "UMG / CommonUI / widget / HUD", "client/Source/", [
        "umg", "commonui", "common ui", "widget", "wbp", "hud 实现",
        "界面实现", "ui 实现",
    ]),
    ("ue-blueprint-specialist", "Blueprint 架构 / BP↔C++ 边界 / BP 优化", "client/Content/", [
        "蓝图架构", "blueprint 架构", "bp spaghetti", "bp 优化", "蓝图重构",
        "bp 重构", "bp vs c++", "蓝图 vs c++",
    ]),
    ("unreal-specialist", "UE 最佳实践 / Subsystem 选型 / 打包 / Niagara·Nanite·Lumen", "client/Source/", [
        "subsystem 选型", "ue 最佳实践", "打包", "packaging", "niagara",
        "nanite", "lumen 调优", "ue 插件", "ue plugin", "bp vs c++ 决策",
    ]),
    ("ue-replication-specialist", "属性复制 / RPC / 客户端预测 / 带宽优化", "client/Source/", [
        "replication", "属性复制", "rpc", "客户端预测", "client prediction",
        "net serialization", "带宽优化", "多人同步", "联机同步",
    ]),
]

MAX_SUGGESTIONS = 3
LOG_PATH = Path(".claude/state/suggest-subagent.log")


def log(line: str) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now().isoformat(timespec='seconds')} {line}\n")
    except Exception:
        pass  # logging must never break the hook


def read_prompt() -> str:
    try:
        if hasattr(sys.stdin, "buffer"):
            raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        else:
            raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        return str(data.get("prompt", ""))
    except Exception:
        return ""


def load_excluded_agents() -> set:
    """Optional per-project override: .claude/harness-config.json {"excludedAgents": [...]}."""
    try:
        cfg = json.loads(Path(".claude/harness-config.json").read_text(encoding="utf-8"))
        return set(cfg.get("excludedAgents", []))
    except Exception:
        return set()


def match_agents(prompt_lower: str):
    excluded = load_excluded_agents()
    hits = []
    for agent, label, doc_hint, keywords in AGENT_RULES:
        if agent in excluded:
            continue
        kw = next((k for k in keywords if k.lower() in prompt_lower), None)
        if kw:
            hits.append((agent, label, doc_hint, kw))
    return hits[:MAX_SUGGESTIONS]


def build_context(hits) -> str:
    lines = [
        "=== 💡 子 agent 提示（hook 自动检测；可忽略）===",
        "",
        "本条消息匹配到下列专家 subagent。Claude Code **不会自动 spawn** —— 主 agent 应"
        "**主动提示用户**可用以下 subagent 并给出 spawn 模板，由用户决定是否启用。"
        "**不要自动 spawn**；subagent 也不能再 spawn 别的 subagent（叶子节点）。",
        "",
    ]
    for agent, label, doc_hint, _kw in hits:
        lines.append(f"• `{agent}` — {label}")
        lines.append(f"  spawn {agent} subagent: <任务描述；附 `{doc_hint}` 相关路径 + 期望产物>")
    lines.append("")
    lines.append("若任务并不需要专家深度，主 agent 可照常自处理，无需勉强 spawn。")
    return "\n".join(lines)


def main() -> int:
    prompt = read_prompt()
    if not prompt.strip():
        return 0

    prompt_lower = prompt.lower()

    # User already remembered — don't nag.
    if "subagent" in prompt_lower or "spawn " in prompt_lower:
        log("skip (prompt already references subagent/spawn)")
        return 0

    hits = match_agents(prompt_lower)
    if not hits:
        return 0

    log("suggest: " + ", ".join(h[0] for h in hits))
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": build_context(hits),
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
