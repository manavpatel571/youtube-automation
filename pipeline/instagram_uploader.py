"""
Step 6: Upload videos to Instagram Reels.
Uses the unofficial instagrapi library.
"""

import os
from pathlib import Path
from rich.console import Console

import config

console = Console()


def upload_reel(
    video_path: str | Path,
    caption: str,
) -> bool:
    """
    Upload a video to Instagram Reels.
    
    Args:
        video_path: Path to the MP4 file.
        caption: Caption for the Reel (including hashtags).
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        from instagrapi import Client
    except ImportError:
        console.print("[red]✗ instagrapi is not installed. Run 'pip install instagrapi'[/red]")
        return False

    video_path = Path(video_path)
    if not video_path.exists():
        console.print(f"[red]✗ Video not found: {video_path}[/red]")
        return False

    if not config.INSTAGRAM_USERNAME or not config.INSTAGRAM_PASSWORD:
        console.print("[red]✗ Instagram credentials not set in config/environment![/red]")
        return False

    console.print(f"[cyan]📱 Logging into Instagram as @{config.INSTAGRAM_USERNAME}...[/cyan]")
    
    try:
        cl = Client()
        cl.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
        
        console.print(f"[cyan]📤 Uploading Reel to Instagram...[/cyan]")
        media = cl.clip_upload(
            str(video_path),
            caption
        )
        
        console.print(f"[green]✓ Instagram Reel uploaded successfully![/green]")
        try:
            console.print(f"  Media ID: {media.pk}")
        except:
            pass
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed to upload to Instagram: {e}[/red]")
        return False


if __name__ == "__main__":
    print("Use 'python main.py upload <filename>' to test uploads.")
