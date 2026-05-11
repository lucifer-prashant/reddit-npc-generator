# Reddit NPC Generator

Drop any subreddit. Get a character profile of the average person who posts there.

**Live:** [reddit-npc.vercel.app](https://reddit-npc.vercel.app) &nbsp;|&nbsp; **Backend:** Hugging Face Spaces

---

## What it does

1. Scrapes recent comments from a subreddit via Reddit's public API
2. Runs NLP — sentiment analysis, topic detection, style metrics (reading grade, verbosity, profanity rate)
3. Calls an LLM to generate a character: name, age, job, mood, catchphrase, signature drink, things they own
4. Generates a portrait via Pollinations (free tier)
5. Caches results in SQLite for 24h

**Compare mode** — profile two subreddits head-to-head with a side-by-side battle card.

---

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React 19, Vite, Vercel |
| Backend | FastAPI, Python |
| NLP | spaCy, NLTK, textstat |
| LLM | OpenAI API |
| Image gen | Pollinations.ai |
| Cache | SQLite (sqlite-utils) |
| Hosting | Vercel (frontend) + Hugging Face Spaces Docker (backend) |

---

## Running locally

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

cp .env.example .env   # fill in OPENAI_API_KEY
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Point `src/App.jsx` fetch URL to `http://localhost:8000` for local dev.

---

## API

```
POST /analyze
Body: { "subreddit": "wallstreetbets", "refresh": false }

POST /generate-image
Body: { "prompt": "..." }

GET /image-proxy?url=...
GET /health
```

---

## Deploy

- **Frontend:** push to GitHub → Vercel auto-deploys
- **Backend:** push `backend/` → Hugging Face Spaces (Docker SDK, see `backend/Dockerfile`)

---

## Project structure

```
├── frontend/          # React app
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── CharacterCard.jsx
│           └── CompareView.jsx
└── backend/           # FastAPI
    ├── main.py        # routes + cache
    ├── scraper.py     # Reddit scraping
    ├── nlp.py         # NLP pipeline
    ├── profiler.py    # character builder
    └── llm.py         # OpenAI calls
```
