#!/usr/bin/env python3
"""Repository packaging invariants, without external Python dependencies."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate():
    count = 0
    market = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
    assert market["name"] == "XGameHarness"
    for entry in market["plugins"]:
        assert entry["policy"]["installation"] == "AVAILABLE"
        assert entry["policy"]["authentication"] == "ON_INSTALL"
        pack = ROOT / entry["source"]["path"]
        assert pack.resolve().is_relative_to(ROOT)
        codex = json.loads((pack / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((pack / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        assert codex["name"] == claude["name"] == entry["name"] == pack.name
        assert codex["version"] == claude["version"], pack
        assert (pack / codex["skills"]).is_dir()
        for skill in (pack / codex["skills"]).glob("*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            assert text.startswith("---\n"), skill
            front = text.split("---", 2)[1]
            assert re.search(r"^name:\s*\S", front, re.M), skill
            assert re.search(r"^description:\s*\S", front, re.M), skill
            if skill.parent.name != "archify":
                assert "只有 Claude Code 会设这个变量" not in text, skill
            count += 1
    hooks = json.loads((ROOT / "plugins/game-studio-core/hooks/hooks.json").read_text(encoding="utf-8"))
    for groups in hooks["hooks"].values():
        for group in groups:
            for hook in group["hooks"]:
                assert "dispatch.py" in hook["command"]
                assert "PLUGIN_ROOT" in hook["commandWindows"]
    print(f"Packaging OK: {len(market['plugins'])} plugins, {count} skills, dual-host versions, hook commands")


if __name__ == "__main__":
    try:
        validate()
    except (AssertionError, KeyError, ValueError, OSError) as exc:
        print(f"Packaging FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
