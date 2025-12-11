# scripts/attach_audio_urls.py
"""
attach_audio_urls.py — Add audio URLs to today's NewsLite JSON safely.

- Reads data/daily_summary_YYYY-MM-DD.json
- Appends audio URLs: https://<r2-base-url>/<date>/article_01.mp3
- Saves new JSON as: data/daily_summary_YYYY-MM-DD_with_audio.json
- Prevents accidental overwrite or double processing
"""

import json
from datetime import date
import os
from pathlib import Path
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# ====== Config =======================
R2_BASE_URL = os.getenv("R2_BASE_URL")
if not R2_BASE_URL:
    raise RuntimeError("R2_BASE_URL is not set. Please export R2_BASE_URL in your environment.")
# Example value:
#   R2_BASE_URL=https://audio.newslite.tarclog.com/audio
# ============================================================


def main():
    today_str = date.today().strftime("%Y-%m-%d")

    src_path = Path(f"data/daily_summary_{today_str}.json")
    dst_path = Path(f"data/daily_summary_{today_str}_with_audio.json")

    # --- Safety 1: Source file does not exist, then exit ---
    if not src_path.exists():
        print(f"❌ Source JSON not found: {src_path}")
        return

    # --- Safety 2: with_audio already exists, warn ---
    if dst_path.exists():
        print(f"⚠️  WARNING: {dst_path} already exists.")
        print("    → Already audio URL is attached.")
        print("    → Overwriting is not done. Please check manually.")
        return

    # --- Load JSON ---
    data = json.loads(src_path.read_text())

    # --- Safety 3: audio field already exists in source (prevent accidental double processing) ---
    if any("audio" in article for article in data):
        print("⚠️  WARNING: Source JSON already contains 'audio' fields.")
        print("    → Local JSON already has audio fields. Please investigate.")
        print("    → with_audio will not be created.")
        return

    # --- Generate audio URLs ---
    processed = []
    for idx, article in enumerate(data):
        audio_no = f"{idx + 1:02d}"
        audio_url = f"{R2_BASE_URL}/{today_str}/article_{audio_no}.mp3"

        article_with_audio = {
            **article,
            "audio": audio_url,
        }
        processed.append(article_with_audio)

    # --- Save output JSON ---
    dst_path.write_text(json.dumps(processed, ensure_ascii=False, indent=2))

    print(f"✅ Audio URLs successfully added.")
    print(f"📁 Output: {dst_path} ")
    print(f"🔗 Example first audio: {processed[0]['audio']}")


if __name__ == "__main__":
    main()
