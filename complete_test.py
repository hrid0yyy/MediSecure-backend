import requests
import json
import time

BASE_URL = "http://localhost:8000"

def complete_test(email, password, code):
    print(f"Resuming test for {email}...")
    headers = {}

    # 4. Email Verification (Skipping as already verified)
    # print(f"[4/12] Testing Email Verification...")
    # r = requests.post(f"{BASE_URL}/auth/verify-email", json={"email": email, "code": code})
    # print(f"Response: {r.status_code} {r.text}")
    # if r.status_code != 200: return

    # 5. Login
    print(f"[5/12] Testing User Login...")
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    print(f"Response: {r.status_code}")
    if r.status_code != 200: 
        print(f"Full Response: {r.json()}")
        return
    
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✓ Token obtained: {token[:10]}...")

    # 6. Get Current User
    print(f"[6/12] Testing Get Current User...")
    r = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
    print(f"Response: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

    # 7. Create Profile
    print(f"[7/12] Testing Create User Profile...")
    profile_data = {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01",
        "phone": "+15551234567",
        "address": "123 Security Lane",
        "medical_record_number": "MRN12345",
        "insurance_number": "INS67890",
        "emergency_contact_name": "Jane Doe",
        "emergency_contact_phone": "+15559876543"
    }
    r = requests.post(f"{BASE_URL}/api/v1/users/me/profile", json=profile_data, headers=headers)
    print(f"Response: {r.status_code}")

    # 8. Get Profile
    print(f"[8/12] Testing Get User Profile (Decrypted)...")
    r = requests.get(f"{BASE_URL}/api/v1/users/me/profile", headers=headers)
    print(f"Response: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

    # 9. Get Devices
    print(f"[9/12] Testing Get User Devices...")
    r = requests.get(f"{BASE_URL}/api/v1/users/me/devices", headers=headers)
    print(f"Response: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

    # 10. Update User
    print(f"[10/12] Testing Update User...")
    r = requests.put(f"{BASE_URL}/api/v1/users/me", json={"email": email}, headers=headers)
    print(f"Response: {r.status_code}")

    # 11. Change Password
    print(f"[11/12] Testing Change Password...")
    new_password = "NewSecurePassword123!"
    r = requests.post(f"{BASE_URL}/api/v1/users/me/change-password", 
                     json={"current_password": password, "new_password": new_password}, 
                     headers=headers)
    print(f"Response: {r.status_code} {r.text}")

    # 12. Login with new password
    print(f"[12/12] Testing Login with New Password...")
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": new_password})
    print(f"Response: {r.status_code}")
    if r.status_code == 200:
        print("✓ Successfully logged in with new password!")
    else:
        print(f"Error Details: {r.text}")

if __name__ == "__main__":
    import sys
    # Hardcoded from previous log check
    email = "testuser_1768204029@example.com"
    password = "SecurePass123!@#"
    code = "297609"
    complete_test(email, password, code)
