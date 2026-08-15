#!/bin/bash
# Game-studio harness identity resolution library
# Source this file from sibling hooks: source "$(dirname "${BASH_SOURCE[0]}")/resolve-identity.sh"
# Provides: resolve_identity, get_identity_role, get_session_state_dir,
#           get_session_state_file, get_session_state_file_rel, get_session_logs_dir

# Anchor on the hook-provided project root rather than CWD: hooks are not
# guaranteed to run with the project directory as CWD, and a wrong anchor
# silently degrades every caller to identity 'unknown'.
TEAM_CONFIG="${CLAUDE_PROJECT_DIR:-.}/.claude/team.json"

resolve_identity() {
    if [ ! -f "$TEAM_CONFIG" ]; then
        echo "WARNING: $TEAM_CONFIG not found. Using fallback identity 'unknown'." >&2
        echo "unknown"
        return 1
    fi

    local git_user git_email identity

    git_user=$(git config user.name 2>/dev/null)
    git_email=$(git config user.email 2>/dev/null)

    if command -v jq >/dev/null 2>&1; then
        # Primary: match by git username
        identity=$(jq -r --arg u "$git_user" '
            .identities | to_entries[] |
            select(.value.git_users[]? == $u) |
            .key' "$TEAM_CONFIG" 2>/dev/null | head -1)

        # Fallback: match by email
        if [ -z "$identity" ]; then
            identity=$(jq -r --arg e "$git_email" '
                .identities | to_entries[] |
                select(.value.git_emails[]? == $e) |
                .key' "$TEAM_CONFIG" 2>/dev/null | head -1)
        fi
    else
        # Lightweight grep fallback (works for simple flat schema)
        if [ -n "$git_user" ]; then
            identity=$(grep -B10 "\"$git_user\"" "$TEAM_CONFIG" 2>/dev/null |
                       grep -oE '"[a-z_][a-z0-9_]*"\s*:\s*\{' | tail -1 |
                       sed 's/"//g;s/\s*:\s*{//')
        fi
        if [ -z "$identity" ] && [ -n "$git_email" ]; then
            identity=$(grep -B10 "\"$git_email\"" "$TEAM_CONFIG" 2>/dev/null |
                       grep -oE '"[a-z_][a-z0-9_]*"\s*:\s*\{' | tail -1 |
                       sed 's/"//g;s/\s*:\s*{//')
        fi
    fi

    if [ -z "$identity" ]; then
        echo "WARNING: Git user '$git_user' ($git_email) not found in $TEAM_CONFIG" >&2
        echo "WARNING: Using fallback identity 'unknown'. Add your account to $TEAM_CONFIG." >&2
        echo "unknown"
        return 2
    fi

    echo "$identity"
    return 0
}

get_identity_role() {
    local identity="$1" role=""
    # jq exits non-zero on a missing/invalid file, so the `// "developer"`
    # default inside the filter never fires there — guard and re-default here.
    if [ -f "$TEAM_CONFIG" ] && command -v jq >/dev/null 2>&1; then
        role=$(jq -r --arg id "$identity" '.identities[$id].role // "developer"' "$TEAM_CONFIG" 2>/dev/null)
    fi
    if [ -z "$role" ] || [ "$role" = "null" ]; then
        role="developer"
    fi
    echo "$role"
}

# Same anchoring rationale as TEAM_CONFIG: a hook may run from any CWD, and a
# CWD-relative path would silently write session state outside the project.
_harness_project_root() {
    echo "${CLAUDE_PROJECT_DIR:-.}"
}

get_session_state_dir() {
    local identity="$1"
    echo "$(_harness_project_root)/team/session-state/$identity"
}

get_session_state_file() {
    local identity="$1"
    echo "$(_harness_project_root)/team/session-state/$identity/active.md"
}

# Repo-relative variant. `git show <rev>:<path>` resolves <path> against the repo
# root, so the anchored absolute form above does not work there.
get_session_state_file_rel() {
    local identity="$1"
    echo "team/session-state/$identity/active.md"
}

get_session_logs_dir() {
    local identity="$1"
    echo "$(_harness_project_root)/team/session-logs/$identity"
}
