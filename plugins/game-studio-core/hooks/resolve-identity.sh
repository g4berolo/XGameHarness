#!/bin/bash
# Game-studio harness identity resolution library
# Source this file from sibling hooks: source "$(dirname "${BASH_SOURCE[0]}")/resolve-identity.sh"
# Provides: resolve_identity, get_identity_role, get_session_state_dir,
#           get_session_state_file, get_session_state_file_rel, get_session_logs_dir

# Anchor on the hook-provided project root rather than CWD: hooks are not
# guaranteed to run with the project directory as CWD, and a wrong anchor
# silently degrades every caller to identity 'unknown'.
TEAM_CONFIG="${CLAUDE_PROJECT_DIR:-.}/.claude/team.json"

# Print a usable Python interpreter name. Same probe as run-python.sh: skip the
# Microsoft Store alias by path, then require that the interpreter actually runs.
_harness_python() {
    local cmd resolved
    for cmd in python3 python py; do
        resolved=$(command -v "$cmd" 2>/dev/null) || continue
        case "$resolved" in */WindowsApps/*) continue ;; esac
        "$cmd" -c "" >/dev/null 2>&1 || continue
        echo "$cmd"
        return 0
    done
    return 1
}

resolve_identity() {
    if [ ! -f "$TEAM_CONFIG" ]; then
        echo "WARNING: $TEAM_CONFIG not found. Using fallback identity 'unknown'." >&2
        echo "WARNING: the roster is delivered by the server/admin, not generated here." >&2
        echo "WARNING: pull it, or run 'harness.py roster --from <docs-repo>'." >&2
        echo "unknown"
        return 1
    fi

    local git_user git_email identity="" py

    # Read the project's git config, not whatever repo the hook's CWD happens to be in.
    git_user=$(git -C "$(_harness_project_root)" config user.name 2>/dev/null)
    git_email=$(git -C "$(_harness_project_root)" config user.email 2>/dev/null)

    # Exact matching only, same rule as scripts/harness.py identity(): git_users first,
    # then git_emails. The former jq-less path grepped for the value near a JSON key and
    # took the nearest key — it matched identity *keys*, roles and display names, so a
    # git user called "developer" resolved to an unrelated teammate. Never guess here:
    # a wrong identity writes into someone else's session-state.
    if command -v jq >/dev/null 2>&1; then
        if [ -n "$git_user" ]; then
            identity=$(jq -r --arg u "$git_user" '
                .identities | to_entries[] |
                select(.value.git_users[]? == $u) |
                .key' "$TEAM_CONFIG" 2>/dev/null | head -1)
        fi
        if [ -z "$identity" ] && [ -n "$git_email" ]; then
            identity=$(jq -r --arg e "$git_email" '
                .identities | to_entries[] |
                select(.value.git_emails[]? == $e) |
                .key' "$TEAM_CONFIG" 2>/dev/null | head -1)
        fi
    elif py=$(_harness_python); then
        identity=$("$py" -X utf8 - "$TEAM_CONFIG" "$git_user" "$git_email" 2>/dev/null <<'PY'
import json, sys
path, user, email = sys.argv[1:4]
with open(path, encoding="utf-8-sig") as handle:
    members = json.load(handle).get("identities") or {}
for field, value in (("git_users", user), ("git_emails", email)):
    if not value:
        continue
    for key, entry in members.items():
        if isinstance(entry, dict) and value in (entry.get(field) or []):
            print(key)
            sys.exit(0)
PY
)
    else
        echo "WARNING: neither jq nor Python is available; cannot read $TEAM_CONFIG." >&2
    fi

    # Same key shape harness.py accepts. The key becomes a path component under team/.
    if [ -n "$identity" ] && ! [[ "$identity" =~ ^[a-z][a-z0-9_-]*$ ]]; then
        echo "WARNING: roster key '$identity' is not a valid identity key ([a-z][a-z0-9_-]*)." >&2
        identity=""
    fi

    if [ -z "$identity" ]; then
        echo "WARNING: Git user '$git_user' ($git_email) not found in $TEAM_CONFIG" >&2
        echo "WARNING: Using fallback identity 'unknown'. Ask the roster owner to add this" >&2
        echo "WARNING: git user.name and user.email, then pull; do not self-register locally." >&2
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
