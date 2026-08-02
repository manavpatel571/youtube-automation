"""
Step 3 (Music Mode): Generate a music track using the ElevenLabs Music API.
"""

import time
import requests
from pathlib import Path
from rich.console import Console

import config

console = Console()


def generate_music(prompt: str, output_dir: Path) -> Path:
    """
    Generate a 30-second music track using the ElevenLabs Music API.
    """
    output_path = output_dir / "elevenlabs_music.mp3"
    
    console.print(f"  [dim]Sending request to ElevenLabs Music API for prompt: '{prompt}'[/dim]")
    
    url = "https://api.elevenlabs.io/v1/sound-generation" # Alternatively, /v1/music/compose if the SDK supports it, but sound-generation handles text-to-music for many models. Let's try the official SDK first for safety.
    
    # Try the official SDK first, fallback to REST API if needed
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
        
        # We try to use the newest music API
        if hasattr(client, "music") and hasattr(client.music, "compose"):
            console.print("  [dim]Using ElevenLabs SDK music.compose...[/dim]")
            track = client.music.compose(
                prompt=prompt,
                music_length_ms=30000,
                model_id="music_v2",
            )
            with open(output_path, "wb") as f:
                for chunk in track:
                    f.write(chunk)
            console.print(f"  [green]✓ Music generated and saved to {output_path.name}[/green]")
            return output_path
    except ImportError:
        console.print("  [dim]elevenlabs SDK not available or old, falling back to REST API...[/dim]")
        
    # REST API fallback
    headers = {
        "xi-api-key": config.ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Try /v1/sound-generation first, as it's the more stable generalized endpoint
    # for sound effects and short audio in some versions.
    # But wait, the docs said /v1/music/compose is the one. We'll try that.
    payload = {
        "text": prompt, # For sound-generation it's usually 'text'
        "duration_seconds": 30
    }
    
    res = requests.post("https://api.elevenlabs.io/v1/sound-generation", headers=headers, json=payload)
    if not res.ok:
        console.print(f"[red]ElevenLabs API Error: {res.text}[/red]")
        res.raise_for_status()
        
    with open(output_path, "wb") as f:
        f.write(res.content)
        
    console.print(f"  [green]✓ Music generated and saved to {output_path.name}[/green]")
    return output_path
