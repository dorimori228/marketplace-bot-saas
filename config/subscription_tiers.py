"""
Subscription Tier Definitions
Defines pricing, limits, and features for each subscription plan.
"""

# NOTE: Update stripe_price_id values with actual IDs from Stripe Dashboard
SUBSCRIPTION_TIERS = {
    'basic': {
        'name': 'Basic',
        'price': 15.00,  # £15/month
        'currency': 'gbp',
        'stripe_price_id': 'price_basic_monthly',  # Replace with actual Stripe Price ID
        'description': 'Perfect for small-scale sellers',

        'limits': {
            # Account limits
            'max_facebook_accounts': 3,

            # Listing limits
            'max_listings_per_month': 100,
            'max_active_listings': 50,
            'max_batch_size': 1,  # No batch operations (one at a time)

            # Feature access
            'batch_operations': False,
            'templates': False,
            'ai_features': False,
            'analytics': 'basic',  # basic, advanced, premium
            'priority_support': False,
            'image_optimization': True,
            'location_randomization': False,

            # Rate limits
            'api_requests_per_minute': 10,
        },

        'features': [
            'Single listing creation',
            'Up to 3 Facebook accounts',
            '100 listings per month',
            'Basic analytics dashboard',
            'Image optimization',
            'Email support'
        ]
    },

    'pro': {
        'name': 'Professional',
        'price': 30.00,  # £30/month
        'currency': 'gbp',
        'stripe_price_id': 'price_pro_monthly',  # Replace with actual Stripe Price ID
        'description': 'For growing businesses',

        'limits': {
            # Account limits
            'max_facebook_accounts': 10,

            # Listing limits
            'max_listings_per_month': 500,
            'max_active_listings': 200,
            'max_batch_size': 50,  # Can process up to 50 listings at once

            # Feature access
            'batch_operations': True,
            'templates': True,
            'ai_features': False,
            'analytics': 'advanced',
            'priority_support': False,
            'image_optimization': True,
            'location_randomization': True,

            # Rate limits
            'api_requests_per_minute': 30,
        },

        'features': [
            'All Basic features',
            'Batch create/delete/relist',
            'Up to 10 Facebook accounts',
            '500 listings per month',
            'Listing templates',
            'Advanced analytics',
            'Location randomization',
            'Activity logging'
        ]
    },

    'premium': {
        'name': 'Premium',
        'price': 50.00,  # £50/month
        'currency': 'gbp',
        'stripe_price_id': 'price_premium_monthly',  # Replace with actual Stripe Price ID
        'description': 'For power users and agencies',

        'limits': {
            # Account limits
            'max_facebook_accounts': -1,  # -1 = unlimited

            # Listing limits
            'max_listings_per_month': -1,  # Unlimited
            'max_active_listings': -1,  # Unlimited
            'max_batch_size': 100,

            # Feature access
            'batch_operations': True,
            'templates': True,
            'ai_features': True,  # AI title/description generation
            'analytics': 'premium',
            'priority_support': True,
            'image_optimization': True,
            'location_randomization': True,

            # Rate limits
            'api_requests_per_minute': 60,
        },

        'features': [
            'All Pro features',
            'Unlimited Facebook accounts',
            'Unlimited listings',
            'AI title variations (OpenAI)',
            'AI description generation',
            'Image metadata randomization',
            'Image auto-cropping',
            'Account writing styles',
            'Premium analytics',
            'Priority support',
            'Early access to new features'
        ]
    }
}


def get_tier_limits(tier_name):
    """
    Get the limits for a specific subscription tier.

    Args:
        tier_name (str): Tier name (basic, pro, premium)

    Returns:
        dict: Tier limits or None if tier doesn't exist
    """
    if not tier_name:
        tier_name = 'basic'
    normalized = tier_name.lower()
    if normalized == 'free':
        normalized = 'basic'
    tier = SUBSCRIPTION_TIERS.get(normalized)
    return tier['limits'] if tier else None


