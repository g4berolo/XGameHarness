"""Behavioral integration tests with isolated Git projects; no model/API calls."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "plugins/game-studio-core"
CLI = CORE / "scripts/harness.py"
HOOK = CORE / "hooks/dispatch.py"


class CodexIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="xgh space 中文 ")
        self.project = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Harness Tester")
        self.git("config", "user.email", "tester@example.invalid")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.project), *args], check=True, capture_output=True)

    def cli(self, *args, ok=True):
        proc = subprocess.run([sys.executable, str(CLI), *args, "--project", str(self.project)],
                              capture_output=True, encoding="utf-8")
        if ok:
            self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc

    def write_roster(self, key="tester", root: Path | None = None):
        """The roster is owned upstream; every runtime now receives it, never invents it."""
        path = (root or self.project) / ".claude/team.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"version": 1, "identities": {key: {
            "git_users": ["Harness Tester"], "git_emails": ["tester@example.invalid"],
            "role": "developer"}}}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def init(self):
        self.write_roster()
        self.cli("init", "--unreal-root", str(ROOT / "plugins/unreal-pack"))

    def hook(self, action, data=None):
        payload = {"cwd": str(self.project), "session_id": "thread-a", "model": "test"}
        payload.update(data or {})
        env = dict(os.environ, PLUGIN_ROOT=str(CORE), PYTHONIOENCODING="utf-8")
        return subprocess.run([sys.executable, str(HOOK), action], input=json.dumps(payload),
                              env=env, capture_output=True, encoding="utf-8")

    def test_init_dry_run_and_idempotent_upgrade(self):
        self.write_roster()
        self.cli("init", "--dry-run")
        self.assertFalse((self.project / "AGENTS.md").exists())
        (self.project / "AGENTS.md").write_text("# Existing project\nKeep this.\n", encoding="utf-8")
        self.init()
        files = list((self.project / ".codex/agents").glob("*.toml"))
        self.assertEqual(len(files), 13)
        for path in files:
            agent = tomllib.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(agent["developer_instructions"])
            self.assertNotIn("model", agent)
            self.assertNotIn("memory", agent)
        before = {str(p): p.read_bytes() for p in self.project.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.cli("sync")
        after = {str(p): p.read_bytes() for p in self.project.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.assertEqual(before, after)
        self.assertIn("Keep this.", (self.project / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertIn(self.project.name, (self.project / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertNotIn("[日期]", (self.project / "plan/stage.md").read_text(encoding="utf-8"))
        self.cli("doctor")

    def test_doctor_detects_missing_generated_agent(self):
        self.init()
        (self.project / ".codex/agents/game-studio-core--producer.toml").unlink()
        result = self.cli("doctor", ok=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("MISSING managed file", result.stdout)

    def test_customized_rules_agents_and_block_preserved(self):
        self.init()
        rule = self.project / ".claude/rules/design-docs.md"
        rule.write_text("# Custom rule\n", encoding="utf-8")
        agent = self.project / ".codex/agents/game-studio-core--producer.toml"
        agent.write_text(agent.read_text(encoding="utf-8") + "\n# Local change\n", encoding="utf-8")
        entry = self.project / "AGENTS.md"
        entry.write_text(entry.read_text(encoding="utf-8").replace("默认中文", "默认英文"), encoding="utf-8")
        out = self.cli("sync").stdout
        self.assertIn("PRESERVE", out)
        self.assertEqual(rule.read_text(encoding="utf-8"), "# Custom rule\n")
        self.assertIn("Local change", agent.read_text(encoding="utf-8"))
        self.assertIn("默认英文", entry.read_text(encoding="utf-8"))

    def test_patch_rules_multiple_files_and_move(self):
        self.init()
        child = self.project / "client"
        child.mkdir()
        custom = self.project / ".claude/rules/custom.md"
        custom.write_text('---\npaths:\n  - "client/src/**"\n---\nCustom\n', encoding="utf-8")
        result = self.hook("rules", {"cwd": str(child), "hook_event_name": "PreToolUse", "tool_name": "apply_patch",
            "tool_input": {"input": "*** Begin Patch\n*** Update File: src/a.cpp\n*** Move to: src/b.cpp\n*** Add File: ../design/gdd/test.md\n*** End Patch"}})
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")
        self.assertIn("custom.md", output["additionalContext"])
        self.assertIn("design-docs.md", output["additionalContext"])

    def test_checkpoint_uncommitted_and_session_isolation(self):
        self.init()
        active = self.project / "team/session-state/tester/active.md"
        active.parent.mkdir(parents=True)
        active.write_text("Uncommitted recovery\n", encoding="utf-8")
        for sid in ("one", "../../escape"):
            result = self.hook("checkpoint", {"session_id": sid})
            self.assertEqual(result.returncode, 0, result.stderr)
        snapshots = list((self.project / ".codex/state/sessions/tester").glob("*/active.snapshot.md"))
        self.assertEqual(len(snapshots), 2)
        self.assertTrue(all(p.read_text(encoding="utf-8") == "Uncommitted recovery\n" for p in snapshots))

    def test_unknown_identity_does_not_write_shared_memory(self):
        result = self.hook("end")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.project / "team").exists())
        self.assertFalse((self.project / ".codex/state").exists())

    def test_staged_json_not_worktree_and_delete(self):
        path = self.project / "data.json"
        path.write_text('{"ok":true}', encoding="utf-8")
        self.git("add", "data.json")
        path.write_text("{bad", encoding="utf-8")
        self.assertEqual(self.hook("git", {"tool_input": {"cmd": "git commit -m test"}}).returncode, 0)
        self.git("add", "data.json")
        path.write_text('{"ok":true}', encoding="utf-8")
        result = self.hook("git", {"tool_input": {"command": "git commit -m test"}})
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_malformed_payload_visible_failure(self):
        result = subprocess.run([sys.executable, str(HOOK), "start"], input="{invalid",
                                capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertIn("check not completed", result.stderr)

    def test_start_from_subdirectory(self):
        self.init()
        child = self.project / "client/Source"
        child.mkdir(parents=True)
        result = self.hook("start", {"cwd": str(child)})
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("identity=tester", output)
        self.assertIn(str(self.project.resolve()), output)

    def test_identity_flag_removed_no_partial_writes(self):
        # Local self-registration is gone: a rejected flag must not half-configure a project.
        result = self.cli("init", "--identity", "tester", ok=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--identity", result.stderr)
        self.assertFalse((self.project / ".codex").exists())
        self.assertFalse((self.project / ".claude").exists())

    def test_init_without_roster_reports_needs_roster(self):
        result = self.cli("init", ok=False)
        self.assertEqual(result.returncode, 3)
        self.assertIn("NEEDS-ROSTER", result.stderr)
        self.assertFalse((self.project / ".claude/team.json").exists())
        # Everything else is still written; a half-configured project is worse.
        for rel in ("AGENTS.md", ".claude/settings.json", "plan/stage.md", ".codex/harness.json"):
            self.assertTrue((self.project / rel).is_file(), rel)
        self.assertEqual(len(list((self.project / ".codex/agents").glob("*.toml"))), 8)

    def test_settings_enables_only_installed_packs(self):
        self.write_roster()
        self.cli("init")
        data = json.loads((self.project / ".claude/settings.json").read_text(encoding="utf-8"))
        self.assertEqual(list(data["enabledPlugins"]), ["game-studio-core@XGameHarness"])
        self.assertIn("XGameHarness", data["extraKnownMarketplaces"])
        self.assertIn("Bash(git status*)", data["permissions"]["allow"])

    def test_settings_covers_unreal_and_is_never_overwritten(self):
        self.init()
        path = self.project / ".claude/settings.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(set(data["enabledPlugins"]),
                         {"game-studio-core@XGameHarness", "unreal-pack@XGameHarness"})
        data["permissions"]["allow"].append("Bash(team custom*)")
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        out = self.cli("sync").stdout
        self.assertNotIn("PRESERVE", out)
        self.assertNotIn("settings.json", out)
        self.assertIn("Bash(team custom*)",
                      json.loads(path.read_text(encoding="utf-8"))["permissions"]["allow"])

    def test_doctor_detects_missing_settings(self):
        self.init()
        (self.project / ".claude/settings.json").unlink()
        result = self.cli("doctor", ok=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("MISSING .claude/settings.json", result.stdout)

    def test_sources_keyed_by_pack_name_not_directory(self):
        # The installed cache directory is a version string, not the pack name.
        with tempfile.TemporaryDirectory(prefix="xgh cache ") as cache_root:
            cache = Path(cache_root) / "9.9.9"
            shutil.copytree(ROOT / "plugins/unreal-pack", cache)
            self.write_roster()
            self.cli("init", "--unreal-root", str(cache))
            state = json.loads((self.project / ".codex/harness.json").read_text(encoding="utf-8"))
            self.assertEqual(set(state["sources"]), {"game-studio-core", "unreal-pack"})
            self.assertEqual(state["sources"]["unreal-pack"], str(cache))
            self.assertIn("unreal-pack@XGameHarness", json.loads(
                (self.project / ".claude/settings.json").read_text(encoding="utf-8"))["enabledPlugins"])
            # A later sync without --unreal-root must still find the recorded source.
            self.cli("sync")
            self.assertEqual(len(list((self.project / ".codex/agents").glob("*.toml"))), 13)
            self.cli("doctor")

    def test_roster_fetch_overwrites_cache_and_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory(prefix="xgh docs ") as docs_dir:
            docs = Path(docs_dir)

            def docs_git(*args):
                subprocess.run(["git", "-C", str(docs), *args], check=True, capture_output=True)

            subprocess.run(["git", "init", "-q", str(docs)], check=True, capture_output=True)
            docs_git("config", "user.name", "Roster Owner")
            docs_git("config", "user.email", "owner@example.invalid")
            upstream = self.write_roster(root=docs)
            docs_git("add", "-A")
            docs_git("commit", "-qm", "roster")
            self.assertIn("CREATE .claude/team.json", self.cli("roster", "--from", str(docs)).stdout)
            state = json.loads((self.project / ".codex/harness.json").read_text(encoding="utf-8"))
            self.assertEqual(state["roster"]["remote"], str(docs))
            local = self.project / ".claude/team.json"
            self.assertIn("Roster already current", self.cli("roster").stdout)
            # Authority is upstream: a local edit is a stale cache, not a customization.
            local.write_text('{"version":1,"identities":{"tester":{"git_users":[],'
                             '"git_emails":[],"role":"lead"}}}\n', encoding="utf-8")
            self.assertIn("OVERWRITE", self.cli("roster").stdout)
            self.assertIn("Harness Tester", local.read_text(encoding="utf-8"))
            # Broken upstream JSON must not destroy a working local copy.
            upstream.write_text("{bad", encoding="utf-8")
            docs_git("commit", "-qam", "break")
            failed = self.cli("roster", ok=False)
            self.assertEqual(failed.returncode, 1)
            self.assertIn("not valid JSON", failed.stderr)
            self.assertIn("Harness Tester", local.read_text(encoding="utf-8"))

    def test_registered_windows_commands(self):
        if os.name != "nt":
            self.skipTest("Windows command override")
        self.init()
        hooks = json.loads((CORE / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]
        for event, groups in hooks.items():
            for group in groups:
                for handler in group["hooks"]:
                    payload = {"cwd": str(self.project), "session_id": "windows-smoke", "hook_event_name": event,
                               "tool_input": {"input": "*** Add File: design/gdd/test.md"}, "prompt": "排期"}
                    result = subprocess.run(handler["commandWindows"], shell=True, input=json.dumps(payload),
                        env=dict(os.environ, PLUGIN_ROOT=str(CORE)), capture_output=True, encoding="utf-8", timeout=20)
                    self.assertEqual(result.returncode, 0, event + ": " + result.stderr)
                    if result.stdout:
                        self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["hookEventName"], event)

    def test_suggestion_only_installed_roles_and_exclusions(self):
        self.write_roster()
        self.cli("init")
        self.assertEqual(self.hook("suggest", {"prompt": "Gameplay Ability System"}).stdout, "")
        self.assertIn("systems-designer", self.hook("suggest", {"prompt": "数值公式"}).stdout)
        (self.project / ".claude/harness-config.json").write_text(
            '{"excludedAgents":["game-studio-core:systems-designer"]}', encoding="utf-8")
        self.assertEqual(self.hook("suggest", {"prompt": "数值公式"}).stdout, "")
        self.assertEqual(self.hook("suggest", {"prompt": "explore grpc"}).stdout, "")

    def test_git_other_workdir_and_echo_not_a_commit(self):
        bad = self.project / "bad.json"
        bad.write_text("{bad", encoding="utf-8")
        self.git("add", "bad.json")
        self.assertEqual(self.hook("git", {"tool_input": {"command": 'echo "git commit"'}}).returncode, 0)
        other = self.project / "another repo"
        other.mkdir()
        subprocess.run(["git", "init", "-q", str(other)], check=True, capture_output=True)
        self.assertEqual(self.hook("git", {"tool_input": {"cmd": "git commit -m test", "workdir": str(other)}}).returncode, 0)
        self.assertEqual(self.hook("git", {"tool_input": {"cmd": f'git -C "{other}" commit -m test'}}).returncode, 0)

    def test_claude_python_dispatch_preserved(self):
        env = dict(os.environ)
        env.pop("PLUGIN_ROOT", None)
        env.pop("CODEX_THREAD_ID", None)
        result = subprocess.run([sys.executable, str(HOOK), "language"], input='{}', env=env,
                                capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")

    def test_non_object_payload(self):
        result = subprocess.run([sys.executable, str(HOOK), "start"], input='[]',
                                capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertIn("JSON object", result.stderr)


if __name__ == "__main__":
    unittest.main()
