import os
import time
import requests
from pathlib import Path
from rich.console import Console

console = Console()

def upload_reel(video_path: str, caption: str) -> bool:
    """
    Uploads a video to Instagram Reels using the Official Meta Graph API.
    Uses the Resumable Upload API to upload the local video file.
    """
    access_token = os.getenv("META_ACCESS_TOKEN")
    ig_user_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

    if not access_token or not ig_user_id:
        console.print("[red]✗ META_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID not found in environment![/red]")
        return False

    console.print(f"[cyan]📱 Initializing Instagram Reel upload via Meta Graph API...[/cyan]")
    
    file_size = os.path.getsize(video_path)
    
    # STEP 1: Initialize Resumable Upload Session
    init_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
    init_payload = {
        "access_token": access_token,
        "media_type": "REELS",
        "upload_type": "resumable",
        "caption": caption
    }
    
    init_res = requests.post(init_url, data=init_payload).json()
    
    if "id" not in init_res:
        console.print(f"[red]✗ Failed to initialize upload session: {init_res}[/red]")
        return False
        
    container_id = init_res["id"]
    console.print(f"[dim]Upload session started. Container ID: {container_id}[/dim]")
    
    # STEP 2: Upload the video binary
    console.print(f"[cyan]📤 Uploading video data ({file_size} bytes)...[/cyan]")
    upload_url = f"https://rupload.facebook.com/ig-api-upload/v19.0/{container_id}"
    
    headers = {
        "Authorization": f"OAuth {access_token}",
        "offset": "0",
        "file_size": str(file_size),
        "Content-Type": "application/octet-stream"
    }
    
    with open(video_path, "rb") as f:
        video_data = f.read()
        
    upload_res = requests.post(upload_url, headers=headers, data=video_data)
    
    if upload_res.status_code != 200:
        console.print(f"[red]✗ Failed to upload video binary: {upload_res.text}[/red]")
        return False
        
    console.print("[green]✓ Video data uploaded successfully![/green]")
    
    # STEP 3: Check Status and Publish
    console.print("[cyan]⏳ Waiting for Meta servers to process the video...[/cyan]")
    status_url = f"https://graph.facebook.com/v19.0/{container_id}?fields=status_code&access_token={access_token}"
    
    max_retries = 10
    ready = False
    
    for _ in range(max_retries):
        time.sleep(10)
        status_res = requests.get(status_url).json()
        status = status_res.get("status_code")
        
        console.print(f"[dim]Status: {status}[/dim]")
        
        if status == "FINISHED":
            ready = True
            break
        elif status == "ERROR":
            console.print("[red]✗ Meta failed to process the video.[/red]")
            return False
            
    if not ready:
        console.print("[red]✗ Timed out waiting for video processing.[/red]")
        return False
        
    # STEP 4: Publish
    console.print("[cyan]📢 Publishing Reel...[/cyan]")
    publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
    publish_payload = {
        "access_token": access_token,
        "creation_id": container_id
    }
    
    publish_res = requests.post(publish_url, data=publish_payload).json()
    
    if "id" in publish_res:
        console.print(f"[green]✓ Instagram Reel published successfully! Media ID: {publish_res['id']}[/green]")
        return True
    else:
        console.print(f"[red]✗ Failed to publish Reel: {publish_res}[/red]")
        return False

if __name__ == "__main__":
    pass
