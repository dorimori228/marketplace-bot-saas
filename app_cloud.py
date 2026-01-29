"""
Cloud Flask Application for Facebook Marketplace Bot SaaS
Multi-tenant API with authentication, subscriptions, and feature gating.
"""

from flask import Flask, request, jsonify, g, send_from_directory
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import os
import json

# Import models and utilities
from models import db, User, FacebookAccount, Listing, ListingImage, Subscription, UsageLog, ListingTemplate, Analytics
from middleware.feature_gate import FeatureGate, get_usage_summary, validate_batch_size
from stripe_integration import StripeIntegration, StripeWebhookHandler
from config.subscription_tiers import get_all_tiers, format_tier_comparison

# Initialize Flask app
app = Flask(__name__)

# Configuration
def _get_database_url():
    """Pick the first non-empty database URL from common Railway env vars."""
    candidate_keys = [
        'DATABASE_URL',
        'DATABASE_PUBLIC_URL',
        'DATABASE_PRIVATE_URL',
        'POSTGRES_URL',
        'POSTGRESQL_URL',
        'DATABASE_URI',
        'SQLALCHEMY_DATABASE_URI'
    ]
    for key in candidate_keys:
        value = os.getenv(key)
        if value and value.strip():
            print(f"✅ Using database URL from {key}")
            return value.strip()
    print("⚠️ DATABASE_URL is empty; falling back to local postgres")
    return 'postgresql://localhost/marketplace_bot'

app.config['SQLALCHEMY_DATABASE_URI'] = _get_database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-this-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# ==================== ERROR HANDLING ====================

@app.errorhandler(Exception)
def handle_exception(error):
    """Return JSON for unhandled exceptions."""
    if isinstance(error, HTTPException):
        return jsonify({'error': error.description}), error.code
    print(f"⚠️ Unhandled exception: {error}")
    return jsonify({'error': 'Internal server error'}), 500


# CORS - Allow all origins (Chrome extensions don't send standard Origin headers)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Encryption for cookies
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
if ENCRYPTION_KEY:
    cipher = Fernet(ENCRYPTION_KEY.encode())
else:
    print("⚠️ WARNING: ENCRYPTION_KEY not set! Generating temporary key.")
    cipher = Fernet(Fernet.generate_key())


# ==================== JWT CALLBACKS ====================

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Load user from JWT token."""
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).first()


tables_initialized = False

def _ensure_tables():
    """Create tables on demand if missing."""
    global tables_initialized
    if tables_initialized:
        return
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if not inspector.has_table('users'):
            print("🛠️ Creating database tables...")
            db.create_all()
        tables_initialized = True
    except Exception as e:
        print(f"⚠️ Table initialization failed: {e}")


@app.before_request
def load_user():
    """Load current user into g if authenticated."""
    _ensure_tables()
    g.current_user = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            g.current_user = User.query.get(user_id)
    except Exception:
        g.current_user = None


# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for deployment platforms."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


# ==================== STATIC ASSETS ====================

@app.route('/static/logo/<path:filename>')
def serve_logo(filename):
    """Serve logo files for the extension UI."""
    logo_dir = os.path.join(os.getcwd(), 'logo')
    return send_from_directory(logo_dir, filename)


# ==================== AUTHENTICATION ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.json

        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400

        email = data['email'].lower().strip()
        password = data['password']

        # Check if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409

        # Create user
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            subscription_tier='free',
            subscription_status='active'
        )

        db.session.add(user)
        db.session.commit()

        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user."""
    data = request.json

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    email = data['email'].lower().strip()
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.session.commit()

    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    })


@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)

    return jsonify({'access_token': access_token})


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info."""
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id) if user_id is not None else None
    except (TypeError, ValueError):
        user_id = None
    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 401

    return jsonify({
        'user': user.to_dict(),
        'usage': get_usage_summary(user)
    })


# ==================== SUBSCRIPTION ====================

@app.route('/api/subscription/tiers', methods=['GET'])
def get_subscription_tiers():
    """Get all available subscription tiers."""
    return jsonify({
        'tiers': format_tier_comparison()
    })


@app.route('/api/subscription/create-checkout', methods=['POST'])
@jwt_required()
def create_checkout():
    """Create Stripe Checkout session for subscription."""
    user = g.current_user
    data = request.json

    tier = data.get('tier', 'basic')
    tiers = get_all_tiers()

    if tier not in tiers:
        return jsonify({'error': 'Invalid tier'}), 400

    try:
        # Create Stripe customer if doesn't exist
        if not user.stripe_customer_id:
            customer = StripeIntegration.create_customer(user.email, user.id)
            user.stripe_customer_id = customer.id
            db.session.commit()

        # Create checkout session
        price_id = tiers[tier]['stripe_price_id']
        success_url = data.get('success_url', f"{os.getenv('FRONTEND_URL')}/success")
        cancel_url = data.get('cancel_url', f"{os.getenv('FRONTEND_URL')}/pricing")

        session = StripeIntegration.create_checkout_session(
            user.stripe_customer_id,
            price_id,
            success_url,
            cancel_url,
            trial_days=7
        )

        return jsonify({
            'session_id': session.id,
            'url': session.url
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/subscription/portal', methods=['POST'])
@jwt_required()
@FeatureGate.check_subscription()
def create_portal():
    """Create Stripe Customer Portal session."""
    user = g.current_user

    if not user.stripe_customer_id:
        return jsonify({'error': 'No Stripe customer found'}), 404

    try:
        return_url = request.json.get('return_url', os.getenv('FRONTEND_URL'))
        session = StripeIntegration.create_portal_session(user.stripe_customer_id, return_url)

        return jsonify({
            'url': session.url
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/subscription/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks."""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    try:
        event = StripeWebhookHandler.handle_webhook(payload, sig_header, webhook_secret)
        result = StripeWebhookHandler.process_event(event, db)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== FACEBOOK ACCOUNTS ====================

