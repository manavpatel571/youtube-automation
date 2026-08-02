import os
import requests

token = "EAAOeeu1HzesBSDNa24JiBjMacaLZA7EqgZC2fy1W2F6VRkAxZAPzOXBf5yjHzQtE6ItAqCSplqHiUCbM7RTWcbyZCMcAUDw6qQghnRJDTZB7wOUvZABGhviDyvmllaAiaFyljUF4iGfRjG0d5chybsk3qvEW81sFgMAmSoXOXXGQZC0ldhcutJyQujFceKT4wZDZD"
url = f"https://graph.facebook.com/v19.0/me/accounts?fields=instagram_business_account&access_token={token}"

res = requests.get(url).json()

print(res)

ig_id = None
if "data" in res:
    for page in res["data"]:
        if "instagram_business_account" in page:
            ig_id = page["instagram_business_account"]["id"]
            break

if ig_id:
    print(f"FOUND IG ID: {ig_id}")
    with open("d:\\youtube\\auto_video\\.env", "a") as f:
        f.write(f"\nINSTAGRAM_ACCOUNT_ID={ig_id}\n")
else:
    print("NO IG ID FOUND")
