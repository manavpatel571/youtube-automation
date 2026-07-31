"""
Step 1: Fetch latest AI/Tech news using Gemini with Google Search grounding.
Returns structured news items for script generation.
"""

import json
from google import genai
from google.genai import types
from rich.console import Console

import config

console = Console()


def fetch_news(num_stories: int = 4) -> list[dict]:
    """
    Fetch the latest AI and tech news using Gemini + Google Search.
    
    Returns a list of dicts:
        [{"headline": str, "summary": str, "source": str, "importance": int}, ...]
    """
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    
    import random
    # Pick 2-3 random topics each run so the daily videos have different themes
    selected_topics = random.sample(config.NEWS_TOPICS, min(3, len(config.NEWS_TOPICS)))
    topics_str = ", ".join(selected_topics)
    
    prompt = f"""You are a tech news researcher. Search for the LATEST and most impactful 
AI and technology news from the last 3-4 days. Focus on these areas: {topics_str}.

Find the top {num_stories} most exciting/important stories. For each story, provide:
1. headline - a catchy, concise headline
2. summary - 2-3 sentence summary of what happened and why it matters
3. source - the company/organization involved (e.g., "Google", "OpenAI")
4. importance - score from 1-10 (10 = most impactful)

IMPORTANT: Return ONLY valid JSON in this exact format, no markdown code fences:
[
    {{
        "headline": "...",
        "summary": "...",
        "source": "...",
        "importance": 8
    }}
]

Sort by importance (highest first). Only include genuinely NEW stories from the last few days."""

    # Enable Google Search grounding for real-time data
    google_search_tool = types.Tool(
        google_search=types.GoogleSearch()
    )

    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[google_search_tool],
            temperature=0.3,
        )
    )

    # Parse the JSON response
    raw_text = response.text.strip()
    
    # Clean up in case Gemini wraps it in markdown code fences
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]  # Remove first line
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

    try:
        news_items = json.loads(raw_text)
    except json.JSONDecodeError as e:
        console.print(f"[red]Failed to parse news JSON: {e}[/red]")
        console.print(f"[dim]Raw response:[/dim]\n{raw_text}")
        raise

    # Validate and limit
    news_items = news_items[:num_stories]
    
    console.print(f"[green]✓ Fetched {len(news_items)} news stories[/green]")
    for i, item in enumerate(news_items, 1):
        console.print(f"  {i}. [{item.get('source', '?')}] {item.get('headline', '?')}")

    return news_items


if __name__ == "__main__":
    stories = fetch_news()
    print(json.dumps(stories, indent=2))
