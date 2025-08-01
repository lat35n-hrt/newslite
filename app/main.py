# app/main.py

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.guardian_client import fetch_guardian_articles
from app.summary_llm import summarize_article
import json
from datetime import date
from pathlib import Path

# Test Data
sample_summaries = [
    {
        "title": "Labour debates wealth tax and Green party considers alliance",
        "summary": "Labour debates the feasibility of a wealth tax to cover budget deficits, with some internal disagreement. Meanwhile, Green Party leadership candidate Zack Polanski considers cooperation with Jeremy Corbyn’s new leftwing movement. Other developments include Greenpeace’s protest on a Scottish bridge, arrests in Essex, and UN criticism of the UK’s ban on Palestine Action as disproportionate."
    },
    {
        "title": "Four-day work week, IMF warning, and strikes affect UK politics",
        "summary": "South Cambridgeshire becomes the first UK council to adopt a permanent four-day work week, supported by studies showing improved services. IMF advises the UK to maintain fiscal flexibility. Meanwhile, Jeremy Corbyn’s new party claims 230,000 sign-ups. Unite criticizes the government over an oil refinery closure. Mhairi Black leaves SNP citing disagreements. Health Secretary Wes Streeting condemns junior doctors' strikes for risking patient safety."
    }
]


app = FastAPI()

@app.get("/guardian")
def get_guardian_news(q: str = Query("technology"), count: int = Query(1)):
    articles = fetch_guardian_articles(query=q, page_size=count)
    return {"source": "guardian", "articles": articles}


@app.get("/summary")
def summarize_article(q: str = Query("climate"), count: int = Query(1)):
    articles = fetch_guardian_articles(query=q, page_size=count)
    summaries = []

    for article in articles:
        summary = summarize_article(article["content"])
        summaries.append({
            "title": article["title"],
            "url": article["url"],
            "summary": summary["summary"]
        })

    return {"source": "guardian", "summaries": summaries}


@app.get("/sample_summaries")
def get_sample_summaries():
    return JSONResponse(content={"summaries": sample_summaries})

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def search_ui(
    request: Request,
    q: str = "technology",
    count: int = Query(3, ge=1, le=30),  # max 30 and min 1
    page: int = Query(1, ge=1),
    content_type: str = Query("body", pattern="^(body|trail)$")
):

    print(f"DEBUG: q={q}, count={count}, page={page}")
    articles = fetch_guardian_articles(query=q, page_size=count, page=page)

    # contentの種類を切り替え
    for article in articles:
        article["content"] = (
            article["fields"].get("bodyText", "") if content_type == "body"
            else article["fields"].get("trailText", "")
        )

    return templates.TemplateResponse("index.html", {
        "request": request,
        "articles": articles,
        "query": q,
        "count": count,
        "page": page,
        "content_type": content_type,
    })


@app.get("/daily", response_class=HTMLResponse)
def daily_summary_page(request: Request):
    today_str = date.today().isoformat()
    data_file = Path(f"data/daily_summary_{today_str}.json")

    if not data_file.exists():
        return templates.TemplateResponse("daily.html", {
            "request": request,
            "summaries": [],
            "error": "No summary data found for today."
        })

    with open(data_file, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    return templates.TemplateResponse("daily.html", {
        "request": request,
        "summaries": summaries,
        "error": None
    })