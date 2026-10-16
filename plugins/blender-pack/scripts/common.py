"""Shared local runner primitives. Python 3.11+, standard library only."""
from __future__ import annotations
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import subprocess

PACK = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inside(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path escapes asset workspace: {relative}")
    return path


def blender_bin(explicit=None):
    config = Path.home() / ".xgh/blender.json"
    configured = read_json(config).get("executable") if config.exists() else None
    selected = explicit or os.environ.get("BLENDER_BIN") or configured
    if selected:
        path = Path(selected).expanduser()
        if not path.is_file():
            raise ValueError(f"Configured Blender does not exist: {path}")
        return str(path.resolve())
    found = shutil.which("blender")
    candidates = [Path(found)] if found else []
    if os.name == "nt":
        candidates += sorted(Path(os.environ.get("ProgramFiles", "C:/Program Files")).glob("Blender Foundation/Blender */blender.exe"), reverse=True)
    else:
        candidates += [Path("/Applications/Blender.app/Contents/MacOS/Blender")]
    for path in candidates:
        if path.is_file():
            return str(path.resolve())
    raise ValueError("Blender not found. Supply --blender, BLENDER_BIN, or ~/.xgh/blender.json executable.")


def process_options():
    return {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}


@contextmanager
def workspace_lock(root):
    """OS lock survives CLI crashes correctly; never delete the lock inode."""
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = inside(root, ".xgh-blender.lock")
    with path.open("a+b") as handle:
        handle.seek(0, 2)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise RuntimeError("This asset workspace is occupied by another Blender job or live session.") from exc
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)
