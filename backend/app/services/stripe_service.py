import os
import stripe
from datetime import datetime, timedelta
from typing import Optional

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
stripe.api_key = STRIPE_SECRET_KEY

class StripeService:
    @staticmethod
    def create_customer(email: str, name: str) -> str:
        """Create a Stripe customer"""
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"created_at": datetime.utcnow().isoformat()}
        )
        return customer.id

    @staticmethod
    def create_payment_intent(amount_cents: int, customer_id: str, description: str = "") -> dict:
        """Create a payment intent for one-time payments"""
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            customer=customer_id,
            description=description
        )
        return {
            "client_secret": intent.client_secret,
            "intent_id": intent.id
        }

    @staticmethod
    def create_subscription(customer_id: str, price_id: str) -> dict:
        """Create a Stripe subscription"""
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"]
        )
        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice else None
        }

    @staticmethod
    def cancel_subscription(subscription_id: str) -> bool:
        """Cancel a Stripe subscription"""
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except:
            return False

    @staticmethod
    def get_subscription(subscription_id: str) -> dict:
        """Get subscription details"""
        sub = stripe.Subscription.retrieve(subscription_id)
        return {
            "id": sub.id,
            "status": sub.status,
            "current_period_start": sub.current_period_start,
            "current_period_end": sub.current_period_end,
            "customer": sub.customer
        }

    @staticmethod
    def create_checkout_session(
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        client_reference_id: str,
        plan: str = "",
    ) -> dict:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=client_reference_id,
            allow_promotion_codes=True,
            metadata={"plan": plan},
        )
        return {"url": session.url, "id": session.id}

    @staticmethod
    def verify_webhook(payload: bytes, sig_header: str, webhook_secret: str) -> Optional[dict]:
        """Verify and parse Stripe webhook"""
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            return event
        except:
            return None
