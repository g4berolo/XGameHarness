"""Set a verified local Blender executable without touching model/account settings."""
import argparse
import json
from pathlib import Path
from common import read_json, write_json
from runner import doctor


def enable_project(project):
    root = Path(project).resolve()
    if not root.is_dir():
        raise ValueError("Project must exist")
    path = root / ".claude/settings.json"
    if path.exists():
        def unique(pairs):
            obj = {}
            for key, value in pairs:
                if key in obj:
                    raise ValueError(f"Duplicate settings key: {key}; resolve before merging")
                obj[key] = value
            return obj
        old = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique)
    else:
        old = {}
    plugins = old.setdefault("enabledPlugins", {})
    if not isinstance(plugins, dict):
        raise ValueError("enabledPlugins must be an object")
    if plugins.get("blender-pack@XGameHarness") is True:
        return
    if path.exists():
        import uuid
        backup = path.with_name("settings.json.before-blender-" + uuid.uuid4().hex[:8] + ".bak")
        backup.write_bytes(path.read_bytes())
    plugins["blender-pack@XGameHarness"] = True
    write_json(path, old)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", required=True)
    parser.add_argument("--project", help="Optional XGameHarnessUI project to enable this pack")
    args = parser.parse_args()
    info = doctor(args.blender)
    if args.project:
        enable_project(args.project)
    path = Path.home() / ".xgh/blender.json"
    old = read_json(path) if path.exists() else {}
    old["executable"] = info["executable"]
    write_json(path, old)
    print(f"Configured {info['version']}: {path}")
