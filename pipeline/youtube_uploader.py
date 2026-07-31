"""
Step 5: Upload videos to YouTube using the YouTube Data API v3.
Handles OAuth2 authentication and resumable uploads.
"""

import os
import json
from pathlib import Path
from rich.console import Console

import config

console = Console()


def _get_authenticated_service():
    """
    Build an authenticated YouTube API service.
    Uses cached token if available, otherwise runs OAuth flow.
    """
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    
    creds = None
    
    # Check for existing token
    if config.TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(config.TOKEN_FILE), SCOPES)
    
    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            console.print("[cyan]🔄 Refreshing YouTube token...[/cyan]")
            creds.refresh(Request())
        else:
            if not config.CLIENT_SECRET_FILE.exists():
                console.print("[red]✗ YouTube OAuth not set up![/red]")
                console.print(f"  Please follow the guide in SETUP_YOUTUBE.md")
                console.print(f"  Expected file: {config.CLIENT_SECRET_FILE}")
                raise FileNotFoundError(
                    f"Missing {config.CLIENT_SECRET_FILE}. See SETUP_YOUTUBE.md"
                )
            
            console.print("[cyan]🔑 Starting YouTube OAuth flow...[/cyan]")
            console.print("[dim]  A browser window will open for authentication.[/dim]")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(config.CLIENT_SECRET_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save token for future use
        config.TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(config.TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        console.print("[green]✓ YouTube token saved[/green]")
    
    return build("youtube", "v3", credentials=creds)


def upload_video(
    video_path: str | Path,
    title: str,
    description: str,
    tags: list[str] | None = None,
    privacy: str = None,
) -> dict:
    """
    Upload a video to YouTube.
    
    Args:
        video_path: Path to the MP4 file.
        title: Video title (should include #Shorts).
        description: Video description.
        tags: List of tags.
        privacy: Privacy status (private/unlisted/public).
        
    Returns:
        YouTube API response dict with video ID.
    """
    from googleapiclient.http import MediaFileUpload
    
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    privacy = privacy or config.DEFAULT_PRIVACY
    tags = tags or ["AI", "tech", "artificial intelligence", "Shorts"]
    
    youtube = _get_authenticated_service()
    
    console.print(f"[cyan]📤 Uploading to YouTube...[/cyan]")
    console.print(f"  Title: {title}")
    console.print(f"  Privacy: {privacy}")
    
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": config.YOUTUBE_CATEGORY_ID,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    
    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024,  # 1MB chunks
    )
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )
    
    # Execute with progress tracking
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            console.print(f"  ⬆ Upload progress: {progress}%")
    
    video_id = response["id"]
    video_url = f"https://youtube.com/shorts/{video_id}"
    
    console.print(f"[green]✓ Upload complete![/green]")
    console.print(f"  Video ID: {video_id}")
    console.print(f"  URL: {video_url}")
    console.print(f"  Status: {privacy} (change in YouTube Studio)")
    
    return response


if __name__ == "__main__":
    print("Use 'python main.py upload <filename>' to upload videos.")
    print("Make sure you've set up YouTube OAuth first (see SETUP_YOUTUBE.md).")
