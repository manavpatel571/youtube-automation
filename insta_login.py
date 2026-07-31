import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from instagrapi import Client
import config
from rich.console import Console

console = Console()

def create_trusted_session():
    console.print(f"[cyan]Logging in to generate trusted device fingerprint for @{config.INSTAGRAM_USERNAME}...[/cyan]")
    
    cl = Client()
    
    try:
        cl.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
        console.print("[green]✓ Login successful![/green]")
        
        # Save the session details
        cl.dump_settings("insta_settings.json")
        console.print("[green]✓ Saved insta_settings.json![/green]")
        console.print("\n[bold cyan]NEXT STEPS:[/bold cyan]")
        console.print("1. Open insta_settings.json in your editor.")
        console.print("2. Copy ALL the text inside it.")
        console.print("3. Create a new GitHub Secret named INSTAGRAM_SETTINGS and paste the text.")
        console.print("4. Tell the AI when you're done!")
        
    except Exception as e:
        console.print(f"[red]✗ Login failed: {e}[/red]")
        console.print("[yellow]If it asks for an email code, enter the code in your email and try running this script again.[/yellow]")

if __name__ == "__main__":
    create_trusted_session()
