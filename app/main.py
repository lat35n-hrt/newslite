# app/main.py

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from app.guardian_client import fetch_guardian_articles
from app.summary_llm import summarize_article

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