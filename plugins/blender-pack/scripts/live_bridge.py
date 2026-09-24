"""Dedicated Blender instance: loopback HTTP + token, main-thread bpy, one task owner."""
from __future__ import annotations
import contextlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import queue
import secrets
import sys
import threading
import time
import traceback
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from common import inside, read_json, workspace_lock, write_json
from worker import inspect_scene

config = read_json(sys.argv[sys.argv.index("--") + 1])
root, job = Path(config["workspace"]), Path(config["job"])
lock = workspace_lock(root)
lock.__enter__()
token = secrets.token_urlsafe(32)
pending = queue.Queue(maxsize=8)
stopping = False


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        if self.headers.get("Origin") or not hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + token):
            self.send_error(403)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 1024 * 1024:
                raise ValueError("Invalid request size")
            data = json.loads(self.rfile.read(size))
            event = threading.Event()
            item = {"data": data, "event": event, "result": None, "cancelled": False}
            pending.put_nowait(item)
            if not event.wait(115):
                # An already-running script cannot be rolled back. Never retry blindly.
                item["cancelled"] = True
                result = {"ok": False, "error": "Timed out; execution may have started. Inspect scene and logs before retrying."}
            else:
                result = item["result"]
            body = json.dumps(result, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ValueError, queue.Full):
            self.send_error(400)
        except (BrokenPipeError, ConnectionResetError):
            pass


def tick():
    global stopping
    try:
        item = pending.get_nowait()
    except queue.Empty:
        return .1
    if item["cancelled"]:
        return .1
    try:
        data = item["data"]
        action = data["action"]
        if action == "status":
            result = inspect_scene()
        elif action == "exec":
            source = data.get("script")
            if not isinstance(source, str) or not source.strip():
                raise ValueError("script must be nonempty Python")
            revision = job / ("edit-" + uuid.uuid4().hex)
            revision.mkdir()
            (revision / "source.py").write_text(source, encoding="utf-8")
            with (revision / "stdout.log").open("w", encoding="utf-8") as stream, contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
                exec(compile(source, str(revision / "source.py"), "exec"), {"__name__": "__xgh_live__", "bpy": bpy, "XGH_OUTPUT": revision, "XGH_WORKSPACE": root})
            result = {"revision": str(revision), "inspection": inspect_scene()}
            write_json(revision / "result.json", result)
        elif action in {"save", "stop"}:
            path = job / ("scene-" + uuid.uuid4().hex[:8] + ".blend")
            bpy.ops.wm.save_as_mainfile(filepath=str(path))
            result = {"blend": str(path)}
            if action == "stop":
                stopping = True
                if not bpy.app.background:
                    bpy.app.timers.register(lambda: bpy.ops.wm.quit_blender() and None, first_interval=.8)
        else:
            raise ValueError("Unsupported live action")
        item["result"] = {"ok": True, "result": result}
    except Exception as exc:
        traceback.print_exc()
        item["result"] = {"ok": False, "error": str(exc), "note": "Partial edits may exist. Inspect before retrying."}
    finally:
        item["event"].set()
    return .1


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
server.daemon_threads = True
threading.Thread(target=server.serve_forever, daemon=True).start()
# Switch the loaded input to a new working copy immediately; Ctrl+S cannot overwrite input.
bpy.ops.wm.save_as_mainfile(filepath=str(job / "working.blend"))
metadata = inside(root, ".xgh-live.json")
write_json(metadata, {"pid": os.getpid(), "port": server.server_port, "token": token, "owner": config["owner"], "job": str(job)})
if os.name != "nt":
    metadata.chmod(0o600)
write_json(job / "ready.json", {"ready": True})
if bpy.app.background:
    try:
        while not stopping:
            tick()
            time.sleep(.05)
        time.sleep(.2)
    finally:
        server.shutdown()
        lock.__exit__(None, None, None)
else:
    bpy.app.timers.register(tick, persistent=True)
