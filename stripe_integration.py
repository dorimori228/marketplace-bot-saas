"""
Stripe Integration for Subscription Management
Handles payment processing, subscription lifecycle, and webhooks.
"""

import stripe
import os
from datetime import datetime
from config.subscription_tiers import SUBSCRIPTION_TIERS, get_tier_info


# Initialize Stripe with API key from environment
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


class StripeIntegration:
    """Handles all Stripe-related operations."""

    @staticmethod
    def create_customer(email, user_id, metadata=None):
        """
        Create a Stripe customer.

        Args:
            email (str): Customer email
            user_id (int): Internal user ID
            metadata (dict, optional): Additional metadata

        Returns:
            stripe.Customer: Stripe customer object
        """
        customer_metadata = {'user_id': str(user_id)}
        if metadata:
            customer_metadata.update(metadata)

        try:
            customer = stripe.Customer.create(
                email=email,
                metadata=customer_metadata
            )
            return customer
        except stripe.error.StripeError as e:
            print(f"❌ Stripe error creating customer: {e}")
            raise

    @staticmethod
    def create_subscription(customer_id, price_id, trial_days=7):
        """
        Create a new subscription for a customer.

        Args:
            customer_id (str): Stripe customer ID
            price_id (str): Stripe price ID
            trial_days (int): Number of trial days (default: 7)

        Returns:
            stripe.Subscription: Stripe subscription object
        """
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                trial_period_days=trial_days,
                payment_behavior='default_incomplete',
                payment_settings={
                    'save_default_payment_method': 'on_subscription'
                },
                expand=['latest_invoice.payment_intent']
            )
            return subscription
        except stripe.error.StripeError as e:
            print(f"❌ Stripe error creating subscription: {e}")
            raise

    @staticmethod
    def create_checkout_session(customer_id, price_id, success_url, cancel_url, trial_days=7):
        """
        Create a Stripe Checkout session for subscription.

        Args:
            customer_id (str): Stripe customer ID
            price_id (str): Stripe price ID
            success_url (str): URL to redirect on success
            cancel_url (str): URL to redirect on cancel
            trial_days (int): Number of trial days

        Returns:
            stripe.checkout.Session: Checkout session object
        """
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1
                }],
                mode='subscription',
                subscription_data={
                    'trial_period_days': trial_days
                },
                success_url=success_url,
                cancel_url=cancel_url
            )
            return session
        except stripe.error.StripeError as e:
            print(f"❌ Stripe error creating checkout session: {e}")
            raise

    @staticmethod
    def update_subscription(subscription_id, new_price_id):
        """
        Update a subscription to a new price (upgrade/downgrade).

        Args:
            subscription_id (str): Stripe subscription ID
            new_price_id (str): New Stripe price ID

        Returns:
            stripe.Subscription: Updated subscription object
        """
        try:
            # Get current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)

            # Update subscription item
            stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0]['id'],
                    'price': new_price_id
                }],
                proration_behavior='create_prorations'  # Prorate charges
            )

            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            print(f"❌ Stripe error updating subscription: {e}")
            raise

    @staticmethod
    def cancel_subscription(subscription_id, at_period_end=True):
        """
        Cancel a subscription.

        Args:
            subscription_id (str): Stripe subscription ID
            at_period_end (bool): Cancel at period end (default) or immediately

        Returns:
            stripe.Subscription: Canceled subscription object
        """
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)

            return subscription
        except stripe.error.StripeError as e:
            print(f"❌ Stripe error canceling subscription: {e}")
            raise

    @staticmethod
    def reactivate_subscription(subscription_id):
        """
        Reactivate a canceled subscription (if not yet ended).

        Args:
            subscription_id (str): Stripe subscription ID

        Returns:
            stripe.Subscription: Reactivated subscription object
        """
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False
            )
            return subscription
        except stripe.error.StripeError as e:
            print(f"❌ Stripe error reactivating subscription: {e}")
            raise

    @staticmethod
    def get_subscription(subscription_id):
        """
        Retrieve subscription details.

        Args:
            subscription_id (str): Stripe subscription ID

        Returns:
            stripe.Subscription: Subscription object
        """
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            print(f"❌ Stripe error retrieving subscription: {e}")
            raise

    @staticmethod
    def get_customer(customer_id):
        """
        Retrieve customer details.

        Args:
            customer_id (str): Stripe customer ID

        Returns:
            stripe.Customer: Customer object
        """
        try:
            return stripe.Customer.retrieve(customer_id)
        except stripe.error.StripeError as e:
            print(f"❌ Stripe error retrieving customer: {e}")
            raise

    @staticmethod
    def create_portal_session(customer_id, return_url):
        """
        Create a Stripe Customer Portal session for self-service.

        Args:
            customer_id (str): Stripe customer ID
            return_url (str): URL to return to after portal session

        Returns:
            stripe.billing_portal.Session: Portal session object
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return session
        except stripe.error.StripeError as e:
            print(f"❌ Stripe error creating portal session: {e}")
            raise


class StripeWebhookHandler:
    """Handles Stripe webhook events."""

    @staticmethod
    def handle_webhook(payload, sig_header, webhook_secret):
        """
        Verify and handle Stripe webhook.

        Args:
            payload (bytes): Request body
            sig_header (str): Stripe signature header
            webhook_secret (str): Webhook secret from Stripe

        Returns:
            stripe.Event: Verified event object
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError:
            # Invalid payload
            raise ValueError("Invalid webhook payload")
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            raise ValueError("Invalid webhook signature")

    @staticmethod
    def process_event(event, db):
        """
        Process a Stripe webhook event.

        Args:
            event (stripe.Event): Stripe event object
            db: SQLAlchemy database instance

        Returns:
            dict: Processing result
        """
        from models import User, Subscription as SubscriptionModel

        event_type = event['type']
        event_data = event['data']['object']

        print(f"📨 Processing Stripe webhook: {event_type}")

        try:
            # Subscription created
            if event_type == 'customer.subscription.created':
                subscription_id = event_data['id']
                customer_id = event_data['customer']
                status = event_data['status']

                print(f"✅ Subscription created: {subscription_id}, status: {status}")

                # Find user by stripe_customer_id
                user = User.query.filter_by(stripe_customer_id=customer_id).first()
                if not user:
                    print(f"⚠️ User not found for customer: {customer_id}")
                    return {'status': 'user_not_found'}

                # Determine tier from price_id
                price_id = event_data['items']['data'][0]['price']['id']
                tier = StripeWebhookHandler._get_tier_from_price_id(price_id)

                # Create subscription record
                subscription = SubscriptionModel(
                    user_id=user.id,
                    stripe_subscription_id=subscription_id,
                    stripe_price_id=price_id,
                    plan_tier=tier,
                    status=status,
                    current_period_start=datetime.fromtimestamp(event_data['current_period_start']),
                    current_period_end=datetime.fromtimestamp(event_data['current_period_end'])
                )
                db.session.add(subscription)

                # Update user
                user.subscription_tier = tier
                user.subscription_status = status
                user.subscription_expires_at = datetime.fromtimestamp(event_data['current_period_end'])

                db.session.commit()

                return {'status': 'subscription_created', 'tier': tier}

            # Subscription updated
            elif event_type == 'customer.subscription.updated':
                subscription_id = event_data['id']
                status = event_data['status']

                subscription = SubscriptionModel.query.filter_by(
                    stripe_subscription_id=subscription_id
                ).first()

                if not subscription:
                    print(f"⚠️ Subscription not found: {subscription_id}")
                    return {'status': 'subscription_not_found'}

                # Update subscription
                subscription.status = status
                subscription.current_period_start = datetime.fromtimestamp(event_data['current_period_start'])
                subscription.current_period_end = datetime.fromtimestamp(event_data['current_period_end'])
                subscription.cancel_at_period_end = event_data.get('cancel_at_period_end', False)

                # Update user
                user = subscription.user
                user.subscription_status = status
                user.subscription_expires_at = datetime.fromtimestamp(event_data['current_period_end'])

                db.session.commit()

                return {'status': 'subscription_updated'}

            # Subscription deleted
            elif event_type == 'customer.subscription.deleted':
                subscription_id = event_data['id']

                subscription = SubscriptionModel.query.filter_by(
                    stripe_subscription_id=subscription_id
                ).first()

                if not subscription:
                    return {'status': 'subscription_not_found'}

                # Update subscription
                subscription.status = 'canceled'
                subscription.canceled_at = datetime.utcnow()

                # Update user
                user = subscription.user
                user.subscription_status = 'canceled'

                db.session.commit()

                return {'status': 'subscription_canceled'}

            # Payment succeeded
            elif event_type == 'invoice.payment_succeeded':
                subscription_id = event_data.get('subscription')
                if not subscription_id:
                    return {'status': 'no_subscription'}

                subscription = SubscriptionModel.query.filter_by(
                    stripe_subscription_id=subscription_id
                ).first()

                if not subscription:
                    return {'status': 'subscription_not_found'}

                # Update status to active
                subscription.status = 'active'
                subscription.user.subscription_status = 'active'

                db.session.commit()

                return {'status': 'payment_succeeded'}

            # Payment failed
            elif event_type == 'invoice.payment_failed':
                subscription_id = event_data.get('subscription')
                if not subscription_id:
                    return {'status': 'no_subscription'}

                subscription = SubscriptionModel.query.filter_by(
                    stripe_subscription_id=subscription_id
                ).first()

                if not subscription:
                    return {'status': 'subscription_not_found'}

                # Update status to past_due
                subscription.status = 'past_due'
                subscription.user.subscription_status = 'past_due'

                db.session.commit()

                # TODO: Send email notification to user

                return {'status': 'payment_failed'}

            return {'status': 'unhandled_event', 'type': event_type}

        except Exception as e:
            print(f"❌ Error processing webhook event: {e}")
            db.session.rollback()
            raise

    @staticmethod
    def _get_tier_from_price_id(price_id):
        """
        Determine subscription tier from Stripe price ID.

        Args:
            price_id (str): Stripe price ID

        Returns:
            str: Tier name (basic, pro, premium)
        """
        for tier_name, tier_data in SUBSCRIPTION_TIERS.items():
            if tier_data.get('stripe_price_id') == price_id:
                return tier_name

        # Default to basic if not found
        print(f"⚠️ Unknown price ID: {price_id}, defaulting to basic")
        return 'basic'


def setup_stripe_products():
    """
    One-time setup: Create Stripe products and prices.
    Run this script once to initialize Stripe with your subscription tiers.

    Returns:
        dict: Created products and prices
    """
    created = {}

    for tier_key, tier_data in SUBSCRIPTION_TIERS.items():
        try:
            # Create product
            product = stripe.Product.create(
                name=tier_data['name'],
                description=tier_data['description'],
                metadata={'tier': tier_key}
            )

            # Create price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(tier_data['price'] * 100),  # Convert to pence
                currency=tier_data['currency'],
                recurring={'interval': 'month'},
                metadata={'tier': tier_key}
            )

            created[tier_key] = {
                'product_id': product.id,
                'price_id': price.id
            }

            print(f"✅ Created {tier_data['name']}: price_id = {price.id}")

        except stripe.error.StripeError as e:
            print(f"❌ Error creating {tier_key}: {e}")

    print("\n📝 Update config/subscription_tiers.py with these price IDs:")
    for tier_key, ids in created.items():
        print(f"{tier_key}: stripe_price_id = '{ids['price_id']}'")

    return created


if __name__ == '__main__':
    # Run this script to set up Stripe products
    print("🚀 Setting up Stripe products...")
    setup_stripe_products()
