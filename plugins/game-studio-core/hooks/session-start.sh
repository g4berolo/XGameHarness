#!/bin/bash
# Game-studio harness SessionStart hook: Load project context at session start
# Identity-aware: resolves current git user to project identity

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/resolve-identity.sh"

# Consume the hook payload: session_id is needed to hand off rule-injection
# bookkeeping to inject-rules.py (see the path-scoped rules block below).
HOOK_INPUT=$(cat 2>/dev/null)
if command -v jq >/dev/null 2>&1; then
    SESSION_ID=$(printf '%s' "$HOOK_INPUT" | jq -r '.session_id // empty' 2>/dev/null)
else
    SESSION_ID=$(printf '%s' "$HOOK_INPUT" |
        grep -oE '"session_id"[[:space:]]*:[[:space:]]*"[^"]*"' |
        sed 's/.*:[[:space:]]*"//;s/"$//')
fi

PROJECT_NAME="$(basename "${CLAUDE_PROJECT_DIR:-$PWD}")"
echo "=== ${PROJECT_NAME} — Session Context ==="

# Identity resolution
IDENTITY=$(resolve_identity)
ROLE=$(get_identity_role "$IDENTITY")
echo "Developer: $IDENTITY (role: $ROLE)"

# Current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ -n "$BRANCH" ]; then
    echo "Branch: $BRANCH"

    # Recent commits
    echo ""
    echo "Recent commits:"
    git log --oneline -5 2>/dev/null | while read -r line; do
        echo "  $line"
    done
fi

# Code health quick check (auto-enables when client/Source/ exists)
if [ -d "client/Source" ]; then
    TODO_COUNT=$(grep -r "TODO" client/Source/ 2>/dev/null | wc -l)
    FIXME_COUNT=$(grep -r "FIXME" client/Source/ 2>/dev/null | wc -l)
    if [ "$TODO_COUNT" -gt 0 ] || [ "$FIXME_COUNT" -gt 0 ]; then
        echo ""
        echo "Code health: ${TODO_COUNT} TODOs, ${FIXME_COUNT} FIXMEs in client/Source/"
    fi
fi

# --- Active session state recovery (identity-aware) ---
STATE_FILE=$(get_session_state_file "$IDENTITY")
if [ -f "$STATE_FILE" ]; then
    echo ""
    echo "=== ACTIVE SESSION STATE DETECTED ==="
    echo "Your session state: $STATE_FILE"
    echo "Read this file to recover context and continue where you left off."
    echo ""
    echo "Quick summary:"
    head -20 "$STATE_FILE" 2>/dev/null
    TOTAL_LINES=$(wc -l < "$STATE_FILE" 2>/dev/null)
    if [ "$TOTAL_LINES" -gt 20 ]; then
        echo "  ... ($TOTAL_LINES total lines — read the full file to continue)"
    fi
    echo "=== END SESSION STATE PREVIEW ==="
fi

# --- Show custom memory/todo files ---
STATE_DIR=$(get_session_state_dir "$IDENTITY")
if [ -d "$STATE_DIR" ]; then
    MEMORY_FILES=$(find "$STATE_DIR" -maxdepth 1 -name "*.md" ! -name "active.md" 2>/dev/null)
    if [ -n "$MEMORY_FILES" ]; then
        echo ""
        echo "=== YOUR MEMORY FILES ==="
        echo "$MEMORY_FILES" | while read -r mf; do
            BASENAME=$(basename "$mf" .md)
            LINES=$(wc -l < "$mf" 2>/dev/null | tr -d ' ')
            echo "  $mf ($LINES lines)"
        done
        echo "=== END MEMORY FILES ==="
    fi
fi

# --- Path-scoped rules (full content for first-edit coverage) ---
# PostToolUse fires AFTER an edit, so inject-rules.py alone cannot govern the
# FIRST edit of a session — hence the full dump here.
#
# Because this dump already puts every rule in context, we pre-write the same
# session markers inject-rules.py uses. Without that handoff the first matching
# edit re-injects a rule body that is already in context, once per rule.
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
RULES_GLOB=("$PROJECT_ROOT"/.claude/rules/*.md)
if [ -e "${RULES_GLOB[0]}" ]; then
    echo ""
    echo "=== Path-Scoped Rules (injected once here; inject-rules.py re-injects only rules added later) ==="
    MARKER_DIR=""
    if [ -n "$SESSION_ID" ]; then
        MARKER_DIR="$PROJECT_ROOT/.claude/state/rules-injected/$SESSION_ID"
        mkdir -p "$MARKER_DIR" 2>/dev/null
    fi
    for rule_file in "${RULES_GLOB[@]}"; do
        echo ""
        echo "--- $(basename "$rule_file") ---"
        cat "$rule_file"
        if [ -n "$MARKER_DIR" ] && [ -d "$MARKER_DIR" ]; then
            RULE_NAME=$(basename "$rule_file" .md)
            : > "$MARKER_DIR/$RULE_NAME" 2>/dev/null
        fi
    done
    echo ""
    echo "=== END Path-Scoped Rules ==="
fi

# --- Agent process rules (plugin-provided; replaces the former CLAUDE.md @import) ---
APR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../docs/agent-process-rules.md"
if [ -f "$APR" ]; then
    echo ""
    echo "=== Agent Process Rules (plugin-provided; treat as CLAUDE.md-level instructions) ==="
    cat "$APR"
    echo ""
    echo "=== END Agent Process Rules ==="
fi

# --- Skill-first routing bootstrap (R5 short form; mandatory workflow, not a suggestion) ---
echo ""
echo "=== ⚡ Skill-First 路由（R5 摘要 — 强制流程）==="
echo "接到任何任务，动手前先扫一遍已装 skills（速查表 = XGameHarness HANDBOOK § 1）："
echo "  1. 有匹配 skill → 直接调用（Skill tool），不要徒手复刻它的流程"
echo "  2. 目标模糊 / 不知从何下手 / 多步工作流 → 调 /how-to-do（主推入口，任何时候可用）"
echo "  3. 无匹配才自行处理；subagent 仍按 R4 显式触发（提示用户，不自动 spawn）"
echo "=== END Skill-First 路由 ==="

echo "==================================="
exit 0
