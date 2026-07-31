"""
Main CLI entry point for the Auto Video pipeline.
Orchestrates: news fetch → script → voice → images → video → upload.

Usage:
    python main.py generate          # Create a new video draft
    python main.py upload <file>     # Upload a draft to YouTube
    python main.py full              # Generate + upload
    python main.py list              # List pending drafts
"""

import sys
import os
import json
import shutil
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding for emoji/unicode support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import config
from pipeline.news_fetcher import fetch_news
from pipeline.script_writer import generate_script
from pipeline.voice_generator import generate_voice_for_script
from pipeline.meme_fetcher import fetch_memes_for_script
from pipeline.image_generator import generate_all_images
from pipeline.video_composer import compose_video
from pipeline.youtube_uploader import upload_video

console = Console()


def _check_ffmpeg():
    """Verify ffmpeg is available on the system."""
    if shutil.which("ffmpeg") is None:
        console.print("[red]✗ ffmpeg not found![/red]")
        console.print("  MoviePy requires ffmpeg to encode video.")
        console.print("  Install it:")
        console.print("    Windows: winget install ffmpeg")
        console.print("    Or download from: https://ffmpeg.org/download.html")
        sys.exit(1)


def cmd_generate() -> Path | None:
    """Run the full generation pipeline (Steps 1-4)."""
    console.print(Panel(
        "🚀 [bold cyan]Auto Video Generator[/bold cyan]\n"
        "[dim]Fetching news → Script → Voice → Images → Video[/dim]",
        border_style="cyan",
    ))
    
    _check_ffmpeg()
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    work_dir = config.DRAFTS_DIR / timestamp
    work_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # ── Step 1: Fetch News ────────────────────────────────────────────
        console.print("\n[bold]━━━ Step 1/5: Fetching Latest AI News ━━━[/bold]")
        news_items = fetch_news(num_stories=4)
        
        # Save news for reference
        with open(work_dir / "news.json", "w") as f:
            json.dump(news_items, f, indent=2)
        
        # ── Step 2: Generate Script ───────────────────────────────────────
        console.print("\n[bold]━━━ Step 2/5: Writing Script ━━━[/bold]")
        script = generate_script(news_items)
        
        # Save script for reference
        with open(work_dir / "script.json", "w") as f:
            json.dump(script, f, indent=2)
        
        # ── Step 3: Generate Voice ────────────────────────────────────────
        console.print("\n[bold]━━━ Step 3/5: Generating Voiceover ━━━[/bold]")
        script = generate_voice_for_script(script, work_dir)
        
        # Calculate total duration
        total_duration = sum(s.get("duration", 0) for s in script.get("segments", []))
        console.print(f"  Total audio duration: {total_duration:.1f}s")
        
        if total_duration > config.MAX_DURATION_SECONDS:
            console.print(
                f"[yellow]  ⚠ Audio is {total_duration:.1f}s "
                f"(max {config.MAX_DURATION_SECONDS}s). Will be trimmed.[/yellow]"
            )
            
        # ── Step 4a: Fetch Memes ──────────────────────────────────────────
        console.print("\n[bold]━━━ Step 4a/5: Fetching Memes ━━━[/bold]")
        script = fetch_memes_for_script(script, work_dir)
        
        # ── Step 4b: Generate Images ───────────────────────────────────────
        console.print("\n[bold]━━━ Step 4b/5: Generating Background Images ━━━[/bold]")
        image_paths = generate_all_images(script["segments"], work_dir)
        
        # ── Step 5: Compose Video ─────────────────────────────────────────
        console.print("\n[bold]━━━ Step 5/5: Composing Video ━━━[/bold]")
        video_filename = f"short_{timestamp}.mp4"
        video_path = work_dir / video_filename
        
        compose_video(script, image_paths, video_path)
        
        # ── Done ──────────────────────────────────────────────────────────
        console.print()
        console.print(Panel(
            f"[bold green]✅ Video Generated Successfully![/bold green]\n\n"
            f"📁 Draft: [cyan]{video_path}[/cyan]\n"
            f"📝 Title: {script['title']}\n"
            f"⏱  Duration: {total_duration:.1f}s\n\n"
            f"[dim]Review the video, then upload with:[/dim]\n"
            f"  python main.py upload {video_filename}",
            border_style="green",
            title="🎉 Complete",
        ))
        
        return video_path
    
    except Exception as e:
        console.print(f"\n[red]✗ Pipeline failed: {e}[/red]")
        console.print_exception()
        return None


