import os
import stripe
from datetime import datetime, timedelta
from typing import Optional

from app.config import get_config

STRIPE_SECRET_KEY = get_config("STRIPE_SECRET_KEY") or get_config("STRIPE_API_KEY", "sk_test_placeholder")
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
    def create_topup_checkout_session(
        customer_id: str,
        credits: int,
        price_cents: int,
        success_url: str,
        cancel_url: str,
        client_reference_id: str,
    ) -> dict:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": price_cents,
                    "product_data": {
                        "name": f"Vantro Credit Top-up — {credits} credits",
                        "description": f"One-time purchase of {credits} video generation credits",
                    },
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=client_reference_id,
            metadata={"type": "topup", "credits": str(credits)},
        )
        return {"url": session.url, "id": session.id}

    @staticmethod
    def create_customer_portal_session(customer_id: str, return_url: str) -> dict:
        """Create a Stripe Billing Portal session for self-service billing management."""
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return {"url": session.url}

    @staticmethod
    def verify_webhook(payload: bytes, sig_header: str, webhook_secret: str) -> Optional[dict]:
        """Verify and parse Stripe webhook"""
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            return event
        except:
            return None

    @staticmethod
    def get_or_create_customer(email: str, name: str, existing_id: Optional[str] = None) -> str:
        """Return existing customer or create one. Idempotent."""
        if existing_id:
            return existing_id
        existing = stripe.Customer.list(email=email, limit=1)
        if existing.data:
            return existing.data[0].id
        return StripeService.create_customer(email, name)

    @staticmethod
    def create_setup_intent(customer_id: str) -> str:
        """Create a SetupIntent for card collection (no charge). Returns client_secret."""
        intent = stripe.SetupIntent.create(
            customer=customer_id,
            usage="off_session",
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
        )
        return intent.client_secret

    @staticmethod
    def attach_pm_and_subscribe(customer_id: str, pm_id: str, price_id: str) -> dict:
        """
        Attach payment method to customer, set as default, create monthly subscription.
        Billing cycle anchor = 28 days from now so Stripe charges 2 days before the
        natural monthly anniversary on every subsequent renewal.
        Returns {subscription_id, status, client_secret, payment_intent_id, period_end}.
        """
        from datetime import timezone
        stripe.PaymentMethod.attach(pm_id, customer=customer_id)
        stripe.Customer.modify(
            customer_id,
            invoice_settings={"default_payment_method": pm_id},
        )
        anchor = int((datetime.now(timezone.utc) + timedelta(days=28)).timestamp())
        sub = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            default_payment_method=pm_id,
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
            billing_cycle_anchor=anchor,
            proration_behavior="none",
        )
        pi = sub.latest_invoice.payment_intent if sub.latest_invoice else None
        period_end = datetime.fromtimestamp(sub.current_period_end, tz=timezone.utc) if sub.current_period_end else None
        return {
            "subscription_id": sub.id,
            "status": sub.status,
            "client_secret": pi.client_secret if pi else None,
            "payment_intent_id": pi.id if pi else None,
            "period_end": period_end,
        }
