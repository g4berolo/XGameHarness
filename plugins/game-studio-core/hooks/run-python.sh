#!/bin/bash
# Game-studio harness helper: run a Python hook with whatever interpreter exists.
#
# hooks.json cannot probe for an interpreter, and a bare `python` does not exist
# on most Linux/macOS installs (python3 only) — hardcoding it silently disabled
# every Python hook there. Usage from hooks.json:
#
#   bash "${CLAUDE_PLUGIN_ROOT}/hooks/run-python.sh" "${CLAUDE_PLUGIN_ROOT}/hooks/<script>.py"
#
# stdin is passed straight through by exec, which the hooks depend on.

for cmd in python3 python py; do
    resolved=$(command -v "$cmd" 2>/dev/null) || continue

    # Skip the Microsoft Store app-execution alias *by path*, before paying to
    # launch it. On a Windows box without the Store Python, `python3` resolves
    # to that alias and always fails the probe below (exit 49) — but reaching
    # that verdict costs ~200ms of package resolution, on every prompt and
    # every file edit. It is also the slowest thing here when the machine is
    # busy, which is exactly when a hook timeout gets hit.
    # No path on Linux/macOS contains WindowsApps, so this is inert there.
    case "$resolved" in */WindowsApps/*) continue ;; esac

    # `command -v` alone is still not enough: other shims resolve but cannot
    # execute anything.
    "$cmd" -c "" >/dev/null 2>&1 || continue
    exec "$cmd" "$@"
done

# No usable interpreter. Hooks must fail open — never block the tool call.
exit 0
