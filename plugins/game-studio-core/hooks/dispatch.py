#!/usr/bin/env python3
"""Codex hook adapter; Claude continues to use its existing handlers."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
from harness import digest, git, identity, load_json, project_root, read, safe_path

LEGACY = {
    "start": "session-start.sh", "gaps": "detect-gaps.sh",
    "git": "validate-git.sh", "rules": "inject-rules.py",
    "language": "inject-language-reminder.py", "suggest": "suggest-subagent.py",
    "compact": "pre-compact.sh", "end": "session-stop.sh",
}


def context(event: str, message: str):
    if message:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": event, "additionalContext": message
        }}, ensure_ascii=False))


def session_key(data: dict) -> str:
    # Session IDs are untrusted path components; never use them directly.
    return digest(str(data.get("session_id", "missing")))[:24]


def checkpoint(root: Path, data: dict, event: str):
    who = identity(root)
    if who is None:
        return  # never coalesce unrelated developers under unknown/
    key = session_key(data)
    folder = safe_path(root, f".codex/state/sessions/{who}/{key}")
    folder.mkdir(parents=True, exist_ok=True)
    active = safe_path(root, f"team/session-state/{who}/active.md")
    task = safe_path(root, f"team/session-state/{who}/sessions/{key}.md")
    record = {
        "event": event, "time": datetime.now(timezone.utc).isoformat(),
        "head": git(root, "rev-parse", "HEAD"),
        "status": git(root, "status", "--short"),
        "identity": who, "sessionKey": key,
        "activeFile": str(active.relative_to(root)),
        "taskFile": str(task.relative_to(root)),
    }
    # Snapshot uncommitted state as well; a HEAD pointer alone cannot restore it.
    for source in (active, task):
        if source.is_file():
            content = read(source)
            record[source.name + "Hash"] = digest(content)
            destination = folder / ("active.snapshot.md" if source == active else "task.snapshot.md")
            destination.write_text(content, encoding="utf-8")
    log = folder / "events.jsonl"
    if log.exists() and log.stat().st_size > 1024 * 1024:
        log.replace(folder / "events.previous.jsonl")
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def rule_paths(data: dict) -> list[str]:
    value = data.get("tool_input", {})
    if isinstance(value, str):
        patch, names = value, []
    elif isinstance(value, dict):
        names = [value["file_path"]] if isinstance(value.get("file_path"), str) else []
        patch = value.get("patch", value.get("input", ""))
    else:
        return []
    if isinstance(patch, str):
        names.extend(re.findall(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$", patch, re.M))
    return list(dict.fromkeys(names))


def rules_context(root: Path, data: dict) -> str:
    # Reuse tested glob semantics without running the legacy hook main function.
    spec = importlib.util.spec_from_file_location("rule_parser", PLUGIN / "hooks/inject-rules.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    paths = []
    cwd = Path(data.get("cwd") or root).resolve()
    for item in rule_paths(data):
        try:
            paths.append((cwd / item).resolve().relative_to(root).as_posix())
        except ValueError:
            continue
    matched = []
    for path in sorted((root / ".claude/rules").glob("*.md")):
        patterns, _body = module.parse_frontmatter(read(path))
        if any(module.glob_match(name, pattern) for name in paths for pattern in patterns):
            matched.append(path.relative_to(root).as_posix())
    return ("编辑前读取并遵守匹配的项目规则：\n" + "\n".join(matched)) if matched else ""


def validate_git(root: Path, data: dict) -> tuple[list[str], list[str]]:
    value = data.get("tool_input", {})
    if not isinstance(value, dict):
        return [], []
    command = value.get("command", value.get("cmd", ""))
    if not isinstance(command, str):
        return [], []
    # Advisory recognizer, not a shell parser/security boundary. Never execute input.
    match = re.search(r"(?:^|[;&|\n])\s*(?:[A-Za-z_]\w*=\S+\s+)*git(?:\.exe)?\s+(?:-C\s+(?:\"([^\"]+)\"|'([^']+)'|(\S+))\s+)?(commit|push)\b", command)
    if not match:
        return [], []
    cwd = Path(value.get("workdir") or data.get("cwd") or root).resolve()
    target_arg = next((s for s in match.groups()[:3] if s), None)
    target = (cwd / target_arg).resolve() if target_arg else cwd
    # cd/Set-Location and script indirection are ambiguous; do not check the wrong index.
    if re.search(r"\b(cd|Set-Location|Push-Location)\b", command[:match.start()], re.I):
        return [], ["Git 校验未执行：命令先改变目录。请在明确的 workdir 中运行 git。"]
    if match.group(4) == "push":
        return [], ["推送前确认本次构建／测试证据和目标分支。hook 不代表发布授权。"]
    result = subprocess.run(["git", "-C", str(target), "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"],
                            capture_output=True, timeout=10)
    if result.returncode:
        return [], ["Git 暂存区不可读，校验未执行。"]
    errors, warnings = [], []
    staged = result.stdout.decode("utf-8", errors="replace").split("\0")
    who = identity(project_root(target))
    team = load_json(project_root(target) / ".claude/team.json")
    admin = team.get("identities", {}).get(who, {}).get("role") == "admin"
    for name in filter(None, staged):
        if name.startswith("team/session-state/") and who and not admin and not name.startswith(f"team/session-state/{who}/"):
            warnings.append("涉及其他成员的会话状态：" + name)
        if name.endswith(".json"):
            blob = subprocess.run(["git", "-C", str(target), "show", ":" + name], capture_output=True, timeout=10)
            if blob.returncode:
                warnings.append("无法读取暂存文件：" + name)
                continue
            try:
                json.loads(blob.stdout.decode("utf-8-sig"))
            except (ValueError, UnicodeError) as exc:
                errors.append(f"{name}: {exc}")
    for pack in sorted({n.split('/')[1] for n in staged if n.startswith('plugins/') and n.count('/') > 2}):
        versions = []
        for host in ("claude", "codex"):
            file = f"plugins/{pack}/.{host}-plugin/plugin.json"
            text = git(target, "show", ":" + file)
            if text:
                try:
                    versions.append(json.loads(text).get("version"))
                    previous = git(target, "show", "HEAD:" + file)
                    if previous and json.loads(previous).get("version") == versions[-1]:
                        warnings.append(f"{pack} ({host}) 内容改变但 version 未更新")
                except ValueError:
                    pass  # malformed staged JSON already blocks above
        if len(versions) == 2 and versions[0] != versions[1]:
            warnings.append(f"{pack}: Claude/Codex version 不一致")
    return errors, warnings


def codex(action: str, data: dict) -> int:
    root = project_root(data.get("cwd") or os.getcwd())
    event = data.get("hook_event_name") or {
        "start": "SessionStart", "gaps": "SessionStart", "git": "PreToolUse",
        "rules": "PostToolUse", "language": "UserPromptSubmit", "suggest": "UserPromptSubmit",
        "compact": "PreCompact", "end": "SessionEnd", "checkpoint": "Stop"
    }[action]
    if action == "start":
        who = identity(root)
        message = [f"XGameHarness Codex | project={root} | identity={who or 'unresolved'}",
                   "默认中文。按任务选择已安装技能；无 Skill 工具时读取 SKILL.md。",
                   "遵守项目 AGENTS.md；编辑前按 paths 读取 .claude/rules/*.md。",
                   f"运行时说明：{PLUGIN / 'docs/codex-runtime.md'}",
                   f"当前任务状态路径：team/session-state/{who or '<identity>'}/sessions/{session_key(data)}.md"]
        if who:
            active = safe_path(root, f"team/session-state/{who}/active.md")
            if active.exists():
                message += [f"恢复摘要 {active}（使用前核验当前文件和 Git）：", read(active)[:1800]]
            task = safe_path(root, f"team/session-state/{who}/sessions/{session_key(data)}.md")
            if task.exists():
                message += [f"本任务摘要 {task}：", read(task)[:1800]]
            snapshots = root / f".codex/state/sessions/{who}/{session_key(data)}"
            if snapshots.exists():
                message.append(f"本地检查点（含未提交摘要快照）：{snapshots}")
        else:
            message.append("请映射 .claude/team.json；身份未知时禁止自动写入共享记忆。")
        context(event, "\n".join(message))
    elif action == "gaps":
        missing = [p for p in ("AGENTS.md", "plan/stage.md", ".claude/team.json", ".codex/harness.json") if not (root / p).exists()]
        context(event, "项目接入缺项：" + ", ".join(missing) + "；运行 $project-init。" if missing else "")
    elif action == "language":
        context(event, "默认使用中文回复，保留代码标识符和日志原文。")
    elif action == "suggest":
        # Advertise only roles that have actually been installed in this project.
        prompt = str(data.get("prompt", "")).lower()
        config = load_json(root / ".claude/harness-config.json")
        excluded = config.get("excludedAgents", [])
        spec = importlib.util.spec_from_file_location("suggestions", PLUGIN / "hooks/suggest-subagent.py")
        suggestions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(suggestions)
        hints = {role: keywords for _pack, role, _label, _doc, keywords in suggestions.AGENT_RULES}
        found = []
        for path in sorted((root / ".codex/agents").glob("*.toml")):
            role = path.stem.split("--")[-1]
            if role in excluded or path.stem in excluded or path.stem.replace("--", ":", 1) in excluded:
                continue
            if any(suggestions._keyword_hit(key, prompt) for key in hints.get(role, ())):
                found.append(path.stem)
        context(event, "可用专家：" + ", ".join(found) + "。仅在当前任务授权委派时调用。" if found else "")
    elif action == "rules":
        context(event, rules_context(root, data))
    elif action == "git":
        errors, warnings = validate_git(root, data)
        if warnings:
            context(event, "\n".join(warnings))
        if errors:
            print("Invalid staged JSON:\n" + "\n".join(errors), file=sys.stderr)
            return 2
    elif action in ("compact", "checkpoint", "end"):
        checkpoint(root, data, event)
        if action == "compact":
            context(event, "机械检查点已尝试保存到 .codex/state/sessions/。压缩后读取本任务摘要与 active.md，核验 Git；不要把检查点当作语义记忆。")
    return 0


def main() -> int:
    action = sys.argv[1]
    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
    if not isinstance(data, dict):
        raise ValueError("hook payload must be a JSON object")
    is_codex = bool(os.environ.get("PLUGIN_ROOT") or os.environ.get("CODEX_THREAD_ID") or data.get("model"))
    if is_codex:
        return codex(action, data)
    if action == "checkpoint":
        return 0  # Claude's existing session end behavior remains unchanged.
    if action == "rules" and data.get("hook_event_name") == "PreToolUse":
        return 0  # The legacy rule injector only emits PostToolUse output.
    path = PLUGIN / "hooks" / LEGACY[action]
    command = [sys.executable, str(path)] if path.suffix == ".py" else ["bash", str(path)]
    return subprocess.run(command, input=raw, encoding="utf-8", cwd=data.get("cwd") or os.getcwd()).returncode


if __name__ == "__main__":
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f"XGameHarness hook failed (check not completed): {exc}", file=sys.stderr)
        sys.exit(1)
