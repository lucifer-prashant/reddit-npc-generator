import requests
import sqlite_utils
import time
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "cache.db"
BASE = "https://arctic-shift.photon-reddit.com/api"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_db():
    db = sqlite_utils.Database(DB_PATH)
    if "cache" not in db.table_names():
        db["cache"].create({
            "subreddit": str,
            "scraped_at": float,
            "comments_json": str,
            "posts_count": int,
        }, pk="subreddit")
    return db

def is_fresh(subreddit: str, max_age_hours: int = 24) -> bool:
    db = get_db()
    rows = list(db["cache"].rows_where("subreddit = ?", [subreddit.lower()]))
    if not rows:
        return False
    return (time.time() - rows[0]["scraped_at"]) < max_age_hours * 3600

def load_cached(subreddit: str) -> list[str]:
    db = get_db()
    rows = list(db["cache"].rows_where("subreddit = ?", [subreddit.lower()]))
    return json.loads(rows[0]["comments_json"])

BOT_AUTHORS = {"automoderator", "automod"}
BOT_PHRASES = {"i am a bot", "action was performed automatically", "contact the moderators"}

def _is_junk(author: str, body: str) -> bool:
    a = (author or "").lower()
    b = (body or "").lower()
    if a in BOT_AUTHORS:
        return True
    if b in {"[deleted]", "[removed]"}:
        return True
    if any(p in b for p in BOT_PHRASES):
        return True
    return False

def scrape(subreddit: str) -> list[str]:
    sub = subreddit.lower().strip()

    if is_fresh(sub):
        return load_cached(sub)

    # fetch up to 500 comments directly — much faster than post-by-post
    comments = []
    after = None

    for _ in range(5):  # 5 pages × 100 = 500 comments
        params = {"subreddit": sub, "limit": 100}
        if after:
            params["after"] = after

        r = requests.get(f"{BASE}/comments/search", headers=HEADERS, params=params, timeout=15)
        if r.status_code != 200:
            break

        data = r.json().get("data") or []
        if not data:
            break

        for c in data:
            body = c.get("body", "")
            author = c.get("author", "")
            if len(body) > 10 and not _is_junk(author, body):
                comments.append(body)

        after = data[-1].get("created_utc") if data else None
        time.sleep(0.5)

    db = get_db()
    db["cache"].upsert({
        "subreddit": sub,
        "scraped_at": time.time(),
        "comments_json": json.dumps(comments),
        "posts_count": len(comments),
    }, pk="subreddit")

    return comments
