import requests
import json
import time
import re

BASE_URL = "http://localhost:8000"

def test_api():
    print("========================================")
    print("  MediSecure API Testing Suite (Python)")
    print("========================================")
    
    # Generate unique test user
    timestamp = int(time.time())
    email = f"testuser_{timestamp}@example.com"
    password = "SecurePass123!@#"
    
    print(f"Test Configuration:\n  Email: {email}\n  Password: {password}\n")

    # 1. Health Check
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"✓ Health Check: {r.status_code}")
    except Exception as e:
        print(f"✗ Health Check Failed: {e}")
        return

    # 2. Signup
    print(f"[3/12] Testing User Signup...")
    signup_data = {"email": email, "password": password}
    r = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    if r.status_code == 201 or r.status_code == 200:
        print(f"✓ Signup Successful: {r.json()}")
    else:
        print(f"✗ Signup Failed: {r.status_code} {r.text}")
        return

    print("\n⚠ IMPORTANT: I need the verification code from the server logs.")
    print("I will wait 5 seconds and try to find it...")
    time.sleep(5)
    
    # We'll ask the user to provide it for now as a fallback, 
    # but I'll try to automate it in the next step.
    # For this script run, I'll stop here and search logs.
    
if __name__ == "__main__":
    test_api()
