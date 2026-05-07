import re
import json
import time
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import sqlite_utils
from pathlib import Path

load_dotenv()

from scraper import scrape
from nlp import analyze
from profiler import build_profile
from kling import generate_image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).parent / "cache.db"
PROFILE_TTL = 86400  # 24h

def get_cached_profile(sub: str) -> dict | None:
    db = sqlite_utils.Database(DB_PATH)
    if "profiles" not in db.table_names():
        return None
    rows = list(db["profiles"].rows_where("subreddit = ?", [sub]))
    if not rows:
        return None
    if time.time() - rows[0]["cached_at"] > PROFILE_TTL:
        return None
    return json.loads(rows[0]["profile_json"])

def cache_profile(sub: str, profile: dict):
    db = sqlite_utils.Database(DB_PATH)
    if "profiles" not in db.table_names():
        db["profiles"].create({
            "subreddit": str,
            "profile_json": str,
            "cached_at": float,
        }, pk="subreddit")
    db["profiles"].upsert({
        "subreddit": sub,
        "profile_json": json.dumps(profile),
        "cached_at": time.time(),
    }, pk="subreddit")

class AnalyzeRequest(BaseModel):
    subreddit: str
    refresh: bool = False

@app.post("/analyze")
async def analyze_subreddit(req: AnalyzeRequest):
    raw = req.subreddit.strip().lower()
    sub = re.sub(r'^r/', '', raw)
    if not sub:
        raise HTTPException(status_code=400, detail="subreddit required")

    if not req.refresh:
        cached = get_cached_profile(sub)
        if cached:
            return {"profile": cached, "raw_stats": {}, "cached": True}

    comments = scrape(sub)
    if len(comments) < 50:
        raise HTTPException(status_code=404, detail=f"Not enough data for r/{sub}. Try a larger subreddit.")

    stats = analyze(comments)
    profile = build_profile(sub, stats)
    cache_profile(sub, profile)
    return {"profile": profile, "raw_stats": stats, "cached": False}

class ImageRequest(BaseModel):
    prompt: str

@app.post("/generate-image")
async def gen_image(req: ImageRequest):
    url = await generate_image(req.prompt)
    return {"image_url": url}

@app.get("/image-proxy")
async def image_proxy(url: str):
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        content_type = r.headers.get("content-type", "")
        if "text" in content_type or "html" in content_type:
            raise HTTPException(status_code=502, detail="Image generation failed")
        return Response(content=r.content, media_type="image/jpeg")

@app.get("/health")
def health():
    return {"ok": True}