@app.route('/api/accounts', methods=['GET'])
@jwt_required()
@FeatureGate.check_subscription()
def get_accounts():
    """Get user's Facebook accounts."""
    user = g.current_user

    accounts = FacebookAccount.query.filter_by(user_id=user.id).all()

    return jsonify({
        'accounts': [acc.to_dict() for acc in accounts]
    })


@app.route('/api/accounts/add', methods=['POST'])
@jwt_required()
@FeatureGate.check_subscription()
@FeatureGate.check_limit('facebook_accounts')
def add_account():
    """Add a new Facebook account."""
    user = g.current_user
    data = request.json

    if not data or not data.get('account_name') or not data.get('cookies'):
        return jsonify({'error': 'Account name and cookies required'}), 400

    account_name = data['account_name']
    cookies = data['cookies']

    # Check if account name already exists for this user
    existing = FacebookAccount.query.filter_by(
        user_id=user.id,
        account_name=account_name
    ).first()

    if existing:
        return jsonify({'error': 'Account name already exists'}), 409

    # Encrypt cookies
    cookies_encrypted = cipher.encrypt(json.dumps(cookies).encode()).decode()

    # Create account
    account = FacebookAccount(
        user_id=user.id,
        account_name=account_name,
        cookies_encrypted=cookies_encrypted,
        status='active',
        last_sync=datetime.utcnow()
    )

    db.session.add(account)
    db.session.commit()

    return jsonify({
        'message': 'Account added successfully',
        'account': account.to_dict()
    }), 201


@app.route('/api/accounts/<int:account_id>/sync-cookies', methods=['POST'])
@jwt_required()
@FeatureGate.check_subscription()
def sync_cookies(account_id):
    """Sync cookies for an account (auto-update from extension)."""
    user = g.current_user
    data = request.json

    if not data or not data.get('cookies'):
        return jsonify({'error': 'Cookies required'}), 400

    account = FacebookAccount.query.filter_by(
        id=account_id,
        user_id=user.id
    ).first()

    if not account:
        return jsonify({'error': 'Account not found'}), 404

    # Encrypt and update cookies
    cookies_encrypted = cipher.encrypt(json.dumps(data['cookies']).encode()).decode()
    account.cookies_encrypted = cookies_encrypted
    account.last_sync = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'message': 'Cookies synced successfully'
    })


@app.route('/api/accounts/<int:account_id>', methods=['DELETE'])
@jwt_required()
@FeatureGate.check_subscription()
def delete_account(account_id):
    """Delete a Facebook account."""
    user = g.current_user

    account = FacebookAccount.query.filter_by(
        id=account_id,
        user_id=user.id
    ).first()

    if not account:
        return jsonify({'error': 'Account not found'}), 404

    db.session.delete(account)
    db.session.commit()

    return jsonify({
        'message': 'Account deleted successfully'
    })


# ==================== LISTINGS ====================

@app.route('/api/listings', methods=['GET'])
@jwt_required()
@FeatureGate.check_subscription()
def get_listings():
    """Get user's listings."""
    user = g.current_user

    account_id = request.args.get('account_id', type=int)
    status = request.args.get('status', 'all')
    limit = request.args.get('limit', 100, type=int)

    query = Listing.query.filter_by(user_id=user.id)

    if account_id:
        query = query.filter_by(fb_account_id=account_id)

    if status != 'all':
        query = query.filter_by(status=status)

    listings = query.order_by(Listing.created_at.desc()).limit(limit).all()

    return jsonify({
        'listings': [listing.to_dict(include_images=True) for listing in listings],
        'count': len(listings)
    })


