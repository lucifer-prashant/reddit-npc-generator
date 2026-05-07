import os
import json
from openai import OpenAI

MODEL = "meta/llama-3.3-70b-instruct"

def get_client() -> OpenAI | None:
    key = os.getenv("NVIDIA_API_KEY")
    if not key:
        return None
    return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=key)

def generate_character_details(subreddit: str, stats: dict) -> dict | None:
    client = get_client()
    if not client:
        return None

    top_words = [w for w, _ in stats["top_words"][:10]]
    top_phrases = stats["top_phrases"][:5]
    sentiment = stats["sentiment"]["label"]
    topics = stats["topics"]
    style = stats["style"]
    profanity = stats["profanity_rate"]

    prompt = (
        f"Generate a funny character profile for the average r/{subreddit} reddit user based on this data.\n"
        f"Top words: {top_words}\n"
        f"Phrases: {top_phrases}\n"
        f"Sentiment: {sentiment}, topics: {topics}, style: {style['verbosity']}, profanity: {profanity}\n\n"
        f"Output ONLY a JSON object with exactly these keys:\n"
        f"- mood (max 6 words)\n"
        f"- drink (max 6 words)\n"
        f"- catchphrase (max 10 words, something they'd actually say)\n"
        f"- owns (array of 3 items, max 6 words each)\n"
        f"- job (max 5 words)\n"
        f"- age_range (e.g. '22-28' or '30-40', infer from community vibe and vocabulary)\n"
        f"- online_hours (max 6 words, when/how they post, e.g. '3am doom scrolling', 'lunch break at work')\n"
        f"- energy_label (max 5 words, how they communicate, community-specific, e.g. 'types in all caps', 'writes essays unprompted', 'sends memes only')\n"
        f"- sentiment_vibe (max 5 words, their emotional signature, e.g. 'aggressively optimistic', 'perpetual victim energy')\n"
        f"- image_prompt (one sentence describing what this person looks like, their environment, expression, clothing — for an AI portrait generator. Be specific to this community.)\n"
        f"Be funny and specific. No explanation, just the JSON."
    )

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=500,
        )
        msg = resp.choices[0].message
        raw = msg.content or getattr(msg, "reasoning_content", None) or ""
        raw = raw.strip()
        # extract JSON from markdown block if wrapped
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        # find JSON object in case model added prose around it
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            print(f"[llm] no JSON found in response: {raw[:200]}")
            return None
        return json.loads(raw[start:end])
    except Exception as e:
        print(f"[llm] error: {e}")
        return None
