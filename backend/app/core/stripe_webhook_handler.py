"""
Stripe Webhook Handler

Receives and processes Stripe events:
- payment_intent.succeeded
- invoice.payment_succeeded
- invoice.payment_failed
- customer.subscription.updated
- customer.subscription.deleted
- charge.refunded
"""

import os
import json
import hmac
import hashlib
from typing import Dict, Any, Optional


def verify_stripe_webhook_signature(
    payload: str | bytes,
    signature: str,
    secret: str = None,
) -> bool:
    """Verify Stripe webhook signature"""
    if secret is None:
        secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    if not secret:
        return False
    
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    
    try:
        parts = {}
        for part in signature.split(","):
            key, value = part.split("=", 1)
            parts[key] = value
        
        timestamp = parts.get("t", "")
        received_signature = parts.get("v1", "")
        
        if not timestamp or not received_signature:
            return False
        
        signed_content = f"{timestamp}.{payload.decode('utf-8') if isinstance(payload, bytes) else payload}"
        
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            signed_content.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, received_signature)
    
    except Exception:
        return False


def parse_webhook_event(payload: str | bytes) -> Optional[Dict[str, Any]]:
    """Parse JSON webhook payload"""
    try:
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        return json.loads(payload)
    except Exception:
        return None


def handle_payment_intent_succeeded(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle payment_intent.succeeded event"""
    payment_intent = event.get("data", {}).get("object", {})
    return {
        "success": True,
        "event_type": "payment_intent.succeeded",
        "payment_intent_id": payment_intent.get("id"),
        "customer_id": payment_intent.get("customer"),
        "amount": payment_intent.get("amount"),
        "currency": payment_intent.get("currency"),
        "status": "payment_intent_succeeded",
        "action": "mark_payment_succeeded",
    }


def handle_invoice_payment_succeeded(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle invoice.payment_succeeded event"""
    invoice = event.get("data", {}).get("object", {})
    return {
        "success": True,
        "event_type": "invoice.payment_succeeded",
        "invoice_id": invoice.get("id"),
        "customer_id": invoice.get("customer"),
        "subscription_id": invoice.get("subscription"),
        "amount_paid": invoice.get("amount_paid"),
        "currency": invoice.get("currency"),
        "status": "invoice_paid",
        "action": "mark_invoice_paid_and_update_subscription",
    }


def handle_invoice_payment_failed(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle invoice.payment_failed event"""
    invoice = event.get("data", {}).get("object", {})
    return {
        "success": True,
        "event_type": "invoice.payment_failed",
        "invoice_id": invoice.get("id"),
        "customer_id": invoice.get("customer"),
        "subscription_id": invoice.get("subscription"),
        "amount": invoice.get("amount_due"),
        "currency": invoice.get("currency"),
        "status": "invoice_failed",
        "action": "schedule_payment_retry_or_notify_customer",
    }


def handle_customer_subscription_updated(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle customer.subscription.updated event"""
    subscription = event.get("data", {}).get("object", {})
    return {
        "success": True,
        "event_type": "customer.subscription.updated",
        "subscription_id": subscription.get("id"),
        "customer_id": subscription.get("customer"),
        "status": subscription.get("status"),
        "current_period_end": subscription.get("current_period_end"),
        "action": "update_subscription_state",
    }


def handle_customer_subscription_deleted(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle customer.subscription.deleted event"""
    subscription = event.get("data", {}).get("object", {})
    return {
        "success": True,
        "event_type": "customer.subscription.deleted",
        "subscription_id": subscription.get("id"),
        "customer_id": subscription.get("customer"),
        "status": "subscription_cancelled",
        "action": "mark_subscription_cancelled_and_downgrade_client",
    }


def handle_charge_refunded(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle charge.refunded event"""
    charge = event.get("data", {}).get("object", {})
    return {
        "success": True,
        "event_type": "charge.refunded",
        "charge_id": charge.get("id"),
        "customer_id": charge.get("customer"),
        "amount_refunded": charge.get("amount_refunded"),
        "currency": charge.get("currency"),
        "status": "charge_refunded",
        "action": "record_refund_and_credit_client_account",
    }


def route_webhook_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Route webhook event to appropriate handler"""
    event_type = event.get("type", "")
    
    handlers = {
        "payment_intent.succeeded": handle_payment_intent_succeeded,
        "invoice.payment_succeeded": handle_invoice_payment_succeeded,
        "invoice.payment_failed": handle_invoice_payment_failed,
        "customer.subscription.updated": handle_customer_subscription_updated,
        "customer.subscription.deleted": handle_customer_subscription_deleted,
        "charge.refunded": handle_charge_refunded,
    }
    
    handler = handlers.get(event_type)
    
    if not handler:
        return {
            "success": True,
            "event_type": event_type,
            "status": "event_type_not_handled",
            "action": "log_and_skip",
        }
    
    try:
        return handler(event)
    except Exception as exc:
        return {
            "success": False,
            "event_type": event_type,
            "error": str(exc),
            "status": "handler_exception",
        }


def process_stripe_webhook(payload: str | bytes, signature: str) -> Dict[str, Any]:
    """Complete webhook processing pipeline"""
    if not verify_stripe_webhook_signature(payload, signature):
        return {
            "success": False,
            "status": "signature_verification_failed",
            "customer_safe": True,
            "credential_values_exposed": False,
        }
    
    event = parse_webhook_event(payload)
    if not event:
        return {
            "success": False,
            "status": "webhook_parse_failed",
            "customer_safe": True,
            "credential_values_exposed": False,
        }
    
    handler_result = route_webhook_event(event)
    
    return {
        "success": True,
        "status": "webhook_processed",
        "event_id": event.get("id"),
        "event_type": event.get("type"),
        "handler_result": handler_result,
        "credential_values_exposed": False,
        "customer_safe": True,
    }