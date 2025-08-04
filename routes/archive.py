from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import json

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/archive/{date_str}", response_class=HTMLResponse)
async def read_archive(request: Request, date_str: str):
    filepath = Path(f"data/daily_summary_{date_str}.json")
    if not filepath.exists():
        return HTMLResponse(content="Article not found", status_code=404)

    with open(filepath, "r", encoding="utf-8") as f:
        articles = json.load(f)

    # print(json.dumps(articles, indent=2)) # debug

    return templates.TemplateResponse("archive.html", {
        "request": request,
        "date": date_str,
        "articles": articles
    })
