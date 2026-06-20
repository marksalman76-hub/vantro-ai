import stripe
import os
from dotenv import load_dotenv
import json
import time

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY_TEST')

def test_payment_intent_webhook():
    print("\n" + "="*60)
    print("TEST 1: Payment Intent Succeeded")
    print("="*60)
    
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=2000,
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
    print("\n" + "="*60)
    print("TEST 3: Subscription Creation")
    print("="*60)
    
    if not customer_id:
        print("❌ No customer ID provided")
        return
    
    try:
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[
                {'price': 'price_1234567890'}
            ]
        )
        
        print(f"✅ Created subscription: {subscription['id']}")
        print(f"   Status: {subscription['status']}")
        
    except stripe.error.StripeError as e:
        print(f"⚠️  Note: {e}")
        print("   (You may need to set up test prices