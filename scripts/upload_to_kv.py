# scripts/upload_to_kv.py
import subprocess
from pathlib import Path

# --- Config ---
NEWSLITE_UI_DIR = Path("~/dev/newslite-ui").expanduser()
JSON_FILE = Path("data/daily_summary_2025-12-06.json")
KV_KEY = "articles/2025-12-06"

# --- Read JSON ---
payload = JSON_FILE.read_text(encoding="utf-8")

# --- Execute Wrangler Command ---
result = subprocess.run(
    [
        "npx", "wrangler", "kv", "key", "put",
        KV_KEY,
        payload,
        "--binding=test_kv",
        "--remote",
        "--preview"
    ],
    cwd=NEWSLITE_UI_DIR,
    text=True,
    capture_output=True
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)