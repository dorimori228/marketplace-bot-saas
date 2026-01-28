# Procfile for Heroku/Render deployment
# Defines which processes to run

# Web server - main Flask application
web: gunicorn app_cloud:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120

# Celery worker - background job processing
worker: celery -A tasks.listing_tasks worker --loglevel=info --concurrency=2

# Optional: Celery beat for periodic tasks
# beat: celery -A tasks.listing_tasks beat --loglevel=info
