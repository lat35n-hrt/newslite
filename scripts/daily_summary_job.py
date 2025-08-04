# scripts/daily_summary_job.py

import json
from pathlib import Path
from datetime import date
from app.guardian_client import fetch_guardian_articles
from app.summary_llm import summarize_article
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)
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


with open(output_file, "w", encoding="utf-8") as f:
    json.dump(summaries, f, ensure_ascii=False, indent=2)

print(f"✅ Saved daily summary to {output_file}")

exit(0)