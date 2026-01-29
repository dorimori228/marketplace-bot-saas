"""
Feature Gating Middleware
Enforces subscription limits and feature access based on user's plan tier.
"""

from functools import wraps
from flask import jsonify, g
from datetime import datetime, timedelta
from config.subscription_tiers import (
    get_tier_limits,
    has_feature,
    check_limit,
    TIER_BASIC,
    TIER_PRO,
    TIER_PREMIUM
)


class FeatureGateError(Exception):
    """Custom exception for feature gate violations."""
    def __init__(self, message, code, status_code=403, **kwargs):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.extra = kwargs
        super().__init__(self.message)

    def to_dict(self):
        return {
            'error': self.message,
            'code': self.code,
            **self.extra
        }


class FeatureGate:
    """Decorator-based feature gating for subscription enforcement."""

    @staticmethod
    def check_subscription(required_tier=None):
        """
        Decorator to check if user has active subscription.

        Args:
            required_tier (str, optional): Minimum tier required (basic, pro, premium)

        Usage:
            @app.route('/api/feature')
            @jwt_required()
            @FeatureGate.check_subscription(required_tier='pro')
            def protected_endpoint():
                ...
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Check if user is authenticated
                if not hasattr(g, 'current_user') or not g.current_user:
                    return jsonify({
                        'error': 'Authentication required',
                        'code': 'AUTH_REQUIRED'
                    }), 401

                user = g.current_user

                if getattr(user, 'is_admin', False):
                    g.subscription_tier = TIER_PREMIUM
                    g.subscription_limits = get_tier_limits(TIER_PREMIUM)
                    return f(*args, **kwargs)

                # Check if user has any subscription
                if user.subscription_status not in ['active', 'trialing']:
                    return jsonify({
                        'error': 'Active subscription required',
                        'code': 'SUBSCRIPTION_REQUIRED',
                        'current_status': user.subscription_status,
                        'upgrade_url': '/pricing'
                    }), 403

                # Check if subscription is expired
                if user.subscription_expires_at and user.subscription_expires_at < datetime.utcnow():
                    return jsonify({
                        'error': 'Subscription expired',
                        'code': 'SUBSCRIPTION_EXPIRED',
                        'expired_at': user.subscription_expires_at.isoformat()
                    }), 403

                # Check tier requirement if specified
                if required_tier:
                    tier_hierarchy = [TIER_BASIC, TIER_PRO, TIER_PREMIUM]

                    current_tier = user.subscription_tier.lower()
                    required = required_tier.lower()

                    if current_tier not in tier_hierarchy:
                        return jsonify({
                            'error': 'Invalid subscription tier',
                            'code': 'INVALID_TIER'
                        }), 403

                    if required not in tier_hierarchy:
                        return jsonify({
                            'error': 'Invalid required tier',
                            'code': 'SERVER_ERROR'
                        }), 500

                    current_level = tier_hierarchy.index(current_tier)
                    required_level = tier_hierarchy.index(required)

                    if current_level < required_level:
                        return jsonify({
                            'error': f'{required.title()} plan required',
                            'code': 'INSUFFICIENT_TIER',
                            'current_tier': current_tier,
                            'required_tier': required,
                            'upgrade_url': '/pricing'
                        }), 403

                # Store subscription info in g for use in endpoint
                g.subscription_tier = user.subscription_tier
                g.subscription_limits = get_tier_limits(user.subscription_tier)

                return f(*args, **kwargs)

            return decorated_function
        return decorator

    @staticmethod
    def check_limit(resource_type):
        """
        Decorator to check usage limits for a resource.

        Args:
            resource_type (str): Type of resource to check
                - 'facebook_accounts'
                - 'listings_per_month'
                - 'active_listings'
                - 'batch_size'

        Usage:
            @app.route('/api/accounts/add')
            @jwt_required()
            @FeatureGate.check_subscription()
            @FeatureGate.check_limit('facebook_accounts')
            def add_account():
                ...
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user = g.current_user
                tier = TIER_PREMIUM if getattr(user, 'is_admin', False) else user.subscription_tier

                # Get tier limits
                limits = get_tier_limits(tier)
                if not limits:
                    return jsonify({
                        'error': 'Unable to determine subscription limits',
                        'code': 'LIMIT_ERROR'
                    }), 500

                limit_key = f'max_{resource_type}'

                if limit_key not in limits:
                    # No limit for this resource, allow
                    return f(*args, **kwargs)

                limit = limits[limit_key]

                # -1 means unlimited
                if limit == -1:
                    return f(*args, **kwargs)

                # Get current usage
                from models import FacebookAccount, Listing, UsageLog

                if resource_type == 'facebook_accounts':
                    current_count = FacebookAccount.query.filter_by(
                        user_id=user.id,
                        status='active'
                    ).count()

                elif resource_type == 'active_listings':
                    current_count = Listing.query.filter_by(
                        user_id=user.id,
                        status='active'
                    ).count()

                elif resource_type == 'listings_per_month':
                    # Count listings created in the last 30 days
                    month_ago = datetime.utcnow() - timedelta(days=30)
                    current_count = UsageLog.query.filter(
                        UsageLog.user_id == user.id,
                        UsageLog.action_type == 'listing_created',
                        UsageLog.timestamp >= month_ago
                    ).count()

                elif resource_type == 'batch_size':
                    # This needs to be checked in the endpoint with actual batch size
                    # Store limit in g for endpoint to check
                    g.max_batch_size = limit
                    return f(*args, **kwargs)

                else:
                    current_count = 0

                # Check if limit exceeded
                if current_count >= limit:
                    return jsonify({
                        'error': f'{resource_type.replace("_", " ").title()} limit reached',
                        'code': 'LIMIT_REACHED',
                        'resource': resource_type,
                        'current': current_count,
                        'limit': limit,
                        'upgrade_required': True,
                        'current_tier': tier
                    }), 403

                # Store current usage in g for endpoint reference
                g.current_usage = {
                    'resource': resource_type,
                    'count': current_count,
                    'limit': limit,
                    'remaining': limit - current_count
                }

                return f(*args, **kwargs)

            return decorated_function
        return decorator

    @staticmethod
    def require_feature(feature_name):
        """
        Decorator to check if user's tier has access to a feature.

        Args:
            feature_name (str): Feature key from subscription_tiers.py
                - 'ai_features'
                - 'batch_operations'
                - 'templates'
                - 'location_randomization'

        Usage:
            @app.route('/api/ai/generate')
            @jwt_required()
            @FeatureGate.check_subscription()
            @FeatureGate.require_feature('ai_features')
            def ai_endpoint():
                ...
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user = g.current_user
                tier = user.subscription_tier

                # Check if tier has this feature
                if not has_feature(tier, feature_name):
                    # Determine which tier has this feature
                    required_tier = None
                    if has_feature(TIER_PRO, feature_name):
                        required_tier = TIER_PRO
                    elif has_feature(TIER_PREMIUM, feature_name):
                        required_tier = TIER_PREMIUM

                    return jsonify({
                        'error': f'{feature_name.replace("_", " ").title()} not available in your plan',
                        'code': 'FEATURE_NOT_AVAILABLE',
                        'feature': feature_name,
                        'current_tier': tier,
                        'required_tier': required_tier,
                        'upgrade_required': True
                    }), 403

                return f(*args, **kwargs)

            return decorated_function
        return decorator

    @staticmethod
    def check_rate_limit():
        """
        Decorator to enforce API rate limits based on subscription tier.

        Usage:
            @app.route('/api/listings')
            @jwt_required()
            @FeatureGate.check_subscription()
            @FeatureGate.check_rate_limit()
            def get_listings():
                ...
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user = g.current_user
                tier = user.subscription_tier

                limits = get_tier_limits(tier)
                if not limits or 'api_requests_per_minute' not in limits:
                    return f(*args, **kwargs)

                # Rate limiting implementation would go here
                # For now, just pass through
                # In production, use Flask-Limiter or Redis-based rate limiting

                return f(*args, **kwargs)

            return decorated_function
        return decorator


