"""
Step 2 (Music Mode): Generate a music video script.
Uses Gemini to write a funny song prompt based on tech news and generate visual segments.
"""

import json
from google import genai
from google.genai import types
from rich.console import Console

import config

console = Console()

def generate_music_script(news_items: list[dict]) -> dict:
    """
    Generate a music video script based on tech news.
    
    Returns a dict with:
        {
            "title": str,
            "description": str,
            "tags": list[str],
            "song_prompt": str,
            "segments": [
                {
                    "text": str,           # Short lyrical excerpt (for context)
                    "image_prompt": str,   # Prompt for AI image generation
                    "pop_images": [
                        {
                            "search_query": str,
                            "trigger_word": str
                        }
                    ]
                }
            ]
        }
    """
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    news_json = json.dumps(news_items, indent=2)

    prompt = f"""You are a funny YouTube Shorts creator who makes 30-second music videos about tech news.

Given these news stories, create a music video script.

NEWS STORIES:
{news_json}

REQUIREMENTS:
1. Identify the funniest or most meme-worthy news item.
2. Write a `song_prompt` (max 2 sentences) describing the song for an AI music generator (e.g., "A high energy pop-punk song about AI taking our jobs because of the new GPT release.").
3. Generate exactly 6 visual segments to cover the 30-second duration (each segment represents about 5 seconds of the video).
4. For each segment, provide:
   - `text`: A short lyric or caption describing the vibe (e.g., "Robots are coming!").
   - `image_prompt`: A detailed prompt for generating a highly relevant background image related specifically to the topic of the song (do not default to generic robotics/cyberpunk unless the song is about that).
   - `pop_images`: A list of 1-2 images/memes to pop up dynamically. Provide a `search_query`. IMPORTANT: If you want an animated GIF, explicitly append the word 'gif' to the search query (e.g., "robot dancing gif", "exploding head emoji gif"). Provide a `trigger_word`.

CRITICAL CONSTRAINTS:
- You MUST have exactly 6 segments. No more, no less.

IMPORTANT: Return ONLY valid JSON in this exact format, no markdown fences:
{{
    "title": "catchy title here #Shorts",
    "description": "engaging description with hashtags",
    "tags": ["AI", "tech", "meme"],
    "song_prompt": "prompt for the AI music generator",
    "segments": [
        {{
            "text": "lyric or caption",
            "image_prompt": "detailed image generation prompt",
            "pop_images": [
                {{
                    "search_query": "meme search query",
                    "trigger_word": "lyric"
                }}
            ]
        }}
    ]
}}
"""

    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
        )
    )

    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

    try:
        script = json.loads(raw_text)
    except json.JSONDecodeError as e:
        console.print(f"[red]Failed to parse script JSON: {e}[/red]")
        raise

    if "#Shorts" not in script.get("title", ""):
        script["title"] = script.get("title", "AI Meme Song") + " #Shorts"

    console.print(f"[green]✓ Music script generated: \"{script['title']}\"[/green]")
    console.print(f"  Song Prompt: {script.get('song_prompt')}")
    console.print(f"  Segments: {len(script.get('segments', []))}")

    return script
