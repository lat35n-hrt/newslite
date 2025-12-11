# scripts/daily_upload_to_kv.py
import subprocess
from datetime import date
import json
import pathlib

NEWSLITE_UI_DIR = pathlib.Path("~/dev/newslite-ui").expanduser()

today = date.today().strftime("%Y-%m-%d")

# Load today's JSON with audio URLs
json_path = pathlib.Path(f"data/daily_summary_{today}_with_audio.json")

if not json_path.exists():
    print(f"❌ File not found: {json_path}")
    exit(1)

payload = json_path.read_text().strip()

cmd = [
    "npx", "wrangler", "kv", "key", "put",
    f"articles/{today}",
    payload,
    "--binding=newslite_kv",
    "--preview",
    "--remote",
]

print("[EXEC]", " ".join(cmd))

print("[EXEC]", " ".join(cmd))

# 🟢 super important: run wrangler INSIDE newslite-ui directory
result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    cwd=NEWSLITE_UI_DIR # run inside newslite-ui repo
)


if result.returncode != 0:
    print("❌ KV upload failed:")
    print(result.stderr)
else:
    print("✅ KV upload success")
    print("STDOUT:", result.stdout)