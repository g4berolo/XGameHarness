"""Read-only Codex app-server skill/MCP discovery. Does not send a model prompt."""
import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading


def probe(home, cwd):
    proc = subprocess.Popen(["codex", "app-server"], env=dict(os.environ, CODEX_HOME=str(home)),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        encoding="utf-8", text=True, **({"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}))
    messages = queue.Queue()
    errors = []
    def read():
        for line in proc.stdout:
            try:
                messages.put(json.loads(line))
            except ValueError:
                pass
    threading.Thread(target=read, daemon=True).start()
    threading.Thread(target=lambda: errors.extend(proc.stderr), daemon=True).start()
    def send(method, params, id=None):
        value = {"method": method, "params": params}
        if id is not None:
            value["id"] = id
        proc.stdin.write(json.dumps(value) + "\n")
        proc.stdin.flush()
        if id is not None:
            while True:
                msg = messages.get(timeout=40)
                if msg.get("id") == id:
                    if "error" in msg:
                        raise RuntimeError(msg["error"])
                    return msg["result"]
    try:
        send("initialize", {"clientInfo": {"name": "xgh-blender-probe", "version": "1.0"}}, 1)
        send("initialized", {})
        skills = send("skills/list", {"cwds": [str(cwd)], "forceReload": True}, 2)
        servers = send("mcpServerStatus/list", {}, 3)
        selected = [s for data in skills.get("data", []) for s in data.get("skills", []) if "blender-workflow" in s["name"]]
        server = next((s for s in servers.get("data", []) if s["name"] == "xgh-blender"), {})
        return {"skills": selected, "mcp": server, "ok": bool(selected and len(server.get("tools", {})) == 5 and not server.get("toolsError"))}
    finally:
        proc.terminate()
        proc.wait(timeout=10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", required=True)
    parser.add_argument("--cwd", default=".")
    args = parser.parse_args()
    result = probe(args.home, Path(args.cwd).resolve())
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["ok"] else 1)
