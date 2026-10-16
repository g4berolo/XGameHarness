"""Install only this pack's two Codex roles; preserve local customizations."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tomllib
from common import PACK, inside, read_json, write_json


def install(home):
    home = Path(home).resolve()
    state_path = inside(home, "blender-pack-agents.json")
    state = read_json(state_path) if state_path.exists() else {}
    actions = []
    for source in sorted((PACK / "agents").glob("*.md")):
        _, front, body = source.read_text(encoding="utf-8").split("---", 2)
        description = json.loads(re.search(r"^description:\s*(.+)$", front, re.M).group(1))
        name = "blender-pack--" + source.stem
        text = f"name = {json.dumps(name)}\ndescription = {json.dumps(description, ensure_ascii=False)}\n"
        body = f"Plugin root: {PACK.as_posix()}. Resolve role reference paths from this root. Follow current task permissions; inherit host model and sandbox.\n\n" + body.strip()
        text += "developer_instructions = " + json.dumps(body, ensure_ascii=False) + "\n"
        tomllib.loads(text)
        path = inside(home, "agents/" + name + ".toml")
        old = path.read_text(encoding="utf-8") if path.exists() else None
        sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
        if old is not None and old != text and state.get(name) != sha(old):
            actions.append("PRESERVE customized " + str(path))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        state[name] = sha(text)
        actions.append("INSTALLED " + str(path))
    write_json(state_path, state)
    return actions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", required=True, help="Exact Codex home for the intended user/account")
    args = parser.parse_args()
    print("\n".join(install(args.home)))
