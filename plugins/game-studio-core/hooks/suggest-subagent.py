#!/usr/bin/env python3
"""
UserPromptSubmit hook: suggest a relevant specialist subagent by keyword.

Claude Code does NOT auto-spawn subagents — the developer must explicitly name
the agent type (see docs/agent-process-rules.md § R4). This hook scans each
submitted prompt for task patterns that map to a specialist subagent and, on a
match, injects a gentle reminder (hookSpecificOutput.additionalContext) telling
the MAIN agent to OFFER that subagent to the user. It never auto-spawns.

Why a hook: the user reported repeatedly forgetting to invoke subagents. A
prompt-time reminder fires at the generation point, so the main agent surfaces
the option instead of silently self-handling.

Notes:
- Agent identifiers MUST carry their plugin prefix ("game-studio-core:producer").
  The Agent tool rejects bare names outright: `Agent type 'producer' not found`.
- Subagents cannot themselves spawn subagents (the Task/Agent primitive is
  filtered in nested contexts), so only the main agent acts on this hint.
- Conditional injection: outputs nothing when no keyword matches (≈0 token cost
  on non-matching prompts).
- unreal-pack agents are only suggested when that pack is actually enabled for
  the project (see pack_enabled) — game-studio-core is engine-agnostic and must
  not advertise agents a non-UE project has never installed.
- Projects can suppress agents that don't apply via .claude/harness-config.json
  {"excludedAgents": ["unreal-pack:ue-replication-specialist"]}.
- Suppressed when the prompt already says "spawn" / "subagent" (user remembered).
- Any failure exits 0 silently so prompt submission is never blocked.

Decisions are logged to .claude/state/suggest-subagent.log (gitignored).
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Compiled once per process, keyed by lowercased keyword.
_ASCII_KW_CACHE: dict = {}

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Plugin-hosted: this script lives in the plugin cache, so the project root must
# come from the hook environment, never from __file__ or a bare relative path.
PROJECT_ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
LOG_PATH = PROJECT_ROOT / ".claude" / "state" / "suggest-subagent.log"
CONFIG_PATH = PROJECT_ROOT / ".claude" / "harness-config.json"
SETTINGS_PATHS = (
    PROJECT_ROOT / ".claude" / "settings.json",
    PROJECT_ROOT / ".claude" / "settings.local.json",
)

CORE = "game-studio-core"
UE = "unreal-pack"

# (pack, agent, short label, design-doc hint, [keywords]). Order = priority.
AGENT_RULES = [
    (CORE, "producer", "sprint 规划 / 里程碑 / 估时 / 范围审查 / 复盘", "plan/", [
        "sprint", "里程碑", "milestone", "估时", "estimate", "工期", "排期",
        "范围审查", "scope creep", "风险登记", "risk register", "复盘",
        "retrospective", "进度风险",
    ]),
    (CORE, "systems-designer", "数值公式 / 算例 / 进阶曲线 / 交互矩阵", "design/gdd/", [
        "数值公式", "伤害公式", "公式 audit", "算例", "进阶曲线", "成长曲线",
        "数值平衡", "交互矩阵", "damage formula", "balance formula",
    ]),
    (CORE, "economy-designer", "商人 sink/faucet / 掉落表 / 经济曲线", "design/gdd/", [
        "经济曲线", "商人", "掉落表", "掉率", "loot table",
        "drop rate", "金币产出", "经济平衡", "sink/faucet", "资源产销",
    ]),
    (CORE, "game-designer", "核心循环 / 系统拆解 / 顶层框架", "design/gdd/", [
        "核心循环", "core loop", "系统拆解", "玩法框架", "顶层框架",
        "战斗框架",
    ]),
    (CORE, "level-designer", "关卡布局 / encounter / 空间叙事 / pacing", "design/gdd/", [
        "关卡布局", "关卡设计", "encounter", "空间叙事", "关卡 pacing",
        "level layout", "level design",
    ]),
    (CORE, "narrative-director", "故事架构 / 角色背景 / 对话策略 / lore", "design/gdd/", [
        "故事架构", "叙事架构", "角色背景", "对话策略", "剧情", "世界观",
        "lore", "narrative arc",
    ]),
    (CORE, "creative-director", "游戏愿景 / pillar 冲突 / 基调裁决", "design/gdd/game-concept.md", [
        "游戏愿景", "pillar 冲突", "美术方向", "基调裁决", "creative direction",
        "vision pillar",
    ]),
    (CORE, "technical-director", "架构决策 / 技术选型 / 性能预算 / ADR", "docs/architecture/", [
        "架构决策", "技术选型", "性能预算", "performance budget", "技术风险",
        "技术债", "tech debt", "写 adr", "新建 adr", "新 adr",
    ]),
    (CORE, "modeler", "AI 图生 3D 管线（Tripo3D）", "art/", [
        "图生3d", "图生 3d", "生成模型", "3d 模型", "tripo", "建模管线",
    ]),
    (UE, "ue-gas-specialist", "Gameplay Ability System（GA/GE/AttributeSet/Tag）", "client/Source/", [
        "gas ", "gameplay ability", "gameplayeffect", "gameplay effect",
        "attributeset", "attribute set", "gameplay tag", "技能系统",
    ]),
    (UE, "ue-umg-specialist", "UMG / CommonUI / widget / HUD", "client/Source/", [
        "umg", "commonui", "common ui", "widget", "wbp", "hud 实现",
        "界面实现", "ui 实现",
    ]),
    (UE, "ue-blueprint-specialist", "Blueprint 架构 / BP↔C++ 边界 / BP 优化", "client/Content/", [
        "蓝图架构", "blueprint 架构", "bp spaghetti", "bp 优化", "蓝图重构",
        "bp 重构", "bp vs c++", "蓝图 vs c++",
    ]),
    (UE, "unreal-specialist", "UE 最佳实践 / Subsystem 选型 / 打包 / Niagara·Nanite·Lumen", "client/Source/", [
        "subsystem 选型", "ue 最佳实践", "ue 打包", "packaging", "niagara",
        "nanite", "lumen 调优", "ue 插件", "ue plugin", "bp vs c++ 决策",
    ]),
    (UE, "ue-replication-specialist", "属性复制 / RPC / 客户端预测 / 带宽优化", "client/Source/", [
        "replication", "属性复制", "rpc", "客户端预测", "client prediction",
        "net serialization", "带宽优化", "多人同步", "联机同步",
    ]),
]

MAX_SUGGESTIONS = 3


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
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return set(cfg.get("excludedAgents", []))
    except Exception:
        return set()


def enabled_packs() -> set | None:
    """Plugin names enabled for this project, or None if it cannot be determined.

    Returning None means "unknown" and callers fail open (suggest everything),
    preserving prior behaviour rather than silently hiding valid agents from a
    project whose settings live somewhere this hook cannot see.
    """
    found = False
    packs: set = set()
    for path in SETTINGS_PATHS:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        entries = data.get("enabledPlugins")
        if not isinstance(entries, dict):
            continue
        found = True
        for key, on in entries.items():
            if on:
                packs.add(str(key).split("@", 1)[0])
    return packs if found else None


def _keyword_hit(keyword: str, prompt_lower: str) -> bool:
    """Match a keyword against the prompt, honouring word boundaries on ASCII.

    A bare substring test made "lore" fire on "explore" and "rpc" on "grpc",
    injecting a narrative-director or replication-specialist block into
    completely unrelated prompts. CJK keywords keep substring matching --
    Chinese has no word boundaries, so \\b would never match there.
    """
    kw = keyword.lower()
    if not kw:
        return False
    if any(ord(ch) > 127 for ch in kw):
        return kw in prompt_lower
    pattern = _ASCII_KW_CACHE.get(kw)
    if pattern is None:
        pattern = re.compile(
            r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])"
        )
        _ASCII_KW_CACHE[kw] = pattern
    return pattern.search(prompt_lower) is not None


def match_agents(prompt_lower: str):
    excluded = load_excluded_agents()
    packs = enabled_packs()
    hits = []
    for pack, agent, label, doc_hint, keywords in AGENT_RULES:
        # Engine-agnostic core must not advertise agents from a pack this
        # project never installed.
        if packs is not None and pack not in packs:
            continue
        full_name = f"{pack}:{agent}"
        if full_name in excluded or agent in excluded:
            continue
        kw = next((k for k in keywords if _keyword_hit(k, prompt_lower)), None)
        if kw:
            hits.append((full_name, label, doc_hint, kw))
    return hits[:MAX_SUGGESTIONS]


def build_context(hits) -> str:
    lines = [
        "=== 💡 子 agent 提示（hook 自动检测；可忽略）===",
        "",
        "本条消息匹配到下列专家 subagent。Claude Code **不会自动 spawn** —— 主 agent 应"
        "**主动提示用户**可用以下 subagent 并给出 spawn 模板，由用户决定是否启用。"
        "**不要自动 spawn**；subagent 也不能再 spawn 别的 subagent（叶子节点）。",
        "",
        "agent 名必须带插件前缀，否则 Agent tool 直接报 `Agent type not found`。",
        "",
    ]
    for full_name, label, doc_hint, _kw in hits:
        lines.append(f"• `{full_name}` — {label}")
        lines.append(f"  spawn {full_name} subagent: <任务描述；附 `{doc_hint}` 相关路径 + 期望产物>")
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
