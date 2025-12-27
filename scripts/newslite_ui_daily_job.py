# scripts/newslite_ui_daily_job.py
#!/usr/bin/env python3
"""
newslite_ui_daily_job.py — Cross-repo daily job

Repo layout (expected):
  ~/dev/newslite/      (backend/scripts/data live here)
  ~/dev/newslite-ui/   (Workers UI + wrangler put is executed here)

Flow:
  1) Run attach_audio_urls.py in newslite repo (creates *_with_audio.json in newslite/data)
  2) Copy *_with_audio.json into newslite-ui/data (staging)
  3) Put to KV (preview by default, prod with --prod) by running wrangler in newslite-ui repo
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys
from datetime import date


DEFAULT_NEWSLITE_DIR = pathlib.Path("~/dev/newslite").expanduser()
DEFAULT_UI_DIR = pathlib.Path("~/dev/newslite-ui").expanduser()

DEFAULT_BINDING = "newslite_kv"
DEFAULT_ATTACH_SCRIPT_REL = pathlib.Path("scripts/attach_audio_urls.py")


def run(cmd: list[str], cwd: pathlib.Path) -> subprocess.CompletedProcess:
    print("[EXEC]", " ".join(cmd))
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def read_payload(json_path: pathlib.Path) -> str:
    payload = json_path.read_text(encoding="utf-8").strip()
    if not payload:
        raise RuntimeError(f"JSON is empty: {json_path}")
    return payload


def main() -> int:
    p = argparse.ArgumentParser()

    p.add_argument("--prod", action="store_true",
                   help="Publish to production KV (uses --preview=false). Default: preview.")
    p.add_argument("--date", default=date.today().strftime("%Y-%m-%d"),
                   help="Target date in YYYY-MM-DD. Default: today.")

    # Repo roots
    p.add_argument("--newslite-dir", default=str(DEFAULT_NEWSLITE_DIR),
                   help=f"Backend repo root. Default: {DEFAULT_NEWSLITE_DIR}")
    p.add_argument("--ui-dir", default=str(DEFAULT_UI_DIR),
                   help=f"UI repo root. Default: {DEFAULT_UI_DIR}")

    # KV binding
    p.add_argument("--binding", default=DEFAULT_BINDING,
                   help=f"Wrangler KV binding name. Default: {DEFAULT_BINDING}")

    # attach step
    p.add_argument("--no-attach", action="store_true",
                   help="Skip attach_audio_urls.py (expects *_with_audio.json already exists).")
    p.add_argument("--attach-script", default=str(DEFAULT_ATTACH_SCRIPT_REL),
                   help="Path to attach_audio_urls.py relative to newslite-dir.")

    # staging/copy
    p.add_argument("--no-copy", action="store_true",
                   help="Do not copy JSON into newslite-ui/data (wrangler can still put from payload read).")

    args = p.parse_args()

    newslite_dir = pathlib.Path(args.newslite_dir).expanduser().resolve()
    ui_dir = pathlib.Path(args.ui_dir).expanduser().resolve()

    if not newslite_dir.exists():
        print(f"❌ newslite-dir not found: {newslite_dir}")
        return 1
    if not ui_dir.exists():
        print(f"❌ ui-dir not found: {ui_dir}")
        return 1

    # Paths (source of truth in newslite repo)
    src_json = newslite_dir / "data" / f"daily_summary_{args.date}_with_audio.json"
    attach_script = newslite_dir / pathlib.Path(args.attach_script)

    # --- Step A: run attach in newslite repo ---
    if not args.no_attach:
        if not attach_script.exists():
            print(f"❌ attach script not found: {attach_script}")
            return 1

        r = run([sys.executable, str(attach_script)], cwd=newslite_dir)
        if r.returncode != 0:
            print("❌ attach_audio_urls.py failed")
            if r.stdout:
                print("STDOUT:\n", r.stdout)
            if r.stderr:
                print("STDERR:\n", r.stderr)
            return r.returncode

    if not src_json.exists():
        print(f"❌ with_audio JSON not found: {src_json}")
        print("   - attach_audio_urls.py did not create it, or date mismatch.")
        return 1

    # --- Step B: (optional) copy into newslite-ui/data for visibility/traceability ---
    ui_data_dir = ui_dir / "data"
    ui_data_dir.mkdir(parents=True, exist_ok=True)
    dst_json = ui_data_dir / src_json.name

    if not args.no_copy:
        shutil.copy2(src_json, dst_json)
        print(f"✅ Copied to UI repo: {dst_json}")

    # --- Step C: Put to KV (run wrangler from UI repo) ---
    key = f"articles/{args.date}"

    payload = read_payload(src_json)  # read from source-of-truth (newslite)
    cmd = [
        "npx", "wrangler", "kv", "key", "put",
        key,
        payload,
        "--binding", args.binding,
        "--remote",
    ]

    if args.prod:
        cmd += ["--preview=false"]
        mode_label = "PROD"
    else:
        cmd += ["--preview"]
        mode_label = "PREVIEW"

    result = run(cmd, cwd=ui_dir)

    if result.returncode != 0:
        print(f"❌ KV upload failed ({mode_label})")
        if result.stdout:
            print("STDOUT:\n", result.stdout)
        if result.stderr:
            print("STDERR:\n", result.stderr)
        return result.returncode

    print(f"✅ KV upload success ({mode_label})")
    if result.stdout.strip():
        print("STDOUT:\n", result.stdout.strip())

    # Verify hints
    if args.prod:
        print(f"🔎 Verify (prod): https://newslite.tarclog.com/?date={args.date}")
    else:
        print(f"🔎 Verify (preview via localhost): http://localhost:8787/?date={args.date}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
