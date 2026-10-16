"""Blender batch jobs and live-session client. All output revisions are new directories."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import urllib.request
import uuid
from common import PACK, blender_bin, inside, process_options, read_json, workspace_lock, write_json


def doctor(executable=None):
    exe = blender_bin(executable)
    result = subprocess.run([exe, "--version"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30, **process_options())
    if result.returncode:
        raise RuntimeError(result.stderr)
    return {"executable": exe, "version": result.stdout.splitlines()[0], "python": sys.version.split()[0]}


def batch(workspace, action, script=None, blend=None, executable=None, timeout=180, **options):
    root = Path(workspace).resolve()
    if action not in {"build", "inspect", "preview", "export"}:
        raise ValueError("Unknown action")
    if not 1 <= timeout <= 3600:
        raise ValueError("timeout must be 1..3600 seconds")
    if action == "build" and not script:
        raise ValueError("build requires a Python script")
    if action != "build" and not blend:
        raise ValueError(f"{action} requires an existing .blend file")
    script_path = Path(script).resolve() if script else None
    blend_path = Path(blend).resolve() if blend else None
    for path in (script_path, blend_path):
        if path and not path.is_file():
            raise ValueError(f"Input does not exist: {path}")
    exe = blender_bin(executable)
    with workspace_lock(root):
        job = inside(root, "runs/" + time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8])
        job.mkdir(parents=True)
        if script_path:
            # Snapshot exactly what ran, without changing the source file.
            (job / "source.py").write_bytes(script_path.read_bytes())
        config = {"action": action, "workspace": str(root), "job": str(job),
                  "script": str(script_path) if script_path else None,
                  "blend": str(blend_path) if blend_path else None, **options}
        write_json(job / "request.json", config)
        command = [exe, "--background", "--factory-startup", "--disable-autoexec"]
        if blend_path:
            command.append(str(blend_path))
        command += ["--python-exit-code", "1", "--python", str(PACK / "scripts/worker.py"), "--", str(job / "request.json")]
        started = time.monotonic()
        with (job / "blender.log").open("w", encoding="utf-8") as log:
            try:
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, cwd=root,
                                        timeout=timeout, **process_options())
                code = result.returncode
            except subprocess.TimeoutExpired:
                code = -1
        receipt = {"ok": code == 0 and (job / "result.json").is_file(), "exit_code": code,
                   "job": str(job), "seconds": round(time.monotonic() - started, 2),
                   "log": str(job / "blender.log"), "timed_out": code == -1}
        if script_path:
            receipt["script_sha256"] = hashlib.sha256((job / "source.py").read_bytes()).hexdigest()
        if receipt["ok"]:
            receipt["result"] = read_json(job / "result.json")
        write_json(job / "receipt.json", receipt)
        if not receipt["ok"]:
            raise RuntimeError(f"Blender job failed; inspect {job / 'receipt.json'} and blender.log")
        return receipt


def live_request(workspace, owner, action, script=None, timeout=120):
    root = Path(workspace).resolve()
    info = read_json(inside(root, ".xgh-live.json"))
    if info["owner"] != owner:
        raise RuntimeError("Live scene belongs to another task; do not borrow its owner ID.")
    data = json.dumps({"action": action, "script": script}).encode()
    request = urllib.request.Request(f"http://127.0.0.1:{info['port']}/", data=data,
        headers={"Authorization": "Bearer " + info["token"], "Content-Type": "application/json"})
    # Ignore user HTTP proxies for this authenticated loopback-only connection.
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=timeout) as response:
        result = json.load(response)
    if not result.get("ok"):
        raise RuntimeError(result.get("error", "Live command failed"))
    return result


def live_start(workspace, owner, blend=None, executable=None, background=False):
    if not owner or len(owner) > 160:
        raise ValueError("A task-specific owner ID is required")
    root = Path(workspace).resolve()
    # The child holds the same lock for its entire lifetime. Parent never removes it.
    with workspace_lock(root):
        job = inside(root, "runs/live-" + uuid.uuid4().hex)
        job.mkdir(parents=True)
        if blend and not Path(blend).is_file():
            raise ValueError("Input .blend does not exist")
        write_json(job / "request.json", {"workspace": str(root), "owner": owner, "job": str(job)})
        ready = job / "ready.json"
        command = [blender_bin(executable), "--factory-startup", "--disable-autoexec"]
        if background:
            command += ["--background"]
        if blend:
            command += [str(Path(blend).resolve())]
        command += ["--python-exit-code", "1", "--python", str(PACK / "scripts/live_bridge.py"), "--", str(job / "request.json")]
    # A competing starter is safe: the child's acquisition decides the winner.
    with (job / "blender.log").open("w", encoding="utf-8") as log:
        proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, cwd=root, **process_options())
    for _ in range(150):
        if ready.exists():
            # Reap the child in long-lived MCP/test hosts; keep it alive after CLI exits.
            threading.Thread(target=proc.wait, daemon=True).start()
            return {"ok": True, "workspace": str(root), "owner": owner, "pid": proc.pid, "job": str(job)}
        if proc.poll() is not None:
            raise RuntimeError(f"Blender live session exited; read {job / 'blender.log'}")
        time.sleep(.2)
    # No untracked delayed startup after reporting failure.
    proc.terminate()
    proc.wait(timeout=10)
    raise RuntimeError(f"Blender did not become ready within 30s; read {job / 'blender.log'}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["doctor", "build", "inspect", "preview", "export", "live-start", "live-status", "live-exec", "live-save", "live-stop"])
    p.add_argument("--workspace")
    p.add_argument("--script")
    p.add_argument("--blend")
    p.add_argument("--blender")
    p.add_argument("--owner")
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--format", choices=["glb", "fbx"], default="glb")
    p.add_argument("--max-triangles", type=int)
    args = p.parse_args()
    if args.action == "doctor":
        result = doctor(args.blender)
    elif not args.workspace:
        p.error("--workspace is required")
    elif args.action == "live-start":
        result = live_start(args.workspace, args.owner, args.blend, args.blender)
    elif args.action.startswith("live-"):
        source = Path(args.script).read_text(encoding="utf-8-sig") if args.script else None
        if args.action == "live-exec" and source is None:
            p.error("live-exec requires --script")
        result = live_request(args.workspace, args.owner, args.action[5:], source, args.timeout)
    else:
        result = batch(args.workspace, args.action, args.script, args.blend, args.blender, args.timeout,
                       format=args.format, max_triangles=args.max_triangles)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
