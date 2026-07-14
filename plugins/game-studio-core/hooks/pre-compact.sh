#!/bin/bash
# Game-studio harness PreCompact hook: Dump session state before context compression
# Identity-aware: reads per-developer state and memory files

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/resolve-identity.sh"

IDENTITY=$(resolve_identity)

echo "=== SESSION STATE BEFORE COMPACTION ==="
echo "Timestamp: $(date)"
echo "Developer: $IDENTITY"

# --- Active session state file (identity-aware) ---
STATE_FILE=$(get_session_state_file "$IDENTITY")
if [ -f "$STATE_FILE" ]; then
    echo ""
    echo "## Active Session State (from $STATE_FILE)"
    STATE_LINES=$(wc -l < "$STATE_FILE" 2>/dev/null | tr -d ' ')
    if [ "$STATE_LINES" -gt 100 ] 2>/dev/null; then
        head -n 100 "$STATE_FILE"
        echo "... (truncated — $STATE_LINES total lines, showing first 100)"
    else
        cat "$STATE_FILE"
    fi
else
    echo ""
    echo "## No active session state file found"
    echo "Consider maintaining $STATE_FILE for better recovery."
fi

# --- Custom memory/todo files ---
STATE_DIR=$(get_session_state_dir "$IDENTITY")
if [ -d "$STATE_DIR" ]; then
    MEMORY_FILES=$(find "$STATE_DIR" -maxdepth 1 -name "*.md" ! -name "active.md" 2>/dev/null)
    if [ -n "$MEMORY_FILES" ]; then
        echo ""
        echo "## Custom Memory Files"
        echo "$MEMORY_FILES" | while read -r mf; do
            echo "### $(basename "$mf")"
            MF_LINES=$(wc -l < "$mf" 2>/dev/null | tr -d ' ')
            if [ "$MF_LINES" -gt 30 ] 2>/dev/null; then
                head -n 30 "$mf" 2>/dev/null
                echo "... (truncated — $MF_LINES total lines)"
            else
                cat "$mf" 2>/dev/null
            fi
        done
    fi
fi

# --- Files modified this session (unstaged + staged + untracked) ---
echo ""
echo "## Files Modified (git working tree)"

CHANGED=$(git diff --name-only 2>/dev/null)
STAGED=$(git diff --staged --name-only 2>/dev/null)
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null)

if [ -n "$CHANGED" ]; then
    echo "Unstaged changes:"
    echo "$CHANGED" | while read -r f; do echo "  - $f"; done
fi
if [ -n "$STAGED" ]; then
    echo "Staged changes:"
    echo "$STAGED" | while read -r f; do echo "  - $f"; done
fi
if [ -n "$UNTRACKED" ]; then
    echo "New untracked files:"
    echo "$UNTRACKED" | while read -r f; do echo "  - $f"; done
fi
if [ -z "$CHANGED" ] && [ -z "$STAGED" ] && [ -z "$UNTRACKED" ]; then
    echo "  (no uncommitted changes)"
fi

# --- Work-in-progress design docs ---
echo ""
echo "## Design Docs — Work In Progress"

WIP_FOUND=false
if [ -d "design/gdd" ]; then
    for f in design/gdd/*.md; do
        [ -f "$f" ] || continue
        INCOMPLETE=$(grep -n -E "TODO|WIP|PLACEHOLDER|\[TO BE|\[TBD\]" "$f" 2>/dev/null)
        if [ -n "$INCOMPLETE" ]; then
            WIP_FOUND=true
            echo "  $f:"
            echo "$INCOMPLETE" | while read -r line; do echo "    $line"; done
        fi
    done
fi

if [ "$WIP_FOUND" = false ]; then
    echo "  (no WIP markers found in design docs)"
fi

# --- Log compaction event ---
SESSION_LOG_DIR=$(get_session_logs_dir "$IDENTITY")
mkdir -p "$SESSION_LOG_DIR" 2>/dev/null
echo "Context compaction occurred at $(date)." \
    >> "$SESSION_LOG_DIR/compaction-log.txt" 2>/dev/null

echo ""
echo "## Recovery Instructions"
echo "After compaction, read $STATE_FILE to recover full working context."
echo "Then read any files listed above that are being actively worked on."
echo "=== END SESSION STATE ==="

exit 0
