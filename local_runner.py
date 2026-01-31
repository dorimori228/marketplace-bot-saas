import os
import json
import time
import tempfile
from datetime import datetime

import requests

from bot import MarketplaceBot


API_URL = os.getenv("API_URL", "https://marketplace-bot-saas-production.up.railway.app/api")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "15"))


def _auth_headers():
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }


def fetch_pending_listings():
    response = requests.get(
        f"{API_URL}/listings?status=pending&limit=20",
        headers=_auth_headers(),
        timeout=30
    )
    response.raise_for_status()
    return response.json().get("listings", [])


def fetch_account_cookies(account_id):
    response = requests.get(
        f"{API_URL}/accounts/{account_id}/cookies",
        headers=_auth_headers(),
        timeout=30
    )
    response.raise_for_status()
    return response.json().get("cookies", [])


def download_images(images):
    temp_dir = tempfile.mkdtemp(prefix="listing_images_")
    file_paths = []
    for idx, image in enumerate(images):
        url = image.get("image_url")
        if not url:
            continue
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        file_path = os.path.join(temp_dir, f"image_{idx}.jpg")
        with open(file_path, "wb") as f:
            f.write(resp.content)
        file_paths.append(file_path)
    return file_paths


def update_listing(listing_id, payload):
    response = requests.put(
        f"{API_URL}/listings/{listing_id}/status",
        headers=_auth_headers(),
        data=json.dumps(payload),
        timeout=30
    )
    response.raise_for_status()


def run_listing(listing):
    listing_id = listing["id"]
    account_id = listing.get("fb_account_id")

    if not account_id:
        update_listing(listing_id, {
            "status": "failed",
            "error_message": "Missing account id for listing"
        })
        return

    cookies = fetch_account_cookies(account_id)
    if not cookies:
        update_listing(listing_id, {
            "status": "failed",
            "error_message": "No cookies available for account"
        })
        return

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(cookies, f)
        cookies_path = f.name

    images = listing.get("images", [])
    image_paths = download_images(images)

    bot = None
    try:
        bot = MarketplaceBot(
            cookies_path=cookies_path,
            delay_factor=1.0,
            proxy=None
        )

        listing_data = {
            "title": listing.get("title"),
            "price": listing.get("price"),
            "description": listing.get("description"),
            "category": listing.get("category"),
            "product_tags": listing.get("product_tags", ""),
            "location": listing.get("location", ""),
            "image_paths": image_paths,
            "ai_enabled": False
        }

        result = bot.create_new_listing(listing_data)
        if result and result.get("success"):
            update_listing(listing_id, {
                "status": "active",
                "title": result.get("new_title", listing.get("title")),
                "description": result.get("new_description", listing.get("description"))
            })
        else:
            update_listing(listing_id, {
                "status": "failed",
                "error_message": (result.get("error") if result else "Unknown bot error")
            })
    except Exception as exc:
        update_listing(listing_id, {
            "status": "failed",
            "error_message": str(exc)
        })
    finally:
        if bot:
            bot.close()
        try:
            os.unlink(cookies_path)
        except Exception:
            pass


def main():
    if not ACCESS_TOKEN:
        print("ACCESS_TOKEN env var is required.")
        return

    print(f"Local runner started at {datetime.utcnow().isoformat()}Z")
    while True:
        try:
            listings = fetch_pending_listings()
            if listings:
                print(f"Found {len(listings)} pending listing(s)")
            for listing in listings:
                run_listing(listing)
        except Exception as exc:
            print(f"Runner error: {exc}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