def cmd_upload(filename: str):
    """Upload a draft video to YouTube."""
    console.print(Panel(
        f"📤 [bold cyan]YouTube Upload[/bold cyan]\n"
        f"[dim]File: {filename}[/dim]",
        border_style="cyan",
    ))
    
    # Find the video file
    video_path = None
    
    # Check if it's a full path
    if Path(filename).exists():
        video_path = Path(filename)
    else:
        # Search in drafts directories
        for draft_dir in sorted(config.DRAFTS_DIR.iterdir(), reverse=True):
            if draft_dir.is_dir():
                candidate = draft_dir / filename
                if candidate.exists():
                    video_path = candidate
                    break
                # Also try matching without exact name
                for f in draft_dir.glob("*.mp4"):
                    if filename in f.name:
                        video_path = f
                        break
    
    if not video_path:
        console.print(f"[red]✗ Video not found: {filename}[/red]")
        console.print("  Use 'python main.py list' to see available drafts.")
        return
    
    # Load the script metadata if available
    script_file = video_path.parent / "script.json"
    if script_file.exists():
        with open(script_file) as f:
            script = json.load(f)
        title = script.get("title", "AI News Update #Shorts")
        description = script.get("description", "Latest AI and tech news!")
        tags = script.get("tags", ["AI", "tech"])
    else:
        title = "AI News Update #Shorts"
        description = "Latest AI and tech news! Follow for daily updates."
        tags = ["AI", "tech", "artificial intelligence", "Shorts"]
    
    try:
        response = upload_video(video_path, title, description, tags)
        
        # Move to uploaded directory
        uploaded_dest = config.UPLOADED_DIR / video_path.name
        shutil.copy2(video_path, uploaded_dest)
        console.print(f"[dim]  Copied to: {uploaded_dest}[/dim]")
        
    except FileNotFoundError as e:
        console.print(f"[red]✗ {e}[/red]")
        console.print("  Run the YouTube setup first: see SETUP_YOUTUBE.md")
    except Exception as e:
        console.print(f"[red]✗ Upload failed: {e}[/red]")
        console.print_exception()


def cmd_full():
    """Generate a video and upload it immediately."""
    video_path = cmd_generate()
    if video_path:
        console.print("\n[bold]━━━ Auto-Uploading to YouTube ━━━[/bold]")
        cmd_upload(str(video_path))


def cmd_list():
    """List all pending draft videos."""
    console.print(Panel(
        "📋 [bold cyan]Draft Videos[/bold cyan]",
        border_style="cyan",
    ))
    
    if not config.DRAFTS_DIR.exists():
        console.print("[dim]  No drafts found.[/dim]")
        return
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Date", style="dim")
    table.add_column("File")
    table.add_column("Size", justify="right")
    table.add_column("Title")
    
    found = False
    for draft_dir in sorted(config.DRAFTS_DIR.iterdir(), reverse=True):
        if draft_dir.is_dir():
            for mp4 in draft_dir.glob("*.mp4"):
                found = True
                size_mb = mp4.stat().st_size / (1024 * 1024)
                
                # Try to load title from script
                script_file = draft_dir / "script.json"
                title = "—"
                if script_file.exists():
                    with open(script_file) as f:
                        script = json.load(f)
                    title = script.get("title", "—")
                
                table.add_row(
                    draft_dir.name,
                    mp4.name,
                    f"{size_mb:.1f} MB",
                    title,
                )
    
    if found:
        console.print(table)
        console.print("\n[dim]Upload with: python main.py upload <filename>[/dim]")
    else:
        console.print("[dim]  No draft videos found. Run 'python main.py generate' first.[/dim]")


def main():
    """Main entry point — parse CLI arguments."""
    if len(sys.argv) < 2:
        console.print(Panel(
            "[bold]Auto Video — YouTube Shorts Generator[/bold]\n\n"
            "Commands:\n"
            "  [cyan]generate[/cyan]          Fetch news & create a video draft\n"
            "  [cyan]upload <file>[/cyan]     Upload a draft to YouTube\n"
            "  [cyan]full[/cyan]              Generate + upload in one step\n"
            "  [cyan]list[/cyan]              Show pending drafts\n\n"
            "Usage: python main.py <command>",
            border_style="cyan",
            title="📺 Help",
        ))
        return
    
    command = sys.argv[1].lower()
    
    if command == "generate":
        cmd_generate()
    elif command == "upload":
        if len(sys.argv) < 3:
            console.print("[red]Usage: python main.py upload <filename>[/red]")
            return
        cmd_upload(sys.argv[2])
    elif command == "full":
        cmd_full()
    elif command == "list":
        cmd_list()
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print("  Use: generate | upload | full | list")


if __name__ == "__main__":
    main()
