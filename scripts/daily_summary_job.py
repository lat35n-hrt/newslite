# scripts/daily_summary_job.py

import os
import json
from pathlib import Path
from datetime import date
from app.guardian_client import fetch_guardian_articles
from app.summary_llm import summarize_article
from app.amazon_polly_client import summaries_to_mp3
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)
AUDIO_DIR = Path("output/audio")
today_str = date.today().isoformat()
output_file = OUTPUT_DIR / f"daily_summary_{today_str}.json"
output_file_full = OUTPUT_DIR / f"daily_full_article_{today_str}.json"


if output_file.exists():
    print(f"⛔ Summary already exists for {today_str}")
    exit(0)

topics = ["technology", "climate", "education"]
summaries = []
full_articles = []

for topic in topics:
    articles = fetch_guardian_articles(query=topic, page_size=3)
    for article in articles:
        # print(json.dumps(article, indent=2)) # debug
        body = article.get("fields", {}).get("bodyText", "")

        if not body:
            continue

        result = summarize_article(body)
        summaries.append({
            "title": article.get("title", "(No title)"),
            "url": article.get("url", "#"),
            "topic": topic,
            "summary": result.get("summary", "(Summary unavailable)")
        })

    full_articles.extend(articles) # for a full backup

# Save Full Articles
with open(output_file_full, "w", encoding="utf-8") as f:
    json.dump(full_articles, f, ensure_ascii=False, indent=2)

# Save Summaries
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(summaries, f, ensure_ascii=False, indent=2)

print(f"✅ Saved daily summary to {output_file}")

# Amazon Polly (text-to-mp3)
audio_output_dir = AUDIO_DIR / today_str
audio_output_dir.mkdir(parents=True, exist_ok=True)

summaries_to_mp3(
    json_path=output_file,
    output_dir=audio_output_dir,
    voice_id=os.getenv("AWS_POLLY_VOICE_ID", "Ruth"),
    engine=os.getenv("AWS_POLLY_ENGINE", "neural")
)