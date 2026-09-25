"""Behavioral checks for the Blender pack. Real Blender tests opt in with BLENDER_BIN."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins/blender-pack"
sys.path.insert(0, str(PACK / "scripts"))
import common
import runner
import mcp_server
import configure
import install_agents


class RunnerContract(unittest.TestCase):
    def test_user_roles_preserve_customization(self):
        with tempfile.TemporaryDirectory() as folder:
            install_agents.install(folder)
            path = Path(folder) / "agents/blender-pack--asset-reviewer.toml"
            path.write_text(path.read_text(encoding="utf-8") + "\n# custom\n", encoding="utf-8")
            actions = install_agents.install(folder)
            self.assertTrue(any("PRESERVE" in a for a in actions))
            self.assertIn("# custom", path.read_text(encoding="utf-8"))

    def test_project_enable_preserves_settings_and_rejects_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / ".claude/settings.json"
            common.write_json(path, {"permissions": {"allow": ["Read"]}, "enabledPlugins": {"unreal-pack@XGameHarness": True}})
            configure.enable_project(folder)
            settings = common.read_json(path)
            self.assertEqual(settings["permissions"], {"allow": ["Read"]})
            self.assertTrue(settings["enabledPlugins"]["unreal-pack@XGameHarness"])
            self.assertTrue(settings["enabledPlugins"]["blender-pack@XGameHarness"])
            configure.enable_project(folder)
            self.assertEqual(len(list(path.parent.glob("*.bak"))), 1)
            path.write_text('{"enabledPlugins":{},"enabledPlugins":{}}')
            with self.assertRaises(ValueError):
                configure.enable_project(folder)

    def test_workspace_escape_and_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                common.inside(folder, "../outside")
            self.assertEqual(common.inside(folder, "runs/x"), Path(folder).resolve() / "runs/x")

    def test_lock_rejects_other_process_then_recovers(self):
        with tempfile.TemporaryDirectory(prefix="xgh blender 中文 ") as folder:
            code = "import sys; sys.path.insert(0,sys.argv[1]); from common import workspace_lock;\nwith workspace_lock(sys.argv[2]): print('locked')"
            command = [sys.executable, "-c", code, str(PACK / "scripts"), folder]
            with common.workspace_lock(folder):
                blocked = subprocess.run(command, capture_output=True)
                self.assertNotEqual(blocked.returncode, 0)
                self.assertIn(b"occupied", blocked.stderr)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_mcp_stdio_discovery_errors_and_no_notification_reply(self):
        messages = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                    {"jsonrpc": "2.0", "method": "notifications/initialized"},
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "blender_job", "arguments": {"workspace": ".", "action": "delete"}}}]
        result = subprocess.run([sys.executable, str(PACK / "scripts/mcp_server.py")],
            input="\n".join(json.dumps(m) for m in messages) + "\n", capture_output=True, encoding="utf-8", timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        responses = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual([r["id"] for r in responses], [1, 2, 3])
        self.assertEqual(len(responses[1]["result"]["tools"]), 5)
        self.assertTrue(responses[2]["result"]["isError"])

    def test_image_path_confined_and_validated(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fake.png"
            path.write_text("not an image")
            with self.assertRaises(ValueError):
                mcp_server.call("blender_image", {"workspace": folder, "path": "../other.png"})
            with self.assertRaises(ValueError):
                mcp_server.call("blender_image", {"workspace": folder, "path": "fake.png"})

    def test_codex_blender_roles_preserve_customizations(self):
        with tempfile.TemporaryDirectory(prefix="xgh pack 中文 ") as folder:
            cli = [sys.executable, str(ROOT / "plugins/game-studio-core/scripts/harness.py"), "sync", "--project", folder, "--blender-root", str(PACK)]
            # The roster is delivered, never invented locally; without it sync exits 3.
            roster = Path(folder) / ".claude/team.json"
            roster.parent.mkdir(parents=True, exist_ok=True)
            roster.write_text('{"version":1,"identities":{"tester":{"git_users":["Harness Tester"],'
                              '"git_emails":["tester@example.invalid"],"role":"developer"}}}\n',
                              encoding="utf-8")
            first = subprocess.run(cli, capture_output=True, encoding="utf-8")
            self.assertEqual(first.returncode, 0, first.stderr)
            role = Path(folder) / ".codex/agents/blender-pack--asset-reviewer.toml"
            original = role.read_text(encoding="utf-8")
            self.assertIn("asset-reviewer", original)
            role.write_text(original + "\n# project customization\n", encoding="utf-8")
            second = subprocess.run(cli[:-2], capture_output=True, encoding="utf-8")
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("project customization", role.read_text(encoding="utf-8"))
            self.assertIn("blender-pack", common.read_json(Path(folder) / ".codex/harness.json")["sources"])


@unittest.skipUnless(os.environ.get("BLENDER_BIN"), "Set BLENDER_BIN to run real Blender integration")
class RealBlender(unittest.TestCase):
    def test_build_preserve_input_and_export_roundtrip(self):
        with tempfile.TemporaryDirectory(prefix="blender real 中文 ") as folder:
            build = runner.batch(folder, "build", script=PACK / "examples/crate.py")
            blend = Path(build["result"]["blend"])
            before = hashlib.sha256(blend.read_bytes()).hexdigest()
            inspection = runner.batch(folder, "inspect", blend=blend, max_triangles=1)
            self.assertGreater(inspection["result"]["triangles"], 1)
            self.assertFalse(inspection["result"]["within_triangle_budget"])
            for format in ("glb", "fbx"):
                exported = runner.batch(folder, "export", blend=blend, format=format)
                self.assertTrue(exported["result"]["reimport_has_meshes"])
                self.assertTrue(exported["result"]["comparison"]["bounds_match_1e_4"])
                self.assertTrue(exported["result"]["comparison"]["triangles_equal"])
                sources = common.read_json(exported["result"]["sources"])
                self.assertTrue(all(o["source_kind"] == "modeled" for o in sources["objects"]))
            edit = Path(folder) / "edit.py"
            edit.write_text("import bpy\nif __name__ == '__main__':\n bpy.data.objects['Body']['manual_note']='preserved'\n bpy.ops.mesh.primitive_cube_add()\n")
            edited = runner.batch(folder, "build", script=edit, blend=blend)
            self.assertGreater(edited["result"]["inspection"]["mesh_objects"], build["result"]["inspection"]["mesh_objects"])
            self.assertEqual(before, hashlib.sha256(blend.read_bytes()).hexdigest())

    def test_failure_and_timeout_leave_receipts(self):
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / "fail.py"
            script.write_text("raise RuntimeError('intentional failure')")
            with self.assertRaises(RuntimeError):
                runner.batch(folder, "build", script=script)
            script.write_text("import time; time.sleep(10)")
            with self.assertRaises(RuntimeError):
                runner.batch(folder, "build", script=script, timeout=1)
            receipts = [common.read_json(p) for p in Path(folder).glob("runs/*/receipt.json")]
            self.assertEqual(len(receipts), 2)
            self.assertTrue(any(r["timed_out"] for r in receipts))

    def test_live_ownership_exec_save_and_batch_lock(self):
        with tempfile.TemporaryDirectory(prefix="blender live 中文 ") as folder:
            started = runner.live_start(folder, "test-task", background=True)
            try:
                with self.assertRaises(RuntimeError):
                    runner.live_request(folder, "wrong-task", "status")
                with self.assertRaises(RuntimeError):
                    runner.batch(folder, "build", script=PACK / "examples/crate.py")
                result = runner.live_request(folder, "test-task", "exec", "bpy.ops.mesh.primitive_uv_sphere_add(); bpy.context.object.name='LiveSphere'")
                self.assertTrue(result["ok"])
                status = runner.live_request(folder, "test-task", "status")
                self.assertIn("LiveSphere", [o["name"] for o in status["result"]["objects"]])
                saved = runner.live_request(folder, "test-task", "save")
                self.assertTrue(Path(saved["result"]["blend"]).exists())
            finally:
                runner.live_request(folder, "test-task", "stop")
                for _ in range(100):
                    try:
                        with common.workspace_lock(folder):
                            break
                    except RuntimeError:
                        time.sleep(.1)
                else:
                    self.fail("Live process did not release workspace")
                time.sleep(.2)


if __name__ == "__main__":
    unittest.main()
