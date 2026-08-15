#!/bin/bash
# Game-studio harness PreToolUse hook: validates git commit / git push commands.
# Merged from validate-commit.sh + validate-push.sh (2026-06-11) — one process per Bash call instead of two.
# Exit 0 = allow, Exit 2 = block

INPUT=$(cat)

TMP_LIST=""
TMP_DIR=""
cleanup() {
    [ -n "$TMP_LIST" ] && rm -f "$TMP_LIST"
    [ -n "$TMP_DIR" ] && rm -rf "$TMP_DIR"
    return 0
}
trap cleanup EXIT

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

# `git -C <path> commit` acts on ANOTHER repository. Every evidence-gathering
# call below must target that same repo — otherwise a clean commit over there
# gets judged by this repo's staging area, and vice versa.
TARGET_DIR=$(echo "$COMMAND" |
    grep -oE "${GIT_CMD}(commit|push)" |
    grep -oE '\-C[[:space:]]+("[^"]*"|[^[:space:]]+)' |
    head -1 | sed 's/^-C[[:space:]]*//; s/^"//; s/"$//')

git_t() {
    if [ -n "$TARGET_DIR" ]; then
        git -C "$TARGET_DIR" "$@"
    else
        git "$@"
    fi
}

# Resolve a working interpreter. `command -v python3` is not enough on Windows,
# where the Store app-execution alias resolves but cannot run anything.
find_python() {
    local cmd
    for cmd in python3 python py; do
        command -v "$cmd" >/dev/null 2>&1 || continue
        "$cmd" -c "" >/dev/null 2>&1 || continue
        echo "$cmd"
        return 0
    done
    return 1
}

# ──────────────────────────────────────────────
# git commit validation
# ──────────────────────────────────────────────
if echo "$COMMAND" | grep -qE "${GIT_CMD}commit"; then
    # core.quotepath=true (git's default) octal-escapes non-ASCII paths and wraps
    # them in quotes, which silently defeats every filter below; -z additionally
    # handles paths containing spaces. NUL bytes cannot survive a shell variable,
    # so the list goes through a temp file.
    TMP_LIST=$(mktemp 2>/dev/null) || TMP_LIST="${TMPDIR:-/tmp}/xgh-staged.$$"
    git_t -c core.quotepath=false diff --cached -z --name-only > "$TMP_LIST" 2>/dev/null
    [ -s "$TMP_LIST" ] || exit 0

    WARNINGS=""

    PYTHON_CMD=$(find_python)

    # Validate JSON data files -- block invalid JSON.
    # Materialize every staged .json blob into one temp dir, then validate them
    # all in a SINGLE python process: spawning one interpreter per file costs
    # ~150ms each and blew the PreToolUse timeout on batch data commits, after
    # which the hook was killed and the commit passed unchecked (fail-open).
    if [ -n "$PYTHON_CMD" ]; then
        TMP_DIR=$(mktemp -d 2>/dev/null) || TMP_DIR=""
    fi
    if [ -n "$TMP_DIR" ]; then
        n=0
        while IFS= read -r -d '' file; do
            case "$file" in *.json) ;; *) continue ;; esac
            # Skip staged deletions — no blob to validate.
            git_t cat-file -e ":$file" 2>/dev/null || continue
            n=$((n + 1))
            if ! git_t show ":$file" > "$TMP_DIR/$n.json" 2>/dev/null; then
                # Could not read the blob. That is a git problem, not proof of
                # malformed JSON — do not block on it.
                echo "NOTE: could not read staged blob for $file; JSON check skipped" >&2
                rm -f "$TMP_DIR/$n.json"
                continue
            fi
            printf '%s' "$file" > "$TMP_DIR/$n.name"
        done < "$TMP_LIST"

        if [ "$n" -gt 0 ]; then
            # utf-8-sig accepts files with or without a UTF-8 BOM. Plain
            # `json.tool` rejects a BOM outright, which blocked perfectly valid
            # config files exported by Windows editors.
            PYCHECK='
import json, os, sys
d = sys.argv[1]
bad = []
for f in sorted(os.listdir(d)):
    if not f.endswith(".json"):
        continue
    try:
        with open(os.path.join(d, f[:-5] + ".name"), encoding="utf-8", errors="replace") as fh:
            name = fh.read().strip()
    except OSError:
        name = f
    try:
        with open(os.path.join(d, f), encoding="utf-8-sig") as fh:
            json.load(fh)
    except (ValueError, OSError) as e:
        bad.append(name + ": " + str(e))
# Write raw UTF-8 bytes. On Windows sys.stdout defaults to the ANSI codepage,
# so a non-ASCII filename here raised UnicodeEncodeError and killed the checker
# -- with stderr discarded that looked identical to "all files valid".
sys.stdout.buffer.write("\n".join(bad).encode("utf-8"))
'
            BAD=$("$PYTHON_CMD" -c "$PYCHECK" "$TMP_DIR" 2>"$TMP_DIR/pyerr.txt")
            PYRC=$?
            if [ "$PYRC" -ne 0 ]; then
                # Never fail closed on a checker crash, but never stay silent
                # about it either -- silence is what made the last bug invisible.
                echo "NOTE: JSON validation did not run ($PYTHON_CMD exited $PYRC); staged JSON was NOT checked" >&2
                head -3 "$TMP_DIR/pyerr.txt" >&2
            elif [ -n "$BAD" ]; then
                echo "BLOCKED: invalid JSON in staged content:" >&2
                echo "$BAD" >&2
                exit 2
            fi
        fi
    fi

    # Check for cross-identity session state edits
    source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/resolve-identity.sh"
    IDENTITY=$(resolve_identity 2>/dev/null)
    ROLE=$(get_identity_role "$IDENTITY" 2>/dev/null)
    if [ "$ROLE" != "admin" ]; then
        while IFS= read -r -d '' file; do
            case "$file" in
                "team/session-state/$IDENTITY/"*) continue ;;
                team/session-state/*) ;;
                *) continue ;;
            esac
            if [ -z "$WARNINGS" ] || [ "${WARNINGS#*another developer}" = "$WARNINGS" ]; then
                WARNINGS="$WARNINGS\nWARNING: You are modifying another developer's session state:"
            fi
            WARNINGS="$WARNINGS\n  $file"
        done < "$TMP_LIST"
    fi

    # Check for TODO/FIXME without assignee.
    # Read the STAGED blob, not the working tree: with `git -C <other-repo>` the
    # working-tree path does not even resolve from here.
    while IFS= read -r -d '' file; do
        case "$file" in client/Source/*) ;; *) continue ;; esac
        git_t cat-file -e ":$file" 2>/dev/null || continue
        # -q: this is a predicate — without it every matching line leaks into
        # hook stdout. `([^(]|$)` also catches a bare end-of-line `// TODO`,
        # which `[^(]` alone missed.
        if git_t show ":$file" 2>/dev/null | grep -qE '(TODO|FIXME|HACK)([^(]|$)'; then
            WARNINGS="$WARNINGS\nSTYLE: $file has TODO/FIXME without owner tag. Use TODO(name) format."
        fi
    done < "$TMP_LIST"

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
    CURRENT_BRANCH=$(git_t rev-parse --abbrev-ref HEAD 2>/dev/null)
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
