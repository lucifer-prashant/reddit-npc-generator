import urllib.parse

async def generate_image(prompt: str) -> str | None:
    encoded = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true&model=turbo"
