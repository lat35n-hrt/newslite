# app/guardian_client.py

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")


# Default values for 'query' and 'page_size' are set for:
# - convenience during manual testing via `if __name__ == "__main__"`
# - fallback behavior when parameters are not provided in FastAPI requests
# def fetch_guardian_articles(query="world", page_size=5):
def fetch_guardian_articles(query="technology", page_size=1, fields="headline,bodyText,trailText", debug=False):
    url = "https://content.guardianapis.com/search"
    params = {
        "api-key": GUARDIAN_API_KEY,
        "q": query,
        "page-size": page_size,
        "show-fields": fields,
        "order-by": "newest"
    }

    response = httpx.get(url, params=params)

    if debug:
        print("<<< STATUS CODE >>>", response.status_code)
        print("<<< RESPONSE TEXT START >>>", response.text[:200])  # Truncate for readability
        print("<<< RESPONSE TEXT END >>>")

    response.raise_for_status()
    data = response.json()

    articles = []
    for item in data["response"]["results"]:
        articles.append({
            "title": item["webTitle"],
            "url": item["webUrl"],
            "content": item["fields"].get("bodyText", ""),
        })


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