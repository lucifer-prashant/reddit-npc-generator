import re
import string
from collections import Counter
from datetime import datetime

import nltk
import textstat

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("vader_lexicon", quiet=True)

from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize

STOP = set(stopwords.words("english"))
EXTRA_STOP = {
    "like", "just", "really", "get", "got", "one", "would", "could", "also", "even",
    "think", "know", "make", "use", "much", "well", "way", "go", "thing", "people",
    "want", "need", "say", "said", "still", "back", "good", "see", "look", "take",
    "come", "going", "used", "made", "new", "years", "year", "time", "total", "best",
    "first", "last", "account", "post", "comment", "reddit", "subreddit", "deleted",
    "removed", "edit", "https", "www", "user", "report", "right", "actually",
    "probably", "literally", "pretty", "bit", "lot", "many", "every", "never",
    "always", "already", "maybe", "though", "something", "anything", "nothing",
    "someone", "anyone", "everyone", "another", "different", "same", "sure", "fine",
    "seen", "ago", "previous", "join", "submissions", "moderators", "rules", "wiki",
    "karma", "upvote", "downvote", "vote", "awarded", "gilded", "crosspost",
    "comments", "discord", "age", "account", "posted", "posting", "thread",
}
STOP |= EXTRA_STOP

def clean(text: str) -> str:
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9\s\.\!\?]", "", text)
    return text.lower().strip()

def top_words(corpus: str, n: int = 15) -> list[tuple[str, int]]:
    tokens = word_tokenize(corpus)
    tokens = [t for t in tokens if t.isalpha() and t not in STOP and len(t) >= 4]
    return Counter(tokens).most_common(n)

def top_phrases(comments: list[str], n: int = 5) -> list[str]:
    bigrams = []
    for c in comments:
        words = [w for w in word_tokenize(clean(c)) if w.isalpha() and w not in STOP]
        bigrams += [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]
    return [phrase for phrase, _ in Counter(bigrams).most_common(n)]

def sentiment(comments: list[str]) -> dict:
    sia = SentimentIntensityAnalyzer()
    scores = [sia.polarity_scores(c)["compound"] for c in comments]
    avg = sum(scores) / len(scores) if scores else 0
    if avg > 0.2:
        label = "positive"
    elif avg < -0.2:
        label = "negative"
    else:
        label = "neutral"
    return {"score": round(avg, 3), "label": label}

def writing_style(comments: list[str]) -> dict:
    corpus = " ".join(comments)
    sentences = sent_tokenize(corpus)
    avg_sent_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    grade = textstat.flesch_kincaid_grade(corpus)
    exclamation_rate = sum(c.count("!") for c in comments) / max(len(comments), 1)
    question_rate = sum(c.count("?") for c in comments) / max(len(comments), 1)
    avg_comment_len = sum(len(c.split()) for c in comments) / max(len(comments), 1)
    caps_rate = sum(1 for c in comments if any(w.isupper() and len(w) > 1 for w in c.split())) / max(len(comments), 1)

    if avg_comment_len < 20:
        verbosity = "terse"
    elif avg_comment_len < 60:
        verbosity = "moderate"
    else:
        verbosity = "verbose"

    return {
        "avg_sentence_len": round(avg_sent_len, 1),
        "reading_grade": round(min(max(grade, 1.0), 18.0), 1),
        "exclamation_rate": round(exclamation_rate, 2),
        "question_rate": round(question_rate, 2),
        "avg_comment_len": round(avg_comment_len, 1),
        "caps_rate": round(caps_rate, 2),
        "verbosity": verbosity,
    }

def profanity_rate(comments: list[str]) -> float:
    bad = {"fuck", "shit", "ass", "damn", "crap", "hell", "bitch", "bastard", "dick", "piss"}
    total_words = 0
    bad_count = 0
    for c in comments:
        words = c.lower().split()
        total_words += len(words)
        bad_count += sum(1 for w in words if w.strip(string.punctuation) in bad)
    return round(bad_count / max(total_words, 1), 4)

def infer_topics(words: list[tuple[str, int]]) -> list[str]:
    topic_map = {
        "tech": {"ai", "code", "software", "api", "dev", "python", "javascript", "model", "server", "gpu", "ml", "programming", "data", "engineer", "github", "open"},
        "finance": {"stock", "money", "market", "invest", "crypto", "bitcoin", "trade", "profit", "loss", "portfolio", "yolo", "calls", "puts", "shares", "options", "wsb", "gains", "moon", "apes", "hedge", "short", "squeeze", "robinhood", "etf", "dividend", "bulls", "bears", "tendies"},
        "gaming": {"game", "play", "pc", "console", "steam", "fps", "build", "graphics", "mod", "gaming", "xbox", "playstation", "nintendo", "indie"},
        "politics": {"government", "policy", "president", "vote", "party", "law", "democrat", "republican", "election", "congress", "senate", "political", "trump", "biden"},
        "sports": {"team", "player", "win", "season", "score", "coach", "league", "championship", "nba", "nfl", "mlb", "soccer", "football", "basketball", "baseball"},
        "fitness": {"workout", "gym", "run", "weight", "muscle", "diet", "protein", "cardio", "lift", "fitness", "training", "bulk", "cut", "gains"},
        "science": {"research", "study", "evidence", "paper", "theory", "experiment", "results", "physics", "biology", "chemistry", "climate"},
        "memes": {"lol", "meme", "based", "cringe", "cope", "seethe", "ratio", "chad", "npc", "irl", "bruh", "bro", "dude", "vibes"},
        "vegan": {"vegan", "meat", "animal", "animals", "plant", "dairy", "leather", "cruelty", "slaughter", "vegetarian", "tofu", "ethics", "environment", "factory", "protein", "fish", "eggs", "milk", "cheese"},
        "pets": {"cat", "cats", "dog", "dogs", "kitten", "puppy", "pet", "pets", "vet", "paw", "fur", "breed", "adopt", "rescue", "meow", "bark", "litter", "feline", "canine"},
        "relationships": {"love", "relationship", "partner", "boyfriend", "girlfriend", "husband", "wife", "date", "dating", "marriage", "breakup", "toxic", "feelings", "heart"},
        "food": {"recipe", "cook", "food", "eat", "meal", "dinner", "lunch", "breakfast", "ingredient", "taste", "delicious", "kitchen", "bake"},
        "mental_health": {"anxiety", "depression", "therapy", "mental", "health", "stress", "trauma", "heal", "support", "struggle", "cope", "disorder"},
    }
    word_set = {w for w, _ in words}
    hits = {topic: len(word_set & kws) for topic, kws in topic_map.items()}
    top = sorted(hits.items(), key=lambda x: x[1], reverse=True)
    return [t for t, count in top if count > 0][:3]

def analyze(comments: list[str]) -> dict:
    corpus = clean(" ".join(comments))
    words = top_words(corpus)
    return {
        "total_comments": len(comments),
        "top_words": words,
        "top_phrases": top_phrases(comments),
        "sentiment": sentiment(comments),
        "style": writing_style(comments),
        "profanity_rate": profanity_rate(comments),
        "topics": infer_topics(words),
    }
