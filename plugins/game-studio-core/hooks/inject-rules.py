#!/usr/bin/env python3
"""
PostToolUse hook: path-scoped rules auto-injection.

Reads stdin JSON from Claude Code, parses .claude/rules/*.md frontmatter
`paths:` glob list, matches against tool_input.file_path, and outputs
hookSpecificOutput.additionalContext if any rule matches.

Session-level marker in .claude/state/rules-injected/{session_id}/{rule_name}
prevents repeated injection within the same session.

See .claude/docs/rules-mechanism.md for the full convention.
"""
from __future__ import annotations

import io
import json
import os
import pathlib
import re
import sys
import traceback
from datetime import datetime

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Plugin-hosted: the script lives in the plugin cache, so the project root must
# come from the hook environment (CLAUDE_PROJECT_DIR), not from __file__.
REPO_ROOT = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or pathlib.Path.cwd()).resolve()
RULES_DIR = REPO_ROOT / ".claude" / "rules"
STATE_DIR = REPO_ROOT / ".claude" / "state" / "rules-injected"
LOG_FILE = REPO_ROOT / ".claude" / "state" / "inject-rules.log"

ALLOWED_TOOLS = {"Edit", "Write", "MultiEdit"}


def log(msg: str) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n")
    except Exception:
        pass


def parse_frontmatter(text: str) -> tuple[list[str], str]:
    """Extract `paths:` list from YAML frontmatter; return (paths, body)."""
    m = re.match(r"^---\s*\n(.*?\n)---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return [], text
    fm, body = m.group(1), m.group(2)
    paths: list[str] = []
    in_paths = False
    for line in fm.splitlines():
        stripped = line.strip()
        if stripped.startswith("paths:"):
            inline = stripped[len("paths:"):].strip()
            if inline.startswith("["):
                items = re.findall(r'"([^"]+)"|\'([^\']+)\'', inline)
                paths.extend(a or b for a, b in items)
                in_paths = False
            else:
                in_paths = True
            continue
        if in_paths:
            if stripped.startswith("- "):
                paths.append(stripped[2:].strip().strip('"').strip("'"))
            elif stripped == "":
                continue
            else:
                in_paths = False
    return paths, body


def glob_match(rel_path: str, pattern: str) -> bool:
    """Match repo-relative POSIX path against glob with `**` recursive support.

    gitignore-style semantics:
      - `foo/**`        → foo/anything (any depth)
      - `**/foo`        → foo at any depth
      - `foo/**/bar`    → foo/bar, foo/x/bar, foo/x/y/bar, ...
      - `foo/**/bar/**` → foo/bar/..., foo/x/bar/...
      - `*`             → one path segment (no `/`)
      - `?`             → one char (no `/`)
    """
    regex_parts: list[str] = []
    i = 0
    while i < len(pattern):
        if pattern[i:i + 3] == "**/":
            regex_parts.append("(?:.*/)?")
            i += 3
        elif pattern[i:i + 2] == "**":
            regex_parts.append(".*")
            i += 2
        elif pattern[i] == "*":
            regex_parts.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            regex_parts.append("[^/]")
            i += 1
        else:
            regex_parts.append(re.escape(pattern[i]))
            i += 1
    return re.match("^" + "".join(regex_parts) + "$", rel_path) is not None


def normalize_path(file_path_str: str) -> str | None:
    """Repo-relative POSIX path; None if outside repo or invalid."""
    try:
        p = pathlib.Path(file_path_str)
        if not p.is_absolute():
            p = (REPO_ROOT / p).resolve()
        else:
            p = p.resolve()
        rel = p.relative_to(REPO_ROOT)
        return rel.as_posix()
    except Exception:
        return None


def main() -> int:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        if not raw.strip():
            return 0
        data = json.loads(raw)
    except Exception as e:
        log(f"stdin parse failed: {e}")
        return 0

    tool_name = data.get("tool_name", "")
    if tool_name not in ALLOWED_TOOLS:
        return 0

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return 0

    rel_path = normalize_path(file_path)
    if not rel_path:
        log(f"path outside repo: {file_path}")
        return 0

    if not RULES_DIR.exists():
        return 0

    session_id = data.get("session_id", "default")
    session_marker_dir = STATE_DIR / session_id

    matched: list[tuple[str, str]] = []
    for rule_file in sorted(RULES_DIR.glob("*.md")):
        try:
            text = rule_file.read_text(encoding="utf-8")
        except Exception as e:
            log(f"rule read failed {rule_file.name}: {e}")
            continue
        paths, body = parse_frontmatter(text)
        if not paths:
            continue
        if not any(glob_match(rel_path, p) for p in paths):
            continue
        rule_name = rule_file.stem
        marker = session_marker_dir / rule_name
        if marker.exists():
            log(f"skip (already injected): {rule_name} for {rel_path}")
            continue
        try:
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.touch()
        except Exception as e:
            log(f"marker write failed {rule_name}: {e}")
        matched.append((rule_name, body.strip()))
        log(f"matched: {rule_name} for {rel_path}")

    if not matched:
        return 0

    parts = [
        f"Path-scoped rules now apply to `{rel_path}`. "
        "Comply on subsequent edits to this file and related GDD sections.",
        "",
    ]
    for name, body in matched:
        parts.append(f"## Active Rule: {name}")
        parts.append("")
        parts.append(body)
        parts.append("")
    additional_context = "\n".join(parts)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": additional_context,
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        log(f"uncaught: {traceback.format_exc()}")
        sys.exit(0)
