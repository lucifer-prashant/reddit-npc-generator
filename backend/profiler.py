import random

MALE_NAMES = ["Chad", "Kyle", "Brendan", "Tyler", "Jake", "Ethan", "Ryan", "Mike", "Derek", "Josh"]
FEMALE_NAMES = ["Ashley", "Karen", "Brittany", "Stacy", "Megan", "Jessica", "Emily", "Sarah"]
NEUTRAL_NAMES = ["Alex", "Jordan", "Casey", "Riley", "Morgan", "Quinn", "Drew"]

def pick_name(sentiment_label: str, profanity_rate: float) -> str:
    if profanity_rate > 0.02:
        return random.choice(MALE_NAMES)
    return random.choice(NEUTRAL_NAMES + MALE_NAMES)

def infer_age(style: dict, topics: list[str]) -> str:
    grade = style["reading_grade"]
    if grade < 6:
        return "18-22"
    elif grade < 9:
        return "22-28"
    elif grade < 12:
        return "28-35"
    else:
        return "35-45"

def infer_job(topics: list[str]) -> str:
    topic_jobs = {
        "tech": "software engineer / CS student",
        "finance": "finance bro / retail investor",
        "gaming": "unemployed gamer / student",
        "politics": "perpetually online opinion-haver",
        "sports": "fantasy sports addict",
        "fitness": "gym rat",
        "science": "grad student / researcher",
        "memes": "professional lurker",
        "vegan": "ethical consumer / activist",
        "food": "home cook / foodie",
        "mental_health": "therapy enjoyer",
        "pets": "cat parent / pet influencer",
        "relationships": "relationship advice columnist (unpaid)",
    }
    for t in topics:
        if t in topic_jobs:
            return topic_jobs[t]
    return "unclassified internet person"

def infer_drink(topics: list[str], style: dict) -> str:
    if "vegan" in topics:
        return "oat milk latte"
    if "fitness" in topics:
        return "protein shake"
    if "tech" in topics:
        return "cold brew at 11pm"
    if "finance" in topics:
        return "red bull"
    if "mental_health" in topics:
        return "chamomile tea"
    if style["avg_comment_len"] < 15:
        return "monster energy"
    return "coffee (black, obviously)"

def infer_mood(sentiment: dict, profanity_rate: float, style: dict, topics: list[str] = []) -> str:
    label = sentiment["label"]
    score = sentiment["score"]
    caps = style["caps_rate"]

    if "vegan" in topics:
        return "morally superior (and knows it)"
    if "mental_health" in topics and label == "negative":
        return "healing (allegedly)"
    if profanity_rate > 0.03 and label == "negative":
        return "chronically online and angry"
    if label == "positive" and caps > 0.5:
        return "chaotic enthusiastic"
    if label == "positive":
        return "cautiously optimistic"
    if label == "negative" and score < -0.4:
        return "doomer"
    if style["question_rate"] > 0.3:
        return "perpetually confused"
    return "vibes: unclear"

JUNK_PHRASES = {
    "user report", "open source", "feel like", "lot of", "kind of", "sort of",
    "going to", "want to", "able to", "need to", "used to", "trying to",
    "reluctantly leave", "please contact", "have questions", "read rules",
    "submissions seen", "previous submissions", "thank you", "let know",
}

def infer_catchphrase(top_phrases: list[str], top_words: list[tuple], sentiment: dict) -> str:
    clean = [p for p in top_phrases if p.lower() not in JUNK_PHRASES and len(p) > 5]
    if clean:
        return f'"{clean[0]}"'
    return '"I mean, technically..."'

def infer_online_hours(style: dict) -> str:
    if style["avg_comment_len"] > 80:
        return "9am-2am (no life detected)"
    if style["exclamation_rate"] > 0.5:
        return "peaks during work hours (definitely not working)"
    return "2am warrior"

def infer_owns(topics: list[str], style: dict) -> list[str]:
    owns = []
    if "vegan" in topics:
        owns += ["reusable everything", "oat milk (3 kinds)", "a tote bag with a message"]
    if "tech" in topics:
        owns += ["mechanical keyboard", "too many browser tabs"]
    if "gaming" in topics:
        owns += ["gaming chair", "RGB everything"]
    if "finance" in topics:
        owns += ["Robinhood app", "crypto hardware wallet they forgot the password to"]
    if "fitness" in topics:
        owns += ["protein powder tub", "gym bag permanently in car"]
    if "mental_health" in topics:
        owns += ["journal (barely used)", "therapy copay receipts"]
    if "politics" in topics:
        owns += ["strong opinions", "a podcast they recommend constantly"]
    if not owns:
        owns = ["Reddit Premium (gifted)", "opinions", "unfinished side projects"]
    return owns[:3]