def get_tier_info(tier_name):
    """
    Get full information about a tier.

    Args:
        tier_name (str): Tier name (basic, pro, premium)

    Returns:
        dict: Tier information or None if tier doesn't exist
    """
    if not tier_name:
        tier_name = 'basic'
    normalized = tier_name.lower()
    if normalized == 'free':
        normalized = 'basic'
    return SUBSCRIPTION_TIERS.get(normalized)


def check_limit(tier_name, limit_key, current_value):
    """
    Check if current usage is within tier limits.

    Args:
        tier_name (str): Tier name (basic, pro, premium)
        limit_key (str): Key in limits dict (e.g., 'max_listings_per_month')
        current_value (int): Current usage count

    Returns:
        tuple: (bool: within_limit, int: limit_value)
    """
    limits = get_tier_limits(tier_name)

    if not limits or limit_key not in limits:
        return True, -1  # No limit if not defined

    limit = limits[limit_key]

    # -1 means unlimited
    if limit == -1:
        return True, -1

    return current_value < limit, limit


def has_feature(tier_name, feature_name):
    """
    Check if a tier has access to a specific feature.

    Args:
        tier_name (str): Tier name (basic, pro, premium)
        feature_name (str): Feature key (e.g., 'ai_features', 'batch_operations')

    Returns:
        bool: True if tier has access to feature
    """
    limits = get_tier_limits(tier_name)

    if not limits:
        return False

    if feature_name not in limits:
        return False

    feature_value = limits[feature_name]

    # Handle boolean features
    if isinstance(feature_value, bool):
        return feature_value

    # Handle string features (like analytics levels)
    # For now, any non-false value means enabled
    return bool(feature_value)


def get_tier_hierarchy():
    """
    Get tier hierarchy for upgrade/downgrade logic.

    Returns:
        list: Tier names in order from lowest to highest
    """
    return ['basic', 'pro', 'premium']


def can_upgrade(current_tier, target_tier):
    """
    Check if user can upgrade to target tier.

    Args:
        current_tier (str): Current tier name
        target_tier (str): Target tier name

    Returns:
        bool: True if upgrade is valid
    """
    hierarchy = get_tier_hierarchy()

    if current_tier not in hierarchy or target_tier not in hierarchy:
        return False

    return hierarchy.index(target_tier) > hierarchy.index(current_tier)


def can_downgrade(current_tier, target_tier):
    """
    Check if user can downgrade to target tier.

    Args:
        current_tier (str): Current tier name
        target_tier (str): Target tier name

    Returns:
        bool: True if downgrade is valid
    """
    hierarchy = get_tier_hierarchy()

    if current_tier not in hierarchy or target_tier not in hierarchy:
        return False

    return hierarchy.index(target_tier) < hierarchy.index(current_tier)


def get_all_tiers():
    """
    Get all available subscription tiers.

    Returns:
        dict: All subscription tiers
    """
    return SUBSCRIPTION_TIERS


def format_tier_comparison():
    """
    Format tier comparison for display (landing page, pricing table).

    Returns:
        list: List of tier dicts with formatted information
    """
    comparison = []

    for tier_key in get_tier_hierarchy():
        tier = SUBSCRIPTION_TIERS[tier_key]
        limits = tier['limits']

        comparison.append({
            'key': tier_key,
            'name': tier['name'],
            'price': tier['price'],
            'currency': tier['currency'],
            'description': tier['description'],
            'features': tier['features'],
            'limits': {
                'accounts': limits['max_facebook_accounts'] if limits['max_facebook_accounts'] != -1 else 'Unlimited',
                'monthly_listings': limits['max_listings_per_month'] if limits['max_listings_per_month'] != -1 else 'Unlimited',
                'active_listings': limits['max_active_listings'] if limits['max_active_listings'] != -1 else 'Unlimited',
                'batch_size': limits['max_batch_size']
            }
        })

    return comparison


# For quick reference in code
TIER_BASIC = 'basic'
TIER_PRO = 'pro'
TIER_PREMIUM = 'premium'
