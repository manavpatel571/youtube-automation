"""
Step 2: Generate an engaging YouTube Shorts script from news items.
Uses Gemini to write a fast-paced voiceover script with visual cues.
"""

import json
from google import genai
from google.genai import types
from rich.console import Console

import config

console = Console()


def generate_script(news_items: list[dict]) -> dict:
    """
    Generate a complete YouTube Shorts script from news items.
    
    Returns a dict with:
        {
            "title": str,           # YouTube title (includes #Shorts)
            "description": str,     # YouTube description
            "tags": list[str],      # YouTube tags
            "full_script": str,     # Complete voiceover text
            "segments": [
                {
                    "text": str,            # Voiceover text for this segment
                    "image_prompt": str,    # Prompt for AI image generation
                    "pop_images": [         # List of images/memes to pop up
                        {
                            "search_query": str,  # Image search query (e.g. "Google logo", "OpenAI news", "confused meme")
                            "trigger_word": str   # The exact word in the text after which this image pops up
                        }
                    ]
                }
            ]
        }
    """
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    news_json = json.dumps(news_items, indent=2)

    prompt = f"""You are a viral YouTube Shorts scriptwriter for a tech/AI news channel.

Given these news stories, create a {config.TARGET_DURATION_SECONDS}-second YouTube Short script.

NEWS STORIES:
{news_json}

REQUIREMENTS:
1. HOOK (first 3 seconds): Start with a shocking/exciting hook to stop scrollers. Examples:
   - "You won't BELIEVE what Google just dropped!"
   - "AI just changed FOREVER. Here's why."
   - "This changes everything about AI."

2. BODY (exactly 4-5 news segments, ~6-8 seconds each): 
   - Feature a two-person banter! We have a "main" anchor (male) and a "girl" co-host.
   - The "main" anchor introduces the tech news seriously but energetically.
   - The "girl" co-host chimes in with funny, relatable meme commentary, reactions, or jokes.
   - Keep each segment to 1-2 SHORT sentences max — no filler.

3. OUTRO (last 3 seconds):
   - End with a call to action from either speaker: "Follow for daily AI drops!" or similar

4. For each segment, also provide:
   - image_prompt: A detailed prompt for generating a futuristic/tech background image 
     (dark theme, neon accents, cyberpunk style). Be specific about what to show.
   - pop_images: A list of 1-2 images to pop up dynamically during the segment to keep retention high.
     These should be a mix of relatable MEMES (e.g. "mind blown meme") and NEWS-RELATED IMAGES/SCREENSHOTS (e.g. "Google AI logo", "Sam Altman", "OpenAI news article").
     For each pop_image, provide a `search_query` and a `trigger_word` 
     (the exact word in the text that should trigger the image to appear).

CRITICAL CONSTRAINTS:
- The full_script MUST be 80-100 words MAXIMUM. Count carefully!
- You MUST have exactly 4-6 segments total.
- Each segment must have a `speaker` field which is strictly either "main" or "girl". Make sure they alternate or have a natural flow!
- Each segment text should be 10-20 words max.

IMPORTANT: Return ONLY valid JSON in this exact format, no markdown fences:
{{
    "title": "catchy title here #Shorts",
    "description": "engaging description with hashtags",
    "tags": ["AI", "tech", ...],
    "full_script": "complete voiceover text as one paragraph",
    "segments": [
        {{
            "speaker": "main",
            "text": "voiceover text for this part",
            "image_prompt": "detailed image generation prompt",
            "pop_images": [
                {{
                    "search_query": "Google Gemini logo",
                    "trigger_word": "dropped"
                }}
            ]
        }}
    ]
}}

Make the title click-worthy with emojis. Include 5-8 relevant tags.
The full_script should be ALL segment texts combined, smooth and natural.
Target 80-100 words total — this should be about 35-40 seconds when spoken at normal pace."""

    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,  # More creative
        )
    )

    raw_text = response.text.strip()

    # Clean up markdown fences if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

    try:
        script = json.loads(raw_text)
    except json.JSONDecodeError as e:
        console.print(f"[red]Failed to parse script JSON: {e}[/red]")
        console.print(f"[dim]Raw response:[/dim]\n{raw_text}")
        raise

    # Ensure #Shorts is in the title
    if "#Shorts" not in script.get("title", ""):
        script["title"] = script.get("title", "AI News") + " #Shorts"

    console.print(f"[green]✓ Script generated: \"{script['title']}\"[/green]")
    console.print(f"  Segments: {len(script.get('segments', []))}")
    
    word_count = len(script.get("full_script", "").split())
    est_duration = word_count / 2.5  # ~150 words/minute = 2.5 words/second
    console.print(f"  Words: {word_count} | Est. duration: {est_duration:.0f}s")

    return script


if __name__ == "__main__":
    # Test with sample news
    sample_news = [
        {
            "headline": "Google releases Gemini 3",
            "summary": "Google announced Gemini 3, their most powerful AI model yet.",
            "source": "Google",
            "importance": 9
        },
        {
            "headline": "OpenAI launches GPT-5 Turbo",
            "summary": "OpenAI's GPT-5 Turbo brings faster inference and better reasoning.",
            "source": "OpenAI",
            "importance": 8
        },
    ]
    result = generate_script(sample_news)
    print(json.dumps(result, indent=2))
