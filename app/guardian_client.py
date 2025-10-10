# app/guardian_client.py

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")


def fetch_guardian_articles(
    query="technology",
    page_size=3,
    fields="headline,bodyText,trailText",
    page=1,
    debug=False,
    max_pages=3
):

    """
    Fetch unique Guardian articles, ensuring a fixed number of valid results.

    The Guardian Open Platform provides a paginated "Search" API endpoint:
        https://content.guardianapis.com/search

    ─────────────────────────────────────────────────────────────────────────────
    🔹 Pagination Parameters (as per Guardian API)
    - `page`: Specifies which page of results to return (integer ≥ 1)
      → Conceptually identical to a UI "Next Page" button.
        e.g., page=1 returns results 1–N, page=2 returns N+1–2N, etc.

    - `page-size`: Defines how many items are shown per page (1–50)
      → e.g., `page-size=3` returns 3 articles per request.
        This mirrors the visible pagination on theguardian.com.

    These parameters allow incremental retrieval of search results in small batches
    (useful for rate limiting, deduplication, and filtering invalid articles).

    ─────────────────────────────────────────────────────────────────────────────
    🔹 Function Behavior
    - Repeatedly requests new pages from the Guardian API until one of these conditions:
        (a) A total of `page_size` valid articles are collected, OR
        (b) `max_pages` have been checked (failsafe against infinite loops)

    - Skips unwanted entries (live blogs, quizzes, obituaries)
    - Ensures no duplicates using a title + URL tuple key
    - Returns exactly `page_size` items per keyword if possible

    ─────────────────────────────────────────────────────────────────────────────
    Args:
        query (str): Keyword to search (e.g., "technology")
        page_size (int): Desired number of valid articles to return
        fields (str): Comma-separated list of fields to include
        page (int): Starting page number for the Guardian API
        debug (bool): If True, prints detailed response info
        max_pages (int): Maximum number of API pages to scan

    Returns:
        list[dict]: List of dictionaries containing article title, URL, and summary.
    """

    url = "https://content.guardianapis.com/search"
    articles = []
    seen = set()
    page = 1

    total_checked = 0
    # per_page_limit = 5

    # max_allowed = 30 # max 30 articles per page
    # page_size = min(page_size, max_allowed)

    while len(articles) < page_size and page <= max_pages:
        params = {
            "api-key": GUARDIAN_API_KEY,
            "q": query,
            "page-size": page_size,
            "show-fields": fields,
            "page": page,
            "order-by": "newest"
        }

        response = httpx.get(url, params=params)
        print(f"✅ Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Request failed on page {page}")
            break

        response.raise_for_status()
        data = response.json()
        print(f"📦 Found {len(data['response']['results'])} results on page {page}")

        if debug:
            print("<<< STATUS CODE >>>", response.status_code)
            print("<<< RESPONSE TEXT START >>>", response.text[:200])  # Truncate for readability
            print("<<< RESPONSE TEXT END >>>")

        for item in data["response"]["results"]:
            total_checked += 1

            # Skip live blogs, Quizzes, and Obituaries
            # id: unique idenfitiers of articles e.g.
            # world/live/2025/aug/08/uk-election-live-updates
            # sport/quiz/2025/aug/08/football-weekly

            if (
                "live" in item["id"] or
                "quiz" in item["id"] or
                "obituary" in item["webTitle"].lower()
            ):
                continue

            key = (item["webTitle"], item["webUrl"])
            if key in seen:
                continue
            seen.add(key)

            articles.append({
            "title": item["webTitle"],
            "url": item["webUrl"],
            "content": item["fields"].get("trailText", ""),
            "fields": item["fields"],
            })

            if len(articles) >= page_size:
                break

            if debug:
                print(f"Page {page}: Collected {len(articles)} articles so far.")

    # if debug:
    #     for article in articles:
    #         print("Title:", article["title"])
    #         print("URL:", article["url"])
    #         print("Content Preview:", article["content"][:200])
    #         print("=" * 40)

        print(f"📰 Collected {len(articles)} articles so far...")
        page += 1  # ✅ Move to next page inside the while loop

    print(f"✅ Final count for '{query}': {len(articles)} articles")
    return articles

# This block allows standalone execution of this script
# for quick testing or debugging without starting the FastAPI server.
if __name__ == "__main__":
    articles = fetch_guardian_articles(debug=True)
#    print(articles)