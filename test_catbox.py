import requests

def upload_to_catbox(filepath):
    print("Uploading to catbox.moe...")
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload"}
    with open(filepath, "rb") as f:
        res = requests.post(url, data=data, files={"fileToUpload": f})
    
    print("Catbox response:", res.text)
    return res.text

upload_to_catbox("output/uploaded/short_2026-07-31_19-42-49.mp4")
