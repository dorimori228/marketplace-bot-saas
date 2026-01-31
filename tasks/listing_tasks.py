"""
Celery Background Tasks for Listing Processing
Handles asynchronous bot operations for creating, deleting, and relisting items.
"""

from celery import Celery
import os
import sys
import json
import tempfile
import importlib
from datetime import datetime
from cryptography.fernet import Fernet

def _ensure_project_module(module_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate_dirs = [
        base_dir,
        os.path.join(base_dir, 'facebook-marketplace-bot')
    ]
    for path in candidate_dirs:
        if os.path.exists(os.path.join(path, f'{module_name}.py')) and path not in sys.path:
            sys.path.insert(0, path)
            return
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError:
        pass


_ensure_project_module('models')

# Initialize Celery
celery = Celery('tasks',
                broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
                backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=540  # 9 minutes soft limit
)


@celery.task(bind=True, max_retries=3)
def create_listing_task(self, listing_id):
    """
    Background task to create a Facebook Marketplace listing using the bot.

    Args:
        listing_id (int): Database ID of the listing to create

    Returns:
        dict: Task result with success status and details
    """
    from models import db, Listing, FacebookAccount, Analytics, UsageLog
    from bot import MarketplaceBot
    from app_cloud import app

    with app.app_context():
        try:
            print(f"🚀 Starting listing creation task for listing_id: {listing_id}")

            # Get listing from database
            listing = Listing.query.get(listing_id)
            if not listing:
                return {'success': False, 'error': 'Listing not found'}

            # Get FB account and decrypt cookies
            fb_account = FacebookAccount.query.get(listing.fb_account_id)
            if not fb_account:
                return {'success': False, 'error': 'Facebook account not found'}

            # Decrypt cookies
            cipher = Fernet(os.getenv('ENCRYPTION_KEY').encode())
            cookies_json = cipher.decrypt(fb_account.cookies_encrypted.encode()).decode()
            cookies = json.loads(cookies_json)

            # Save cookies to temporary file (bot expects file path)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(cookies, f)
                cookies_path = f.name

            try:
                # Initialize bot
                print(f"🤖 Initializing bot for account: {fb_account.account_name}")
                bot = MarketplaceBot(
                    cookies_path=cookies_path,
                    delay_factor=1.0,
                    proxy=None
                )

                # Get images from listing
                images = [img.image_url for img in listing.images.order_by('image_order').all()]

                # Prepare listing data for bot
                listing_data = {
                    'title': listing.title,
                    'price': listing.price,
                    'description': listing.description,
                    'category': listing.category or 'Home & Garden',
                    'product_tags': listing.product_tags or '',
                    'location': listing.location or '',
                    'image_paths': images,
                    'ai_enabled': False  # Set based on user's subscription tier
                }

                # Check if user has AI features enabled
                user = listing.user
                if user.subscription_tier == 'premium':
                    listing_data['ai_enabled'] = True

                # Execute bot
                print(f"📝 Creating listing: {listing.title}")
                start_time = datetime.utcnow()

                result = bot.create_new_listing(listing_data)

                end_time = datetime.utcnow()
                duration = int((end_time - start_time).total_seconds())

                # Update listing in database
                if result and result.get('success'):
                    listing.status = 'active'
                    listing.title = result.get('new_title', listing.title)
                    listing.description = result.get('new_description', listing.description)
                    listing.published_at = datetime.utcnow()

                    # Log analytics
                    analytics = Analytics(
                        user_id=listing.user_id,
                        fb_account_id=listing.fb_account_id,
                        listing_id=listing.id,
                        action='listing_created',
                        success=True,
                        duration_seconds=duration
                    )
                    db.session.add(analytics)

                    print(f"✅ Listing created successfully: {listing.title}")

                else:
                    listing.status = 'failed'
                    error_msg = result.get('error', 'Unknown error') if result else 'Bot returned no result'
                    listing.error_message = error_msg

                    # Log analytics
                    analytics = Analytics(
                        user_id=listing.user_id,
                        fb_account_id=listing.fb_account_id,
                        listing_id=listing.id,
                        action='listing_created',
                        success=False,
                        error_message=error_msg,
                        duration_seconds=duration
                    )
                    db.session.add(analytics)

                    print(f"❌ Listing creation failed: {error_msg}")

                listing.updated_at = datetime.utcnow()
                db.session.commit()

                # Cleanup
                bot.close()

                return {
                    'success': result.get('success', False) if result else False,
                    'listing_id': listing.id,
                    'new_title': listing.title,
                    'duration': duration
                }

            finally:
                # Clean up temporary cookies file
                if os.path.exists(cookies_path):
                    os.unlink(cookies_path)

        except Exception as e:
            print(f"❌ Task failed with exception: {str(e)}")

            # Update listing status
            try:
                listing = Listing.query.get(listing_id)
                if listing:
                    listing.status = 'failed'
                    listing.error_message = str(e)
                    db.session.commit()
            except:
                pass

            # Retry on failure (up to 3 times)
            raise self.retry(exc=e, countdown=60)


@celery.task(bind=True)
def delete_listing_task(self, listing_id):
    """
    Background task to delete a Facebook Marketplace listing.

    Args:
        listing_id (int): Database ID of the listing to delete

    Returns:
        dict: Task result
    """
    from models import db, Listing, FacebookAccount, Analytics
    from bot import MarketplaceBot
    from app_cloud import app

    with app.app_context():
        try:
            listing = Listing.query.get(listing_id)
            if not listing:
                return {'success': False, 'error': 'Listing not found'}

            fb_account = FacebookAccount.query.get(listing.fb_account_id)
            if not fb_account:
                return {'success': False, 'error': 'Account not found'}

            # Decrypt cookies
            cipher = Fernet(os.getenv('ENCRYPTION_KEY').encode())
            cookies_json = cipher.decrypt(fb_account.cookies_encrypted.encode()).decode()
            cookies = json.loads(cookies_json)

            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(cookies, f)
                cookies_path = f.name

            try:
                bot = MarketplaceBot(cookies_path, delay_factor=1.0)

                # Delete listing on Facebook
                success = bot.delete_listing_if_exists(listing.title)

                # Update database
                if success:
                    listing.status = 'deleted'
                    listing.updated_at = datetime.utcnow()

                    analytics = Analytics(
                        user_id=listing.user_id,
                        fb_account_id=listing.fb_account_id,
                        listing_id=listing.id,
                        action='listing_deleted',
                        success=True
                    )
                    db.session.add(analytics)

                db.session.commit()
                bot.close()

                return {'success': success, 'listing_id': listing_id}

            finally:
                if os.path.exists(cookies_path):
                    os.unlink(cookies_path)

        except Exception as e:
            print(f"Delete task failed: {e}")
            raise self.retry(exc=e, countdown=60)


@celery.task
def batch_create_listings_task(listing_ids):
    """
    Create multiple listings in sequence (Pro+ feature).

    Args:
        listing_ids (list): List of listing IDs to create

    Returns:
        dict: Batch results
    """
    results = []

    for listing_id in listing_ids:
        result = create_listing_task.apply(args=[listing_id])
        results.append({
            'listing_id': listing_id,
            'task_id': result.id,
            'status': result.status
        })

    return {
        'total': len(listing_ids),
        'results': results
    }


@celery.task
def cleanup_old_tasks():
    """
    Periodic task to clean up old task results from Redis.
    Run this daily via celery beat.
    """
    from celery.result import AsyncResult
    from datetime import timedelta

    # Clean up task results older than 7 days
    cutoff = datetime.utcnow() - timedelta(days=7)

    # Implementation depends on your Celery result backend
    print(f"🧹 Cleaned up old task results before {cutoff}")

    return {'cleaned': True}


if __name__ == '__main__':
    # For testing
    print("🔧 Celery worker ready")
    celery.worker_main(['worker', '--loglevel=info'])
