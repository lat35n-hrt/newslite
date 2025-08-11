# app/guardian_client.py

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")


# Default values for 'query' and 'page_size' are set for:
# - convenience during manual testing via `if __name__ == "__main__"`
# - fallback behavior when parameters are not provided in FastAPI requests
# page_size: number of article per page
# page: page number on Guardian API
def fetch_guardian_articles(query="technology", page_size=3, fields="headline,bodyText,trailText", page=1, debug=False):
    url = "https://content.guardianapis.com/search"
    articles = []
    total_checked = 0
    # per_page_limit = 5

    max_allowed = 30 # max 30 articles per page
    page_size = min(page_size, max_allowed)

#    while len(articles) < page_size and total_checked < 100:  # 無限ループ防止
    params = {
        "api-key": GUARDIAN_API_KEY,
        "q": query,
        "page-size": page_size,
        "show-fields": fields,
        "page": page,
        "order-by": "newest"
    }

    response = httpx.get(url, params=params)

    if debug:
        print("<<< STATUS CODE >>>", response.status_code)
        print("<<< RESPONSE TEXT START >>>", response.text[:200])  # Truncate for readability
        print("<<< RESPONSE TEXT END >>>")

    response.raise_for_status()
    data = response.json()


    for item in data["response"]["results"]:
        total_checked += 1
        # Skip live blogs, Quizzes, and Obituaries
        # id: unique idenfitiers of articles e.g.
        # world/live/2025/aug/08/uk-election-live-updates
        # sport/quiz/2025/aug/08/football-weekly

        if "live" in item["id"] or "quiz" in item["id"] or "obituary" in item["webTitle"].lower():
            continue

        articles.append({
            "title": item["webTitle"],
            "url": item["webUrl"],
            "content": item["fields"].get("trailText", ""),
            "fields": item["fields"],
        })

        # if len(articles) >= page_size:
        #     break

#        page+=1

    if debug:
        for article in articles:
            print("Title:", article["title"])
            print("URL:", article["url"])
            print("Content Preview:", article["content"][:200])
            print("=" * 40)


    return articles

# This block allows standalone execution of this script
# for quick testing or debugging without starting the FastAPI server.
if __name__ == "__main__":
    articles = fetch_guardian_articles(debug=True)
#    print(articles)