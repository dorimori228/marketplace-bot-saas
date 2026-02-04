import os
import json
import time
import threading
import tempfile
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, request, jsonify, send_from_directory

from bot import MarketplaceBot

API_URL = os.getenv("API_URL", "https://marketplace-bot-saas-production.up.railway.app/api")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))

APP_DIR = Path.home() / ".pandabay"
APP_DIR.mkdir(parents=True, exist_ok=True)
STATE_PATH = APP_DIR / "runner_state.json"

app = Flask(__name__)

runner_thread = None
runner_stop = threading.Event()
log_buffer = []


def log(message):
    timestamp = datetime.utcnow().strftime("%H:%M:%S")
    line = f"[{timestamp}] {message}"
    log_buffer.append(line)
    if len(log_buffer) > 200:
        log_buffer.pop(0)
    print(line)


def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            return {}
    return {}


def save_state(data):
    STATE_PATH.write_text(json.dumps(data, indent=2))


def get_token():
    return load_state().get("access_token", "")


def auth_headers():
    token = get_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def fetch_pending_listings():
    response = requests.get(
        f"{API_URL}/listings?status=pending&limit=20",
        headers=auth_headers(),
        timeout=30
    )
    response.raise_for_status()
    return response.json().get("listings", [])


def fetch_account_cookies(account_id):
    response = requests.get(
        f"{API_URL}/accounts/{account_id}/cookies",
        headers=auth_headers(),
        timeout=30
    )
    response.raise_for_status()
    return response.json().get("cookies", [])


def update_listing(listing_id, payload):
    response = requests.put(
        f"{API_URL}/listings/{listing_id}/status",
        headers=auth_headers(),
        data=json.dumps(payload),
        timeout=30
    )
    response.raise_for_status()


def download_images(images):
    temp_dir = Path(tempfile.mkdtemp(prefix="listing_images_"))
    file_paths = []
    for idx, image in enumerate(images):
        url = image.get("image_url")
        if not url:
            continue
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        file_path = temp_dir / f"image_{idx}.jpg"
        file_path.write_bytes(resp.content)
        file_paths.append(str(file_path))
    return file_paths


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
            log(f"Listing {listing_id} created successfully.")
        else:
            update_listing(listing_id, {
                "status": "failed",
                "error_message": (result.get("error") if result else "Unknown bot error")
            })
            log(f"Listing {listing_id} failed: {result.get('error') if result else 'Unknown'}")
    except Exception as exc:
        update_listing(listing_id, {
            "status": "failed",
            "error_message": str(exc)
        })
        log(f"Listing {listing_id} crashed: {exc}")
    finally:
        if bot:
            bot.close()
        try:
            os.unlink(cookies_path)
        except Exception:
            pass


def runner_loop():
    log("Runner started.")
    while not runner_stop.is_set():
        try:
            listings = fetch_pending_listings()
            if listings:
                log(f"Found {len(listings)} pending listing(s).")
            for listing in listings:
                run_listing(listing)
        except Exception as exc:
            log(f"Runner error: {exc}")
        time.sleep(POLL_INTERVAL)
    log("Runner stopped.")


@app.route("/")
def index():
    return send_from_directory(".", "runner_ui.html")


@app.route("/api/status")
def status():
    state = load_state()
    return jsonify({
        "running": runner_thread is not None and runner_thread.is_alive(),
        "logged_in": bool(state.get("access_token")),
        "email": state.get("email", "")
    })


@app.route("/api/logs")
def logs():
    return jsonify({"logs": log_buffer[-200:]})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email", "")
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    response = requests.post(
        f"{API_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=30
    )
    payload = response.json()
    if not response.ok:
        return jsonify({"error": payload.get("error", "Login failed")}), 401

    save_state({
        "email": email,
        "access_token": payload.get("access_token")
    })
    return jsonify({"message": "Logged in"})


@app.route("/api/start", methods=["POST"])
def start():
    global runner_thread
    if runner_thread and runner_thread.is_alive():
        return jsonify({"message": "Runner already running"})
    runner_stop.clear()
    runner_thread = threading.Thread(target=runner_loop, daemon=True)
    runner_thread.start()
    return jsonify({"message": "Runner started"})


@app.route("/api/stop", methods=["POST"])
def stop():
    runner_stop.set()
    return jsonify({"message": "Runner stopping"})


if __name__ == "__main__":
    import webbrowser
    webbrowser.open("http://127.0.0.1:5055")
    app.run(host="127.0.0.1", port=5055)
