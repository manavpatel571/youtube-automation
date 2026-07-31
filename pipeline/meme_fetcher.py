"""
Step 4a: Fetch pop images (memes or news screenshots) from the web using Serper API.
"""

from pathlib import Path
from rich.console import Console
from PIL import Image
import io
import requests
import json
import urllib.parse
import time
import config

console = Console()

def fetch_memes_for_script(script: dict, drafts_dir: Path) -> dict:
    """
    Downloads pop images for the script segments and updates the script with local paths.
    """
    console.print("[cyan]🖼 Fetching pop images from the web...[/cyan]")
    
    if not config.SERPER_API_KEY:
        console.print("[red]⚠ SERPER_API_KEY not found in config! Images will be skipped.[/red]")
        return script
        
    headers = {
        'X-API-KEY': config.SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    for i, segment in enumerate(script.get("segments", [])):
        pop_images = segment.get("pop_images", [])
        # Also support older 'memes' key just in case
        pop_images.extend(segment.get("memes", []))
        
        for image_item in pop_images:
            query = image_item.get("search_query")
            if not query:
                continue
            
            img_filename = f"segment_{i}_pop_{query.replace(' ', '_')[:20]}.png"
            img_filename = "".join([c for c in img_filename if c.isalnum() or c in "_."])
            img_path = drafts_dir / img_filename
            
            console.print(f"[cyan]  → Searching Serper for '{query}'...[/cyan]")
            
            try:
                # Search using Serper Image API
                url = "https://google.serper.dev/images"
                payload = json.dumps({"q": query, "num": 1})
                response = requests.post(url, headers=headers, data=payload, timeout=15)
                response.raise_for_status()
                
                results = response.json()
                images_list = results.get("images", [])
                
                if images_list:
                    # Get first valid image URL
                    target_url = images_list[0].get("imageUrl")
                    
                    if target_url:
                        console.print(f"    Found image URL: {target_url[:50]}...")
                        # Download the image itself
                        img_req = requests.get(target_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
                        img_req.raise_for_status()
                        
                        img = Image.open(io.BytesIO(img_req.content))
                        # Convert to RGBA if necessary
                        if img.mode != "RGBA":
                            img = img.convert("RGBA")
                        img.thumbnail((600, 600))
                        img.save(img_path, "PNG")
                        
                        console.print(f"[green]    ✓ Downloaded {img_filename}[/green]")
                        image_item["local_path"] = str(img_path)
                    else:
                        console.print(f"[yellow]    ⚠ No valid imageUrl in Serper response for '{query}'[/yellow]")
                else:
                    console.print(f"[yellow]    ⚠ No images found by Serper for '{query}'[/yellow]")
                    
            except Exception as e:
                console.print(f"[red]    ⚠ Image fetch failed for '{query}': {e}[/red]")
                
        # Make sure the new pop_images array is what video_composer reads
        segment["memes"] = pop_images

    console.print("[green]✓ Pop image fetching complete[/green]")
    return script
