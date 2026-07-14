#!/bin/bash
# Game-studio harness SessionEnd hook: Log session summary when the session ends
# (was Stop until 2026-07-09 — Stop fires after EVERY reply, causing one
#  pointer block per turn; SessionEnd fires once per session)
# Identity-aware: archives to per-developer session logs

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/resolve-identity.sh"

IDENTITY=$(resolve_identity)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Per-developer log directory
SESSION_LOG_DIR=$(get_session_logs_dir "$IDENTITY")
mkdir -p "$SESSION_LOG_DIR" 2>/dev/null

# Monthly-rotated log file (see .claude/docs/directory-structure.md § session-logs)
LOG_FILE="$SESSION_LOG_DIR/session-log-$(date +%Y-%m).md"

# Log recent git activity from this session (check up to 8 hours for long sessions).
# --author filter: without it, commits pulled in from teammates land in this log too.
RECENT_COMMITS=$(git log --oneline --since="8 hours ago" --author="$(git config user.name)" 2>/dev/null)
MODIFIED_FILES=$(git diff --name-only 2>/dev/null)

# --- Record a lightweight state pointer on shutdown ---
# Do NOT dump the full active.md: it is git-tracked, so every historical version
# is recoverable via git. A full-cat snapshot per session was the dominant source
# of session-log bloat. Record a one-line pointer instead.
STATE_FILE=$(get_session_state_file "$IDENTITY")
if [ -f "$STATE_FILE" ]; then
    STATE_LINES=$(wc -l < "$STATE_FILE" 2>/dev/null | tr -d ' ')
    HEAD_HASH=$(git rev-parse --short HEAD 2>/dev/null)
    {
        echo "## Session State Pointer: $TIMESTAMP"
        echo "active.md @ ${STATE_LINES} lines, HEAD ${HEAD_HASH}"
        echo "(full state: git show ${HEAD_HASH}:$STATE_FILE)"
        echo "---"
        echo ""
    } >> "$LOG_FILE" 2>/dev/null
    # active.md persists as living checkpoint (see .claude/docs/context-management.md)
fi

if [ -n "$RECENT_COMMITS" ] || [ -n "$MODIFIED_FILES" ]; then
    {
        echo "## Session End: $TIMESTAMP"
        if [ -n "$RECENT_COMMITS" ]; then
            echo "### Commits"
            echo "$RECENT_COMMITS"
        fi
        if [ -n "$MODIFIED_FILES" ]; then
            echo "### Uncommitted Changes"
            echo "$MODIFIED_FILES"
        fi
        echo "---"
        echo ""
    } >> "$LOG_FILE" 2>/dev/null
fi

exit 0
