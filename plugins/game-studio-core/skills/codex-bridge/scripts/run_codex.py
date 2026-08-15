#!/usr/bin/env python3
"""Bridge Claude Code to the local Codex CLI via headless `codex exec`.

Two modes:
  * generic delegation: --prompt "task"            -> prints codex's final reply
  * image generation:   --imagegen TARGET.png      -> wraps prompt with $imagegen,
    verifies the target file, falls back to copying the newest image codex left
    under ~/.codex/generated_images/.

Codex handles its own auth (Codex Desktop login / ChatGPT subscription); no
OPENAI_API_KEY needed for the built-in image_gen tool.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))


def die(msg: str, code: int = 1) -> None:
    print(f"[codex-bridge] ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def find_codex() -> str:
    """Locate codex executable: env var > ~/.codex/config.toml hint > newest desktop bundle."""
    env = os.environ.get("CODEX_CLI_PATH")
    if env and Path(env).is_file():
        return env

    cfg = CODEX_HOME / "config.toml"
    if cfg.is_file():
        m = re.search(r"CODEX_CLI_PATH\s*=\s*['\"](.+?)['\"]", cfg.read_text(encoding="utf-8", errors="replace"))
        if m and Path(m.group(1)).is_file():
            return m.group(1)

    local = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
    candidates = glob.glob(os.path.join(local, "OpenAI", "Codex", "bin", "*", "codex.exe"))
    if candidates:
        return max(candidates, key=os.path.getmtime)

    which = shutil.which("codex")
    if which:
        return which
    die("codex executable not found. Install Codex Desktop or set CODEX_CLI_PATH.")
    return ""  # unreachable


def newest_generated_images(since: float) -> list[Path]:
    """Images created under ~/.codex/generated_images/ after `since`, newest first."""
    root = CODEX_HOME / "generated_images"
    if not root.is_dir():
        return []
    hits = [p for p in root.rglob("*") if p.is_file()
            and p.suffix.lower() in (".png", ".webp", ".jpg", ".jpeg")
            and p.stat().st_mtime >= since]
    return sorted(hits, key=lambda p: p.stat().st_mtime, reverse=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run a headless codex exec session.")
    ap.add_argument("--prompt", help="task / image prompt text")
    ap.add_argument("--prompt-file", help="read prompt from file (UTF-8)")
    ap.add_argument("--image", action="append", default=[], help="reference image, repeatable")
    ap.add_argument("--imagegen", metavar="TARGET_PNG",
                    help="image generation mode: absolute path where the result must land")
    ap.add_argument("--workdir", default=os.getcwd(), help="codex working root (-C)")
    ap.add_argument("--sandbox", default="workspace-write",
                    choices=["read-only", "workspace-write", "danger-full-access"])
    ap.add_argument("--out", help="file for codex's final message (default: temp file)")
    ap.add_argument("--timeout", type=int, default=600, help="seconds (image gen: use 900)")
    ap.add_argument("--resume-last", action="store_true", help="continue the most recent session")
    ap.add_argument("--model", help="override model (-m)")
    args = ap.parse_args()

    if bool(args.prompt) == bool(args.prompt_file):
        die("provide exactly one of --prompt / --prompt-file")
    prompt = args.prompt or Path(args.prompt_file).read_text(encoding="utf-8")

    target: Path | None = None
    if args.imagegen:
        target = Path(args.imagegen)
        if not target.is_absolute():
            die("--imagegen target must be an absolute path")
        target.parent.mkdir(parents=True, exist_ok=True)
        prompt = (
            "$imagegen " + prompt.strip()
            + f"\n\nAfter generating, copy the final selected image to exactly this path: {target}"
            + "\nDo not leave it only under the default generated_images directory."
        )

    for img in args.image:
        if not Path(img).is_file():
            die(f"reference image not found: {img}")

    if args.out:
        out_file = Path(args.out)
    else:
        # mkstemp, not a time.time() name: two bridges launched in the same
        # second would otherwise share one output file and clobber each other.
        fd, tmp_name = tempfile.mkstemp(prefix="codex_bridge_", suffix=".txt")
        os.close(fd)
        out_file = Path(tmp_name)

    codex = find_codex()
    cmd = [codex, "exec"]
    if args.resume_last:
        cmd += ["resume", "--last"]
    cmd += [prompt, "-o", str(out_file), "-C", args.workdir, "-s", args.sandbox,
            "--skip-git-repo-check", "--color", "never"]
    for img in args.image:
        cmd += ["-i", img]
    if args.model:
        cmd += ["-m", args.model]

    print(f"[codex-bridge] exec via {codex}")
    print(f"[codex-bridge] workdir={args.workdir} sandbox={args.sandbox} timeout={args.timeout}s")
    started = time.time()
    try:
        proc = subprocess.run(cmd, timeout=args.timeout,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.TimeoutExpired:
        die(f"codex exec timed out after {args.timeout}s (raise --timeout or simplify the task)")

    log_tail = proc.stdout.decode("utf-8", errors="replace")[-2000:]
    if proc.returncode != 0:
        print(log_tail)
        die(f"codex exec exited with code {proc.returncode} (see log above; "
            "common causes: not logged in, quota exhausted, config.toml parse error)")

    final_msg = out_file.read_text(encoding="utf-8", errors="replace").strip() if out_file.is_file() else ""
    print("[codex-bridge] ---- final message ----")
    print(final_msg or "(empty final message)")

    if target is not None:
        if target.is_file() and target.stat().st_mtime >= started:
            print(f"[codex-bridge] OK image at target: {target} ({target.stat().st_size} bytes)")
        else:
            fallback = newest_generated_images(started)
            if not fallback:
                die(f"image generation finished but nothing found at {target} "
                    "nor under ~/.codex/generated_images/ — inspect the final message above")
            shutil.copyfile(fallback[0], target)
            print(f"[codex-bridge] target missing; copied fallback {fallback[0]} -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
