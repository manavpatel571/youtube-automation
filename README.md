# YouTube Shorts — AI/Tech News Auto-Generator

Automated pipeline to create and upload YouTube Shorts about the latest AI and tech news.

## Quick Start

```bash
# 1. Install dependencies
pip install -e .

# 2. Set up YouTube API (one-time) — see SETUP_YOUTUBE.md

# 3. Generate a video
python main.py generate

# 4. Review the draft in output/drafts/

# 5. Upload to YouTube
python main.py upload <filename>
```

## Commands

| Command | Description |
|---------|-------------|
| `python main.py generate` | Fetch news → write script → generate voice → create video |
| `python main.py upload <file>` | Upload a draft video to YouTube (as private) |
| `python main.py full` | Generate + upload in one go |
| `python main.py list` | List pending draft videos |

## API Keys Required

- **Gemini API** — for news fetching, script writing, image generation
- **ElevenLabs API** — for text-to-speech voiceover
- **YouTube OAuth** — for automated uploads (see SETUP_YOUTUBE.md)
