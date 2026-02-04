import os
import json
import time
import threading
import tempfile
from datetime import datetime, timezone
from pathlib import Path
import sys

import requests
from flask import Flask, request, jsonify, send_from_directory

from bot import MarketplaceBot

API_URL = os.getenv("API_URL", "https://marketplace-bot-saas-production.up.railway.app/api")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://marketplace-bot-saas-production.up.railway.app")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))

APP_DIR = Path.home() / ".pandabay"
APP_DIR.mkdir(parents=True, exist_ok=True)
STATE_PATH = APP_DIR / "runner_state.json"

app = Flask(__name__)

runner_thread = None
runner_stop = threading.Event()
log_buffer = []
last_empty_log = 0


def log(message):
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
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
    global last_empty_log
    log("Runner started.")
    while not runner_stop.is_set():
        try:
            listings = fetch_pending_listings()
            if listings:
                log(f"Found {len(listings)} pending listing(s).")
            for listing in listings:
                run_listing(listing)
            if not listings:
                now = time.time()
                if now - last_empty_log > 60:
                    log("No pending listings. Waiting...")
                    last_empty_log = now
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
    start_runner()
    return jsonify({"message": "Logged in"})


def login_with_credentials(email, password):
    response = requests.post(
        f"{API_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=30
    )
    payload = response.json()
    if not response.ok:
        raise Exception(payload.get("error", "Login failed"))
    save_state({
        "email": email,
        "access_token": payload.get("access_token")
    })


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


def start_runner():
    global runner_thread
    if runner_thread and runner_thread.is_alive():
        return
    runner_stop.clear()
    runner_thread = threading.Thread(target=runner_loop, daemon=True)
    runner_thread.start()


def stop_runner():
    runner_stop.set()


def launch_gui():
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title("PandaBay Runner")
    root.geometry("720x520")
    root.configure(bg="#F0F0DB")

    def refresh_logs():
        logs_text.delete("1.0", tk.END)
        logs_text.insert(tk.END, "\n".join(log_buffer[-200:]))
        root.after(2000, refresh_logs)

    def refresh_status():
        running = runner_thread is not None and runner_thread.is_alive()
        status_var.set("Running" if running else "Stopped")
        root.after(3000, refresh_status)

    def on_login():
        try:
            login_with_credentials(email_var.get().strip(), password_var.get().strip())
            messagebox.showinfo("Login", "Logged in successfully")
            start_runner()
            open_admin()
        except Exception as exc:
            messagebox.showerror("Login Failed", str(exc))

    def on_start():
        start_runner()
        refresh_status()

    def on_stop():
        stop_runner()
        refresh_status()

    def open_admin():
        import webbrowser
        webbrowser.open(f"{FRONTEND_URL}/dashboard")

    header = tk.Frame(root, bg="#30364F", padx=16, pady=16)
    header.pack(fill="x")
    tk.Label(header, text="PandaBay Runner", fg="white", bg="#30364F",
             font=("Segoe UI", 16, "bold")).pack(anchor="w")
    tk.Label(header, text="Run listings locally with visible Chrome", fg="#E1D9BC",
             bg="#30364F").pack(anchor="w")

    content = tk.Frame(root, bg="#F0F0DB", padx=16, pady=16)
    content.pack(fill="both", expand=True)

    form = tk.Frame(content, bg="#fafaf8", padx=16, pady=16, highlightbackground="#ACBAC4", highlightthickness=1)
    form.pack(fill="x")

    email_var = tk.StringVar()
    password_var = tk.StringVar()
    status_var = tk.StringVar(value="Stopped")

    tk.Label(form, text="Email", bg="#fafaf8").grid(row=0, column=0, sticky="w")
    tk.Entry(form, textvariable=email_var, width=40).grid(row=1, column=0, sticky="w")
    tk.Label(form, text="Password", bg="#fafaf8").grid(row=2, column=0, sticky="w", pady=(10, 0))
    tk.Entry(form, textvariable=password_var, show="*", width=40).grid(row=3, column=0, sticky="w")
    tk.Button(form, text="Sign In", command=on_login, bg="#30364F", fg="white").grid(row=1, column=1, padx=12)

    controls = tk.Frame(content, bg="#F0F0DB", pady=12)
    controls.pack(fill="x")
    tk.Label(controls, text="Status:", bg="#F0F0DB").pack(side="left")
    tk.Label(controls, textvariable=status_var, bg="#F0F0DB", fg="#30364F", font=("Segoe UI", 10, "bold")).pack(side="left", padx=6)
    tk.Button(controls, text="Start", command=on_start, bg="#30364F", fg="white").pack(side="right", padx=6)
    tk.Button(controls, text="Stop", command=on_stop).pack(side="right", padx=6)
    tk.Button(controls, text="Open Admin Panel", command=open_admin).pack(side="right", padx=6)

    logs_frame = tk.Frame(content, bg="#fafaf8", padx=10, pady=10, highlightbackground="#ACBAC4", highlightthickness=1)
    logs_frame.pack(fill="both", expand=True)
    logs_text = tk.Text(logs_frame, height=12, bg="#111827", fg="#e2e8f0")
    logs_text.pack(fill="both", expand=True)

    refresh_logs()
    refresh_status()
    root.mainloop()


if __name__ == "__main__":
    if "--gui" in sys.argv:
        launch_gui()
    else:
        import webbrowser
        webbrowser.open("http://127.0.0.1:5055")
        app.run(host="127.0.0.1", port=5055)
