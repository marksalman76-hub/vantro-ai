import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("✅ Health Check:", response.status_code)
    print(json.dumps(response.json(), indent=2))

def test_root():
    """Test root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print("\n✅ Root Endpoint:", response.status_code)
    print(json.dumps(response.json(), indent=2))

def test_register():
    """Test user registration"""
    payload = {
        "email": "test@vantro.ai",
        "password": "testpass123",
        "name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
    print("\n✅ Register Endpoint:", response.status_code)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"Access Token: {token[:20]}...")
        return token
    else:
        print(response.text)
    return None

def test_login(email="test@vantro.ai", password="testpass123"):
    """Test user login"""
    payload = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
    print("\n✅ Login Endpoint:", response.status_code)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"Access Token: {token[:20]}...")
        return token
    else:
        print(response.text)
    return None

def test_credits(user_id="test-user-1"):
    """Test credits endpoint"""
    response = requests.get(f"{BASE_URL}/api/credits?user_id={user_id}")
    print("\n✅ Credits Endpoint:", response.status_code)
    print(json.dumps(response.json(), indent=2))

def test_admin_stats():
    """Test admin stats endpoint"""
    response = requests.get(f"{BASE_URL}/api/admin/stats")
    print("\n✅ Admin Stats Endpoint:", response.status_code)
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("🧪 VANTRO AI API TEST SUITE")
    print("=" * 50)
    
    try:
        test_health()
        test_root()
        test_credits()
        test_admin_stats()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the API is running: python backend/app/main.py")
