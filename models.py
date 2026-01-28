"""
PostgreSQL Database Models for Multi-Tenant Facebook Marketplace Bot
Designed for cloud deployment with user authentication and subscriptions.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Index

db = SQLAlchemy()


class User(db.Model):
    """User accounts with authentication and subscription info."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Stripe integration
    stripe_customer_id = db.Column(db.String(100), unique=True, index=True)

    # Subscription info (denormalized for quick access)
    subscription_tier = db.Column(db.String(20), default='none')  # none, basic, pro, premium
    subscription_status = db.Column(db.String(20), default='inactive')  # inactive, active, past_due, canceled
    subscription_expires_at = db.Column(db.DateTime)

    # Account metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime)

    # Relationships
    facebook_accounts = db.relationship('FacebookAccount', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    listings = db.relationship('Listing', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    usage_logs = db.relationship('UsageLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    templates = db.relationship('ListingTemplate', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'subscription_tier': self.subscription_tier,
            'subscription_status': self.subscription_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FacebookAccount(db.Model):
    """Facebook accounts linked to users (one user can have multiple FB accounts)."""
    __tablename__ = 'facebook_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    account_name = db.Column(db.String(100), nullable=False)
    cookies_encrypted = db.Column(db.Text, nullable=False)  # Encrypted JSON with Fernet

    status = db.Column(db.String(20), default='active')  # active, suspended, deleted
    last_sync = db.Column(db.DateTime)  # Last time cookies were synced

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    listings = db.relationship('Listing', backref='fb_account', lazy='dynamic', cascade='all, delete-orphan')
    analytics = db.relationship('Analytics', backref='fb_account', lazy='dynamic', cascade='all, delete-orphan')

    # Unique constraint: one user can't have duplicate account names
    __table_args__ = (
        db.UniqueConstraint('user_id', 'account_name', name='uq_user_account'),
        Index('idx_fb_account_user_status', 'user_id', 'status'),
    )

    def __repr__(self):
        return f'<FacebookAccount {self.account_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'account_name': self.account_name,
            'status': self.status,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Listing(db.Model):
    """Marketplace listings created by users."""
    __tablename__ = 'listings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    fb_account_id = db.Column(db.Integer, db.ForeignKey('facebook_accounts.id', ondelete='CASCADE'), nullable=False, index=True)

    # Listing details
    title = db.Column(db.Text, nullable=False)
    price = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    product_tags = db.Column(db.Text)  # Comma-separated tags
    location = db.Column(db.String(200))

    # Facebook metadata
    facebook_listing_id = db.Column(db.String(100), index=True)
    facebook_url = db.Column(db.String(500))

    # Status tracking
    status = db.Column(db.String(20), default='pending', index=True)  # pending, active, failed, deleted, sold
    notes = db.Column(db.Text)
    error_message = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)  # When it went live on FB

    # Relationships
    images = db.relationship('ListingImage', backref='listing', lazy='dynamic', cascade='all, delete-orphan', order_by='ListingImage.image_order')
    analytics = db.relationship('Analytics', backref='listing', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_listing_user_status', 'user_id', 'status'),
        Index('idx_listing_account_status', 'fb_account_id', 'status'),
        Index('idx_listing_created', 'created_at'),
    )

    def __repr__(self):
        return f'<Listing {self.title[:30]}>'

    def to_dict(self, include_images=False):
        data = {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'description': self.description,
            'category': self.category,
            'product_tags': self.product_tags,
            'location': self.location,
            'status': self.status,
            'facebook_listing_id': self.facebook_listing_id,
            'facebook_url': self.facebook_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }

        if include_images:
            data['images'] = [img.to_dict() for img in self.images.all()]

        return data


class ListingImage(db.Model):
    """Images associated with listings."""
    __tablename__ = 'listing_images'

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id', ondelete='CASCADE'), nullable=False, index=True)

    image_url = db.Column(db.Text, nullable=False)  # S3/Cloudinary URL
    image_order = db.Column(db.Integer, default=0)  # Order in listing

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_listing_image_order', 'listing_id', 'image_order'),
    )

    def __repr__(self):
        return f'<ListingImage {self.image_url[:50]}>'

    def to_dict(self):
        return {
            'id': self.id,
            'image_url': self.image_url,
            'image_order': self.image_order
        }


class Subscription(db.Model):
    """Stripe subscription records."""
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Stripe metadata
    stripe_subscription_id = db.Column(db.String(100), unique=True, index=True)
    stripe_price_id = db.Column(db.String(100))  # Which Stripe price they subscribed to

    # Subscription details
    plan_tier = db.Column(db.String(20), nullable=False)  # basic, pro, premium
    status = db.Column(db.String(20), nullable=False, index=True)  # active, past_due, canceled, incomplete

    # Billing period
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime, index=True)

    # Cancellation
    cancel_at_period_end = db.Column(db.Boolean, default=False)
    canceled_at = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Subscription {self.plan_tier} - {self.status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'plan_tier': self.plan_tier,
            'status': self.status,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'cancel_at_period_end': self.cancel_at_period_end
        }


class UsageLog(db.Model):
    """Track user actions for usage limits and analytics."""
    __tablename__ = 'usage_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    action_type = db.Column(db.String(50), nullable=False, index=True)  # listing_created, listing_deleted, ai_generation, etc.
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id', ondelete='SET NULL'))

    # Action data
    action_data = db.Column(db.JSON)  # Additional context

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index('idx_usage_user_action_time', 'user_id', 'action_type', 'timestamp'),
    )

    def __repr__(self):
        return f'<UsageLog {self.action_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'action_type': self.action_type,
            'listing_id': self.listing_id,
            'action_data': self.action_data,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class ListingTemplate(db.Model):
    """Reusable listing templates (Pro+ feature)."""
    __tablename__ = 'listing_templates'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Template fields
    category = db.Column(db.String(100))
    price_template = db.Column(db.String(100))
    description_template = db.Column(db.Text)
    location = db.Column(db.String(200))
    product_tags = db.Column(db.Text)

    # Usage tracking
    use_count = db.Column(db.Integer, default=0)
    last_used_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='uq_user_template'),
    )

    def __repr__(self):
        return f'<ListingTemplate {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price_template': self.price_template,
            'description_template': self.description_template,
            'location': self.location,
            'product_tags': self.product_tags,
            'use_count': self.use_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }


class Analytics(db.Model):
    """Track listing performance and bot actions for analytics."""
    __tablename__ = 'analytics'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    fb_account_id = db.Column(db.Integer, db.ForeignKey('facebook_accounts.id', ondelete='SET NULL'), index=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id', ondelete='SET NULL'), index=True)

    # Action details
    action = db.Column(db.String(50), nullable=False, index=True)  # listing_created, listing_deleted, ai_used, etc.
    success = db.Column(db.Boolean, default=True, index=True)
    error_message = db.Column(db.Text)

    # Performance metrics
    duration_seconds = db.Column(db.Integer)  # How long the action took

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index('idx_analytics_user_action', 'user_id', 'action', 'timestamp'),
        Index('idx_analytics_listing', 'listing_id', 'timestamp'),
    )

    def __repr__(self):
        return f'<Analytics {self.action}>'

    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'success': self.success,
            'error_message': self.error_message,
            'duration_seconds': self.duration_seconds,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


def init_db(app):
    """Initialize database with Flask app."""
    db.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")


def drop_all(app):
    """Drop all tables (use with caution!)."""
    with app.app_context():
        db.drop_all()
        print("⚠️ All database tables dropped")
