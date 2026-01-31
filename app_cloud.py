"""
Cloud Flask Application for Facebook Marketplace Bot SaaS
Multi-tenant API with authentication, subscriptions, and feature gating.
"""

from flask import Flask, request, jsonify, g, send_from_directory, render_template, redirect, url_for
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from cryptography.fernet import Fernet
import os
import json

# Import models and utilities
from models import db, User, FacebookAccount, Listing, ListingImage, Subscription, UsageLog, ListingTemplate, Analytics
from middleware.feature_gate import FeatureGate, get_usage_summary, validate_batch_size
from stripe_integration import StripeIntegration, StripeWebhookHandler
from config.subscription_tiers import get_all_tiers, format_tier_comparison

# Initialize Flask app with template and static folders
app = Flask(__name__,
            template_folder='templates',
            static_folder='static',
            static_url_path='/assets')

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
            return _ensure_sslmode(value.strip())
    print("⚠️ DATABASE_URL is empty; falling back to local postgres")
    return _ensure_sslmode('postgresql://localhost/marketplace_bot')


def _ensure_sslmode(db_url):
    """Ensure SSL mode is required for Postgres connections."""
    try:
        parsed = urlparse(db_url)
        if not parsed.scheme.startswith('postgres'):
            return db_url
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        if 'sslmode' not in query:
            query['sslmode'] = 'require'
            parsed = parsed._replace(query=urlencode(query))
        return urlunparse(parsed)
    except Exception:
        # If parsing fails, fall back to original URL
        return db_url

app.config['SQLALCHEMY_DATABASE_URI'] = _get_database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 60,
    'pool_size': 5,
    'max_overflow': 10,
    'pool_timeout': 30,
    'connect_args': {
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    }
}
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-this-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Always clear DB sessions between requests to avoid stale transactions.
@app.teardown_appcontext
def shutdown_session(exception=None):
    if exception is not None:
        try:
            db.session.rollback()
        except Exception:
            pass
    db.session.remove()

# ==================== ERROR HANDLING ====================

@app.errorhandler(Exception)
def handle_exception(error):
    """Return JSON for unhandled exceptions."""
    try:
        db.session.rollback()
    except Exception:
        pass
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
    """Create tables on demand if missing, and add missing columns."""
    global tables_initialized
    if tables_initialized:
        return

    from sqlalchemy import inspect, text
    from sqlalchemy.exc import OperationalError

    for attempt in range(2):
        try:
            # Clear any invalid transaction before inspecting/creating tables.
            try:
                db.session.rollback()
            except Exception:
                pass

            inspector = inspect(db.engine)
            if not inspector.has_table('users'):
                print("🛠️ Creating database tables...")
                db.create_all()
            else:
                # Ensure new columns exist for legacy databases
                columns = [col['name'] for col in inspector.get_columns('users')]
                if 'is_admin' not in columns:
                    print("🛠️ Adding users.is_admin column...")
                    db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE"))
                    db.session.commit()
            tables_initialized = True
            return
        except OperationalError as e:
            # Transient DB connection issue; reset state and retry once.
            try:
                db.session.rollback()
            except Exception:
                pass
            try:
                db.engine.dispose()
            except Exception:
                pass
            if attempt == 0:
                print(f"⚠️ DB connection hiccup during table init: {e}")
                continue
            print(f"⚠️ Table initialization failed: {e}")
            tables_initialized = False
            return
        except Exception as e:
            try:
                db.session.rollback()
            except Exception:
                pass
            print(f"⚠️ Table initialization failed: {e}")
            return


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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_dir = os.path.join(base_dir, 'logo')
    return send_from_directory(logo_dir, filename)


# ==================== WEB PAGES ====================

@app.route('/')
def landing_page():
    """Serve the landing page."""
    return send_from_directory('landing-page', 'index.html')


@app.route('/landing-page/<path:filename>')
def serve_landing_assets(filename):
    """Serve landing page static assets (CSS, JS, images)."""
    return send_from_directory('landing-page', filename)


@app.route('/login')
def login_page():
    """Serve the login page."""
    return render_template('login.html')


@app.route('/register')
def register_page():
    """Serve the registration page."""
    return render_template('register.html')


@app.route('/dashboard')
def dashboard_page():
    """Serve the main dashboard/admin panel."""
    return render_template('dashboard.html')


@app.route('/pricing')
def pricing_page():
    """Serve the pricing page with Stripe checkout links."""
    return render_template('pricing.html')


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


