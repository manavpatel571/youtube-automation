import os
import time
import requests
from dotenv import load_dotenv

load_dotenv("d:\\youtube\\auto_video\\.env")
access_token = os.getenv("META_ACCESS_TOKEN")
ig_user_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
video_url = "https://files.catbox.moe/37dfzo.mp4"
caption = "Testing upload via Catbox CDN #shorts"

# 1. Create Container
init_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
init_payload = {
    "access_token": access_token,
    "media_type": "REELS",
    "video_url": video_url,
    "caption": caption
}
print("Creating container...")
res = requests.post(init_url, data=init_payload).json()
print("Create response:", res)

if "id" not in res:
    print("FAILED")
    exit(1)
    
container_id = res["id"]

# 2. Wait for Processing
status_url = f"https://graph.facebook.com/v19.0/{container_id}?fields=status_code&access_token={access_token}"
for _ in range(10):
    time.sleep(5)
    status_res = requests.get(status_url).json()
    status = status_res.get("status_code")
    print("Status:", status)
    if status == "FINISHED":
        break
    if status == "ERROR":
        print("FAILED PROCESSING")
        exit(1)

# 3. Publish
publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
publish_payload = {
    "access_token": access_token,
    "creation_id": container_id
}
print("Publishing...")
pub_res = requests.post(publish_url, data=publish_payload).json()
print("Publish Response:", pub_res)
