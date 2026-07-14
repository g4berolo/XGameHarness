#!/bin/bash
# Game-studio harness PreToolUse hook: validates git commit / git push commands.
# Merged from validate-commit.sh + validate-push.sh (2026-06-11) — one process per Bash call instead of two.
# Exit 0 = allow, Exit 2 = block

INPUT=$(cat)

# Parse command
if command -v jq >/dev/null 2>&1; then
    COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
else
    COMMAND=$(echo "$INPUT" | grep -oE '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/"command"[[:space:]]*:[[:space:]]*"//;s/"$//')
fi

# Match `git [-C <path>] commit|push` at line start, after a chain separator
# (&& ; |) or after leading VAR=value prefixes — the old ^git anchor missed
# `git -C <path> commit`, `GIT_EDITOR=true git commit`, `cd x && git commit`.
GIT_CMD='(^|[;&|][[:space:]]*)([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*[[:space:]]+)*git[[:space:]]+(-C[[:space:]]+("[^"]*"|[^[:space:]]+)[[:space:]]+)?'

# ──────────────────────────────────────────────
# git commit validation
# ──────────────────────────────────────────────
if echo "$COMMAND" | grep -qE "${GIT_CMD}commit"; then
    # Get staged files
    STAGED=$(git diff --cached --name-only 2>/dev/null)
    if [ -z "$STAGED" ]; then
        exit 0
    fi

    WARNINGS=""

    # Validate JSON data files -- block invalid JSON
    DATA_FILES=$(echo "$STAGED" | grep -E '\.json$')
    if [ -n "$DATA_FILES" ]; then
        PYTHON_CMD=""
        for cmd in python python3 py; do
            if command -v "$cmd" >/dev/null 2>&1; then
                PYTHON_CMD="$cmd"
                break
            fi
        done

        while IFS= read -r file; do
            if [ -f "$file" ]; then
                if [ -n "$PYTHON_CMD" ]; then
                    if ! "$PYTHON_CMD" -m json.tool "$file" > /dev/null 2>&1; then
                        echo "BLOCKED: $file is not valid JSON" >&2
                        exit 2
                    fi
                fi
            fi
        done <<< "$DATA_FILES"
    fi

    # Check for cross-identity session state edits
    source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/resolve-identity.sh"
    IDENTITY=$(resolve_identity 2>/dev/null)
    ROLE=$(get_identity_role "$IDENTITY" 2>/dev/null)
    OTHER_STATE=$(echo "$STAGED" | grep "^team/session-state/" | grep -v "team/session-state/$IDENTITY/" 2>/dev/null)
    if [ -n "$OTHER_STATE" ] && [ "$ROLE" != "admin" ]; then
        WARNINGS="$WARNINGS\nWARNING: You are modifying another developer's session state:"
        while IFS= read -r ofile; do
            WARNINGS="$WARNINGS\n  $ofile"
        done <<< "$OTHER_STATE"
    fi

    # Check for TODO/FIXME without assignee
    SRC_FILES=$(echo "$STAGED" | grep -E '^client/Source/')
    if [ -n "$SRC_FILES" ]; then
        while IFS= read -r file; do
            if [ -f "$file" ]; then
                if grep -nE '(TODO|FIXME|HACK)[^(]' "$file" 2>/dev/null; then
                    WARNINGS="$WARNINGS\nSTYLE: $file has TODO/FIXME without owner tag. Use TODO(name) format."
                fi
            fi
        done <<< "$SRC_FILES"
    fi

    # Print warnings (non-blocking) and allow commit
    if [ -n "$WARNINGS" ]; then
        echo -e "=== Commit Validation Warnings ===$WARNINGS\n================================" >&2
    fi

    exit 0
fi

# ──────────────────────────────────────────────
# git push validation — warn on protected branches
# ──────────────────────────────────────────────
if echo "$COMMAND" | grep -qE "${GIT_CMD}push"; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    MATCHED_BRANCH=""

    for branch in develop main master; do
        if [ "$CURRENT_BRANCH" = "$branch" ]; then
            MATCHED_BRANCH="$branch"
            break
        fi
        if echo "$COMMAND" | grep -qE "[[:space:]]${branch}([[:space:]]|$)"; then
            MATCHED_BRANCH="$branch"
            break
        fi
    done

    if [ -n "$MATCHED_BRANCH" ]; then
        echo "Push to protected branch '$MATCHED_BRANCH' detected." >&2
        echo "Reminder: Ensure build passes, unit tests pass, and no S1/S2 bugs exist." >&2
    fi

    exit 0
fi

exit 0