@app.route('/api/listings/create', methods=['POST'])
@jwt_required()
@FeatureGate.check_subscription()
@FeatureGate.check_limit('listings_per_month')
@FeatureGate.check_limit('active_listings')
def create_listing():
    """Create a new listing (queues bot job)."""
    user = g.current_user
    data = request.json

    # Validate required fields
    required = ['fb_account_id', 'title', 'price', 'description']
    if not all(data.get(field) for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate account belongs to user
    account = FacebookAccount.query.filter_by(
        id=data['fb_account_id'],
        user_id=user.id
    ).first()

    if not account:
        return jsonify({'error': 'Account not found'}), 404

    # Create listing
    listing = Listing(
        user_id=user.id,
        fb_account_id=data['fb_account_id'],
        title=data['title'],
        price=data['price'],
        description=data['description'],
        category=data.get('category'),
        product_tags=data.get('product_tags'),
        location=data.get('location'),
        status='pending'
    )

    db.session.add(listing)
    db.session.flush()

    # Add images
    for idx, image_url in enumerate(data.get('images', [])):
        image = ListingImage(
            listing_id=listing.id,
            image_url=image_url,
            image_order=idx
        )
        db.session.add(image)

    # Log usage
    usage_log = UsageLog(
        user_id=user.id,
        action_type='listing_created',
        listing_id=listing.id
    )
    db.session.add(usage_log)

    db.session.commit()

    # TODO: Queue Celery task for bot processing
    # from tasks.listing_tasks import create_listing_task
    # task = create_listing_task.delay(listing.id)

    return jsonify({
        'message': 'Listing created and queued',
        'listing': listing.to_dict(include_images=True)
    }), 201


@app.route('/api/listings/batch', methods=['POST'])
@jwt_required()
@FeatureGate.check_subscription()
@FeatureGate.require_feature('batch_operations')
def batch_create_listings():
    """Batch create multiple listings (Pro+ feature)."""
    user = g.current_user
    data = request.json

    listings = data.get('listings', [])

    if not listings:
        return jsonify({'error': 'No listings provided'}), 400

    # Validate batch size
    is_valid, error_msg = validate_batch_size(user, len(listings))
    if not is_valid:
        return jsonify({'error': error_msg}), 403

    # TODO: Implement batch creation with Celery tasks

    return jsonify({
        'message': f'{len(listings)} listings queued for creation'
    }), 202


@app.route('/api/listings/<int:listing_id>', methods=['DELETE'])
@jwt_required()
@FeatureGate.check_subscription()
def delete_listing(listing_id):
    """Delete a listing."""
    user = g.current_user

    listing = Listing.query.filter_by(
        id=listing_id,
        user_id=user.id
    ).first()

    if not listing:
        return jsonify({'error': 'Listing not found'}), 404

    listing.status = 'deleted'
    listing.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'message': 'Listing deleted successfully'
    })


# ==================== TEMPLATES (Pro+) ====================

@app.route('/api/templates', methods=['GET'])
@jwt_required()
@FeatureGate.check_subscription()
@FeatureGate.require_feature('templates')
def get_templates():
    """Get user's listing templates."""
    user = g.current_user

    templates = ListingTemplate.query.filter_by(user_id=user.id).all()

    return jsonify({
        'templates': [t.to_dict() for t in templates]
    })


@app.route('/api/templates', methods=['POST'])
@jwt_required()
@FeatureGate.check_subscription()
@FeatureGate.require_feature('templates')
def create_template():
    """Create a new listing template."""
    user = g.current_user
    data = request.json

    if not data or not data.get('name'):
        return jsonify({'error': 'Template name required'}), 400

    template = ListingTemplate(
        user_id=user.id,
        name=data['name'],
        description=data.get('description'),
        category=data.get('category'),
        price_template=data.get('price_template'),
        description_template=data.get('description_template'),
        location=data.get('location'),
        product_tags=data.get('product_tags')
    )

    db.session.add(template)
    db.session.commit()

    return jsonify({
        'message': 'Template created successfully',
        'template': template.to_dict()
    }), 201


# ==================== ANALYTICS ====================

@app.route('/api/analytics/dashboard', methods=['GET'])
@jwt_required()
@FeatureGate.check_subscription()
def analytics_dashboard():
    """Get analytics dashboard data."""
    user = g.current_user

    # Get usage summary
    usage = get_usage_summary(user)

    # Get recent activity
    recent_listings = Listing.query.filter_by(user_id=user.id)\
        .order_by(Listing.created_at.desc())\
        .limit(10).all()

    return jsonify({
        'usage': usage,
        'recent_listings': [l.to_dict() for l in recent_listings]
    })


# ==================== CREATE TABLES ====================

# Create tables on startup (works with gunicorn)
with app.app_context():
    db.create_all()
    print("✅ Database tables created")


# ==================== RUN APP ====================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