def _topic_visuals(topics: list[str], drink: str, subreddit: str = "") -> str:
    sub = subreddit.lower()
    if sub in {"antiwork", "workreform", "antiworkaus"}:
        return "Person slumped at a boring office desk, fluorescent lighting, dead eyes, cheap coffee, business casual clothes that don't fit right, looks like they haven't slept."
    if "vegan" in topics:
        return "Person holding an oat milk latte, wearing a sustainable tote bag, farmers market or plant-filled apartment background, warm earthy tones, looks earnest and slightly judgmental."
    if "finance" in topics:
        return "Person at a desk with multiple monitors showing stock charts, energy drink nearby, slightly manic expression, dark room with screen glow, hooded sweatshirt."
    if "gaming" in topics:
        return "Person in a gaming setup, RGB lighting glow on face, headphones around neck, relaxed expression, dark room lit by monitor."
    if "fitness" in topics:
        return "Person in gym wear, slightly pumped, protein shaker nearby, gym or home gym background, confident expression."
    if "tech" in topics:
        return "Person at a standing desk, mechanical keyboard visible, multiple monitors, cold brew coffee, focused expression, modern apartment."
    if "politics" in topics:
        return "Person looking intensely at laptop screen, coffee mug, cluttered desk with papers, slightly stressed expression, home office."
    if "science" in topics:
        return "Person in casual academic setting, books and papers scattered, glasses, thoughtful expression, university library or lab background."
    if "mental_health" in topics:
        return "Person wrapped in a blanket on a couch, journal nearby, warm soft lighting, gentle introspective expression, cozy apartment."
    if "sports" in topics:
        return "Person wearing a team jersey, snacks on table, watching something intensely off-camera, couch background."
    return f"Person drinking {drink}, casual home setting, relaxed expression, soft indoor lighting."

def build_profile(subreddit: str, stats: dict) -> dict:
    sentiment = stats["sentiment"]
    style = stats["style"]
    topics = stats["topics"]
    top_words = stats["top_words"]
    top_phrases = stats["top_phrases"]
    profanity = stats["profanity_rate"]

    from llm import generate_character_details

    name = pick_name(sentiment["label"], profanity)

    # try LLM first, fall back to templates
    llm = generate_character_details(subreddit, stats)

    job = llm["job"] if llm and llm.get("job") else infer_job(topics)
    mood = llm["mood"] if llm and llm.get("mood") else infer_mood(sentiment, profanity, style, topics)
    drink = llm["drink"] if llm and llm.get("drink") else infer_drink(topics, style)
    catchphrase = llm["catchphrase"] if llm and llm.get("catchphrase") else infer_catchphrase(top_phrases, top_words, sentiment)
    age_range = llm["age_range"] if llm and llm.get("age_range") else infer_age(style, topics)
    online_hours = llm["online_hours"] if llm and llm.get("online_hours") else infer_online_hours(style)
    energy_label = llm["energy_label"] if llm and llm.get("energy_label") else None
    sentiment_vibe = llm["sentiment_vibe"] if llm and llm.get("sentiment_vibe") else None
    owns = llm["owns"] if llm and llm.get("owns") else infer_owns(topics, style)

    top_word_list = [w for w, _ in top_words[:6]]

    if llm and llm.get("image_prompt"):
        kling_prompt = (
            f"Portrait photo, age {age_range}. {llm['image_prompt']} "
            f"Photorealistic, candid, natural lighting, shallow depth of field."
        )
    else:
        visual_details = _topic_visuals(topics, drink, subreddit)
        kling_prompt = (
            f"Portrait photo of a Reddit user, age {age_range}. {visual_details} "
            f"Mood: {mood}. Photorealistic, candid style, natural lighting. "
            f"Cinematic portrait photography, shallow depth of field."
        )

    return {
        "subreddit": subreddit,
        "name": name,
        "age_range": age_range,
        "job": job,
        "mood": mood,
        "drink": drink,
        "catchphrase": catchphrase,
        "online_hours": online_hours,
        "owns": owns,
        "topics": topics,
        "top_words": top_word_list,
        "sentiment": sentiment["label"],
        "sentiment_vibe": sentiment_vibe,
        "verbosity": style["verbosity"],
        "energy_label": energy_label,
        "reading_grade": style["reading_grade"],
        "total_comments_analyzed": stats["total_comments"],
        "kling_prompt": kling_prompt,
    }
