#!/bin/bash
# Game-studio harness identity resolution library
# Source this file from sibling hooks: source "$(dirname "${BASH_SOURCE[0]}")/resolve-identity.sh"
# Provides: resolve_identity, get_identity_role, get_session_state_dir, get_session_state_file

TEAM_CONFIG=".claude/team.json"

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
    local identity="$1"
    if command -v jq >/dev/null 2>&1; then
        jq -r --arg id "$identity" '.identities[$id].role // "developer"' "$TEAM_CONFIG" 2>/dev/null
    else
        echo "developer"
    fi
}

get_session_state_dir() {
    local identity="$1"
    echo "team/session-state/$identity"
}

get_session_state_file() {
    local identity="$1"
    echo "team/session-state/$identity/active.md"
}

get_session_logs_dir() {
    local identity="$1"
    echo "team/session-logs/$identity"
}