def get_usage_summary(user):
    """
    Get usage summary for a user across all resources.

    Args:
        user: User model instance

    Returns:
        dict: Usage summary with current counts and limits
    """
    from models import FacebookAccount, Listing, UsageLog

    tier = TIER_PREMIUM if getattr(user, 'is_admin', False) else user.subscription_tier
    limits = get_tier_limits(tier)

    if not limits:
        return {}

    # Count current usage
    active_accounts = FacebookAccount.query.filter_by(
        user_id=user.id,
        status='active'
    ).count()

    active_listings = Listing.query.filter_by(
        user_id=user.id,
        status='active'
    ).count()

    # Count listings created in last 30 days
    month_ago = datetime.utcnow() - timedelta(days=30)
    monthly_listings = UsageLog.query.filter(
        UsageLog.user_id == user.id,
        UsageLog.action_type == 'listing_created',
        UsageLog.timestamp >= month_ago
    ).count()

    def calc_percentage(current, limit):
        """Calculate percentage, handling unlimited (-1)."""
        if limit == -1:
            return 0
        if limit == 0:
            return 100
        return round((current / limit) * 100, 1)

    accounts_limit = limits.get('max_facebook_accounts', 0)
    monthly_limit = limits.get('max_listings_per_month', 0)

    return {
        'tier': tier,
        'accounts': {
            'current': active_accounts,
            'limit': accounts_limit,
            'percentage': calc_percentage(active_accounts, accounts_limit),
            'unlimited': accounts_limit == -1
        },
        'active_listings': {
            'current': active_listings,
            'limit': limits.get('max_active_listings', 0),
            'percentage': calc_percentage(active_listings, limits.get('max_active_listings', 0)),
            'unlimited': limits.get('max_active_listings') == -1
        },
        'monthly_listings': {
            'current': monthly_listings,
            'limit': monthly_limit,
            'percentage': calc_percentage(monthly_listings, monthly_limit),
            'unlimited': monthly_limit == -1
        },
        # Backward-compatible flat fields
        'accounts_count': active_accounts,
        'accounts_limit': accounts_limit,
        'listings_this_month': monthly_listings,
        'listings_limit': monthly_limit,
        'features': {
            'ai_features': limits.get('ai_features', False),
            'batch_operations': limits.get('batch_operations', False),
            'templates': limits.get('templates', False),
            'analytics': limits.get('analytics', 'none')
        }
    }


def validate_batch_size(user, batch_size):
    """
    Validate batch operation size against tier limits.

    Args:
        user: User model instance
        batch_size (int): Number of items in batch

    Returns:
        tuple: (bool: is_valid, str: error_message or None)
    """
    tier = user.subscription_tier
    limits = get_tier_limits(tier)

    if not limits:
        return False, "Unable to determine tier limits"

    max_batch = limits.get('max_batch_size', 1)

    if max_batch == 1:
        return False, "Batch operations not available in your plan"

    if max_batch == -1:
        return True, None

    if batch_size > max_batch:
        return False, f"Batch size {batch_size} exceeds limit of {max_batch} for {tier} plan"

    return True, None
