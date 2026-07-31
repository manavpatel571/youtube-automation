"""
Central configuration for the auto-video pipeline.
Loads environment variables and defines all constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent / ".env")

# ── API Keys ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
YOUTUBE_TOKEN = os.getenv("YOUTUBE_TOKEN")
VOICE_ID = os.getenv("VOICE_ID", "mttGjNqgkgo5cciwsyoc")

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
DRAFTS_DIR = OUTPUT_DIR / "drafts"
UPLOADED_DIR = OUTPUT_DIR / "uploaded"
ASSETS_DIR = PROJECT_ROOT / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
CREDENTIALS_DIR = PROJECT_ROOT / "credentials"
CLIENT_SECRET_FILE = CREDENTIALS_DIR / "client_secret.json"
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
HISTORY_FILE = PROJECT_ROOT / "history.json"

# Create directories
for d in [DRAFTS_DIR, UPLOADED_DIR, ASSETS_DIR, FONTS_DIR, CREDENTIALS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Video Settings ────────────────────────────────────────────────────────────
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
MAX_DURATION_SECONDS = 55  # YouTube Shorts max is 60s, leave buffer
TARGET_DURATION_SECONDS = 45  # Aim for ~45 seconds of content

# ── Gemini Settings ───────────────────────────────────────────────────────────
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"

# ── ElevenLabs Settings ──────────────────────────────────────────────────────
ELEVENLABS_MODEL = "eleven_multilingual_v2"

# ── Content Settings ─────────────────────────────────────────────────────────
NEWS_TOPICS = [
    "Google AI", "OpenAI", "Meta AI", "HuggingFace",
    "open-source AI models", "LLM updates", "AI tools",
    "machine learning breakthroughs", "AI startups",
]

# YouTube upload settings
YOUTUBE_CATEGORY_ID = "28"  # Science & Technology
DEFAULT_PRIVACY = "public"  # Upload as public so it's instantly live

# ── Visual Style ──────────────────────────────────────────────────────────────
# Dark futuristic theme colors
COLORS = {
    "bg_dark": (10, 10, 20),
    "bg_gradient_top": (15, 10, 40),
    "bg_gradient_bottom": (5, 5, 15),
    "accent_cyan": (0, 240, 255),
    "accent_purple": (160, 50, 255),
    "accent_pink": (255, 50, 150),
    "text_white": (255, 255, 255),
    "text_gray": (180, 180, 200),
    "overlay_dark": (0, 0, 0, 180),  # RGBA
}