# Admin emails with full access
ADMIN_EMAILS = ['adam.maznev@gmail.com']


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

    # Auto-upgrade admin accounts to premium
    if email in ADMIN_EMAILS:
        user.subscription_tier = 'premium'
        user.subscription_status = 'active'
        user.is_admin = True

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

    try:
        user_payload = user.to_dict()
        usage_payload = get_usage_summary(user)
    except Exception as e:
        print(f"⚠️ Failed to serialize user: {e}")
        return jsonify({'error': 'User lookup failed'}), 500

    return jsonify({
        'user': user_payload,
        'usage': usage_payload
    })


@app.route('/api/admin/reset-db', methods=['POST'])
@jwt_required()
def reset_database():
    """Fully reset the database (admin + token required)."""
    user = g.current_user
    token = request.headers.get('X-Reset-Token', '')
    required_token = os.getenv('RESET_DB_TOKEN', '').strip()

    if not user or not getattr(user, 'is_admin', False):
        return jsonify({'error': 'Admin access required'}), 403

    if not required_token or token != required_token:
        return jsonify({'error': 'Valid reset token required'}), 403

    try:
        db.session.remove()
        db.drop_all()
        db.create_all()
        return jsonify({'message': 'Database reset completed'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database reset failed: {str(e)}'}), 500


@app.route('/api/user/password', methods=['PUT'])
@jwt_required()
def update_password():
    """Update the current user's password."""
    user = g.current_user
    data = request.json or {}

    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password required'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400

    if not check_password_hash(user.password_hash, current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401

    user.password_hash = generate_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Password updated successfully'})


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
        status=data.get('status', 'pending')
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


@app.route('/api/listings/batch-delete', methods=['POST'])
@jwt_required()
@FeatureGate.check_subscription()
def batch_delete_listings():
    """Delete multiple listings."""
    user = g.current_user
    data = request.json or {}
    listing_ids = data.get('listing_ids', [])

    if not listing_ids:
        return jsonify({'error': 'No listings provided'}), 400

    listings = Listing.query.filter(
        Listing.user_id == user.id,
        Listing.id.in_(listing_ids)
    ).all()

    for listing in listings:
        listing.status = 'deleted'
        listing.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({'message': f'Deleted {len(listings)} listings'})


@app.route('/api/listings/relist', methods=['POST'])
@jwt_required()
@FeatureGate.check_subscription()
def relist_listings():
    """Mark listings for relisting."""
    user = g.current_user
    data = request.json or {}
    listing_ids = data.get('listing_ids', [])

    if not listing_ids:
        return jsonify({'error': 'No listings provided'}), 400

    listings = Listing.query.filter(
        Listing.user_id == user.id,
        Listing.id.in_(listing_ids)
    ).all()

    for listing in listings:
        listing.status = 'pending'
        listing.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({'message': f'{len(listings)} listings queued for relist'})


@app.route('/api/listings/run', methods=['POST'])
@jwt_required()
@FeatureGate.check_subscription()
def run_listings():
    """Queue selected listings to run the bot."""
    user = g.current_user
    data = request.json or {}
    listing_ids = data.get('listing_ids', [])

    if not listing_ids:
        return jsonify({'error': 'No listings provided'}), 400

    listings = Listing.query.filter(
        Listing.user_id == user.id,
        Listing.id.in_(listing_ids)
    ).all()

    for listing in listings:
        listing.status = 'pending'
        listing.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({'message': f'Queued {len(listings)} listing(s) to run'})


@app.route('/api/listings/randomize-locations', methods=['POST'])
@jwt_required()
@FeatureGate.check_subscription()
def randomize_listing_locations():
    """Randomize listing locations."""
    user = g.current_user
    data = request.json or {}
    listing_ids = data.get('listing_ids', [])

    if not listing_ids:
        return jsonify({'error': 'No listings provided'}), 400

    uk_locations = [
        'London, England', 'Manchester, England', 'Birmingham, England', 'Liverpool, England',
        'Leeds, England', 'Sheffield, England', 'Newcastle, England', 'Nottingham, England',
        'Bristol, England', 'Cardiff, Wales', 'Glasgow, Scotland', 'Edinburgh, Scotland',
        'Belfast, Northern Ireland', 'Leicester, England', 'Southampton, England', 'Portsmouth, England',
        'Brighton, England', 'Norwich, England', 'York, England', 'Coventry, England'
    ]

    import random
    listings = Listing.query.filter(
        Listing.user_id == user.id,
        Listing.id.in_(listing_ids)
    ).all()

    for listing in listings:
        listing.location = random.choice(uk_locations)
        listing.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({'message': f'Randomized {len(listings)} locations'})


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


@app.route('/api/templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
@FeatureGate.check_subscription()
@FeatureGate.require_feature('templates')
def delete_template(template_id):
    """Delete a listing template."""
    user = g.current_user
    template = ListingTemplate.query.filter_by(id=template_id, user_id=user.id).first()

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    db.session.delete(template)
    db.session.commit()

    return jsonify({'message': 'Template deleted'})


# ==================== ANALYTICS ====================

@app.route('/api/analytics/dashboard', methods=['GET'])
@jwt_required()
@FeatureGate.check_subscription()
def analytics_dashboard():
    """Get analytics dashboard data."""
    from sqlalchemy import func
    user = g.current_user

    # Get usage summary
    usage = get_usage_summary(user)

    # Get recent activity
    recent_listings = Listing.query.filter_by(user_id=user.id)\
        .order_by(Listing.created_at.desc())\
        .limit(10).all()

    # Get stats by action type
    stats = {}
    usage_logs = UsageLog.query.filter_by(user_id=user.id).all()
    for log in usage_logs:
        action = log.action_type
        if action not in stats:
            stats[action] = {'total': 0, 'successful': 0, 'failed': 0}
        stats[action]['total'] += 1
        # Extract status from action_data if available
        status = None
        if log.action_data and isinstance(log.action_data, dict):
            status = log.action_data.get('status')
        if status == 'success':
            stats[action]['successful'] += 1
        elif status == 'error' or status == 'failed':
            stats[action]['failed'] += 1
        else:
            # Assume successful if no status specified
            stats[action]['successful'] += 1

    # Get daily activity for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_activity = []

    daily_logs = db.session.query(
        func.date(UsageLog.timestamp).label('date'),
        func.count(UsageLog.id).label('count')
    ).filter(
        UsageLog.user_id == user.id,
        UsageLog.timestamp >= thirty_days_ago
    ).group_by(func.date(UsageLog.timestamp)).order_by(func.date(UsageLog.timestamp)).all()

    for row in daily_logs:
        daily_activity.append({
            'date': str(row.date) if row.date else '',
            'count': row.count
        })

    # Get account performance
    account_performance = []
    accounts = FacebookAccount.query.filter_by(user_id=user.id).all()
    for account in accounts:
        account_listings = Listing.query.filter_by(user_id=user.id, fb_account_id=account.id).all()
        total = len(account_listings)
        successful = len([l for l in account_listings if l.status == 'active'])
        failed = len([l for l in account_listings if l.status == 'failed'])
        deletions = len([l for l in account_listings if l.status == 'deleted'])
        success_rate = round((successful / total) * 100) if total > 0 else 0

        account_performance.append({
            'account_name': account.account_name,
            'total_listings': total,
            'successful_listings': successful,
            'failed_listings': failed,
            'total_deletions': deletions,
            'success_rate': success_rate
        })

    return jsonify({
        'usage': usage,
        'recent_listings': [l.to_dict() for l in recent_listings],
        'stats': stats,
        'daily_activity': daily_activity,
        'account_performance': account_performance
    })


@app.route('/api/activity', methods=['GET'])
@jwt_required()
@FeatureGate.check_subscription()
def get_activity_log():
    """Get user's activity log."""
    user = g.current_user
    account_id = request.args.get('account_id', type=int)
    limit = request.args.get('limit', 100, type=int)

    query = UsageLog.query.filter_by(user_id=user.id)

    if account_id:
        # Filter logs by listings associated with this account
        listing_ids = [l.id for l in Listing.query.filter_by(user_id=user.id, fb_account_id=account_id).all()]
        query = query.filter(UsageLog.listing_id.in_(listing_ids))

    logs = query.order_by(UsageLog.timestamp.desc()).limit(limit).all()

    activities = []
    for log in logs:
        listing = Listing.query.get(log.listing_id) if log.listing_id else None
        account = None
        if listing and listing.fb_account_id:
            account = FacebookAccount.query.get(listing.fb_account_id)

        # Extract status and details from action_data
        status = 'info'
        details = None
        if log.action_data and isinstance(log.action_data, dict):
            status = log.action_data.get('status', 'info')
            details = log.action_data.get('details')

        activities.append({
            'id': log.id,
            'action_type': log.action_type,
            'status': status,
            'details': details,
            'listing_title': listing.title if listing else None,
            'account_name': account.account_name if account else 'Unknown',
            'timestamp': log.timestamp.isoformat() if log.timestamp else None
        })

    return jsonify({
        'activities': activities,
        'count': len(activities)
    })


# ==================== CREATE TABLES ====================

# Create tables on startup (works with gunicorn)
def init_database():
    """Initialize database tables with retry logic."""
    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with app.app_context():
                db.create_all()
                print("✅ Database tables created")
                return True
        except Exception as e:
            print(f"⚠️ Database init attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print("❌ Database initialization failed after retries")
                return False

init_database()


# ==================== RUN APP ====================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
