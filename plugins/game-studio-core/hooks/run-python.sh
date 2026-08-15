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
    command -v "$cmd" >/dev/null 2>&1 || continue
    # `command -v` alone is not enough on Windows: the Microsoft Store
    # app-execution alias resolves but cannot execute anything.
    "$cmd" -c "" >/dev/null 2>&1 || continue
    exec "$cmd" "$@"
done

# No usable interpreter. Hooks must fail open — never block the tool call.
exit 0
