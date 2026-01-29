import argparse
import json
import pickle
import sqlite3
from datetime import datetime
from pathlib import Path

from app_cloud import app, db, User, FacebookAccount, Listing, cipher


def parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(value, fmt)
        except (TypeError, ValueError):
            continue
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def ensure_jsonable(value):
    try:
        json.dumps(value)
        return value
    except TypeError:
        if isinstance(value, (list, tuple)):
            return [ensure_jsonable(v) for v in value]
        if hasattr(value, "__dict__"):
            return {k: ensure_jsonable(v) for k, v in value.__dict__.items()}
        return str(value)


def load_cookies(account_dir):
    json_path = account_dir / "cookies.json"
    pkl_path = account_dir / "cookies.pkl"

    if json_path.exists():
        try:
            with json_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    if pkl_path.exists():
        try:
            with pkl_path.open("rb") as f:
                data = pickle.load(f)
            return ensure_jsonable(data)
        except Exception:
            return []

    return []


def import_listings_for_account(account, db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT title, price, description, category, product_tags, location,
               image_paths, created_at, updated_at, status, facebook_listing_id, notes
        FROM listings
        """
    )

    created = 0
    for row in cur.fetchall():
        title, price, description, category, product_tags, location, image_paths, created_at, updated_at, status, fb_id, notes = row

        existing = Listing.query.filter_by(
            user_id=account.user_id,
            fb_account_id=account.id,
            title=title,
            price=price
        ).first()
        if existing:
            continue

        listing = Listing(
            user_id=account.user_id,
            fb_account_id=account.id,
            title=title or "",
            price=price or "",
            description=description or "",
            category=category,
            product_tags=product_tags,
            location=location,
            status=status or "active",
            facebook_listing_id=fb_id,
            notes=notes,
            created_at=parse_datetime(created_at) or datetime.utcnow(),
            updated_at=parse_datetime(updated_at),
        )
        db.session.add(listing)
        created += 1

        if created % 200 == 0:
            db.session.commit()

    db.session.commit()
    conn.close()
    return created


def main():
    parser = argparse.ArgumentParser(description="Import local account data into cloud database.")
    parser.add_argument("--email", required=True, help="Target user email in cloud DB")
    parser.add_argument("--accounts-dir", default="accounts", help="Path to local accounts folder")
    args = parser.parse_args()

    accounts_dir = Path(args.accounts_dir)
    if not accounts_dir.exists():
        raise SystemExit(f"Accounts directory not found: {accounts_dir}")

    with app.app_context():
        user = User.query.filter_by(email=args.email.lower().strip()).first()
        if not user:
            raise SystemExit(f"User not found: {args.email}")

        total_accounts = 0
        total_listings = 0

        for account_dir in accounts_dir.iterdir():
            if not account_dir.is_dir():
                continue

            db_path = account_dir / "listings.db"
            if not db_path.exists():
                continue

            account_name = account_dir.name
            account = FacebookAccount.query.filter_by(
                user_id=user.id,
                account_name=account_name
            ).first()

            if not account:
                cookies = load_cookies(account_dir)
                cookies_encrypted = cipher.encrypt(json.dumps(cookies).encode()).decode()
                account = FacebookAccount(
                    user_id=user.id,
                    account_name=account_name,
                    cookies_encrypted=cookies_encrypted,
                    status="active",
                    last_sync=datetime.utcnow()
                )
                db.session.add(account)
                db.session.commit()
                total_accounts += 1

            total_listings += import_listings_for_account(account, db_path)

        print(f"Imported {total_accounts} accounts and {total_listings} listings.")


if __name__ == "__main__":
    main()
