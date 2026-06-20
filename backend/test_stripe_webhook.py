"""
Stripe Webhook Test Script

This script sends test webhook events to your local webhook listener.
Use after running: python backend/stripe_webhook_listener.py

Run: python backend/test_stripe_webhook.py
"""

import stripe
import os
from dotenv import load_dotenv
import json
import time

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY_TEST')

def test_payment_intent_webhook():
    """Test payment intent succeeded webhook"""
    print("\n" + "="*60)
    print("TEST 1: Payment Intent Succeeded")
    print("="*60)
    
    try:
        # Create a test payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=2000,  # $20.00
            currency='usd',
            payment_method_types=['card'],
            description='Test payment for webhook'
        )
        
        print(f"✅ Created payment intent: {payment_intent['id']}")
        print(f"   Amount: ${payment_intent['amount']/100:.2f}")
        print(f"   Status: {payment_intent['status']}")
        
    except stripe.error.StripeError as e:
        print(f"❌ Error: {e}")


def test_customer_creation():
    """Test customer creation"""
    print("\n" + "="*60)
    print("TEST 2: Customer Creation")
    print("="*60)
    
    try:
        customer = stripe.Customer.create(
            email=f'test-{int(time.time())}@trance-formation.com.au',
            description='Test customer for webhook'
        )
        
        print(f"✅ Created customer: {customer['id']}")
        print(f"   Email: {customer['email']}")
        
        return customer['id']
        
    except stripe.error.StripeError as e:
        print(f"❌ Error: {e}")
        return None


def test_subscription(customer_id):
    """Test subscription creation"""
    print("\n" + "="*60)
    print("TEST 3: Subscription Creation")
    print("="*60)
    
    if not customer_id:
        print("❌ No customer ID provided")
        return
    
    try:
        # Get a test price ID (you'll need to create one in Stripe dashboard)
        # For now, we'll just show the structure
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[
                {'price': 'price_1234567890'}  # Replace with actual test price
            ]
        )
        
        print(f"✅ Created subscription: {subscription['id']}")
        print(f"   Status: {subscription['status']}")
        
    except stripe.error.StripeError as e:
        print(f"⚠️  Note: {e}")
        print("   (You may need to set up test prices in Stripe dashboard)")


def test_invoice_webhook():
    """Test invoice payment succeeded"""
    print("\n" + "="*60)
    print("TEST 4: Invoice Payment (Simulated)")
    print("="*60)
    
    print("ℹ️  To test invoice webhooks:")
    print("   1. Create a customer in Stripe dashboard")
    print("   2. Create an invoice for that customer")
    print("   3. Pay the invoice to trigger webhook")
    print("   4. Webhook listener will log the event")


def main():
    """Run all webhook tests"""
    print("\n🧪 STRIPE WEBHOOK TEST SUITE")
    print("This script tests Stripe webhook functionality")
    print(f"Stripe Account: {stripe.api_key[:20]}...")
    
    # Test payment intent
    test_payment_intent_webhook()
    
    time.sleep(1)
    
    # Test customer
    customer_id = test_customer_creation()
    
    time.sleep(1)
    
    # Test subscription
    if customer_id:
        test_subscription(customer_id)
    
    time.sleep(1)
    
    # Test invoice
    test_invoice_webhook()
    
    print("\n" + "="*60)
    print("✅ TESTS COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Start webhook listener: python backend/stripe_webhook_listener.py")
    print("2. In another terminal, run Stripe CLI:")
    print("   npx stripe listen --forward-to localhost:8001/webhook")
    print("3. In a third terminal, run this test:")
    print("   python backend/test_stripe_webhook.py")
    print("\nWebhook events will be logged in webhook_events.log")


if __name__ == "__main__":
    main()