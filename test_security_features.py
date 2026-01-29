import requests
import time
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import redis

# Configuration
BASE_URL = "http://localhost:8002"
DB_URL = "postgresql://postgres:1234@localhost:5432/medisecure"
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Setup DB connection
try:
    engine = create_engine(DB_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Database connection failed: {e}")
    sys.exit(1)

# Setup Redis connection
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
except Exception as e:
    print(f"Redis connection failed: {e}")
    sys.exit(1)

def cleanup_user(email):
    """Remove test user from DB and Redis to ensure clean state"""
    # 1. Clean DB
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM users WHERE email = :email"), {"email": email})
        db.commit()
    except Exception as e:
        print(f"DB Cleanup error: {e}")
    finally:
        db.close()
    
    # 2. Clean Redis
    try:
        redis_client.delete(f"registration:{email}")
        redis_client.delete(f"failed_login:{email}")
        keys = redis_client.keys(f"refresh_token:*") # We can't easily filter by email here as it is inside value, but for test, we can ignore or specific keys if known. 
        # Actually refresh token keys are refresh_token:user_id:token. We deleted user from DB so user_id is effectively gone, but keys remain.
        # It shouldn't block signup.
    except Exception as e:
        print(f"Redis Cleanup error: {e}")

def Test_Strong_Password_Policy():
    print("\n--- Testing Strong Password Policy ---")
    email = "policy_test@example.com"
    cleanup_user(email)

    # 1. Test Weak Password
    weak_payload = {
        "email": email,
        "password": "weak", # Too short, no special chars, etc.
        "role": "patient"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/auth/signup", json=weak_payload)
        if res.status_code == 422:
            print("✅ Weak password rejected correctly (Status 422)")
            # details = res.json().get('detail', [])
            # print(f"   Error details: {details}")
        else:
            print(f"❌ FAILED: Weak password was accepted! Status: {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"❌ Request failed: {e}")

    # 2. Test Strong Password
    strong_payload = {
        "email": email,
        "password": "StrongP@ssw0rd1", # Meets all criteria
        "role": "patient"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/auth/signup", json=strong_payload)
        if res.status_code == 201:
            print("✅ Strong password accepted correctly (Status 201)")
        else:
            print(f"❌ FAILED: Strong password was rejected! Status: {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    cleanup_user(email)

def Test_Account_Lockout():
    print("\n--- Testing Account Lockout ---")
    email = "lockout_test@example.com"
    password = "StrongP@ssw0rd1"
    
    cleanup_user(email)

    # 1. Create a verified user DIRECTLY in the database (not via API)
    # The API stores user in Redis until email verification, so we need to create directly
    from passlib.context import CryptContext
    import secrets
    import string
    
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    salt = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    hashed_password = pwd_context.hash(password + salt)
    
    db = SessionLocal()
    try:
        # Insert user directly into database as verified
        # Use uppercase enum value as stored in PostgreSQL
        db.execute(
            text("""
                INSERT INTO users (email, hashed_password, salt, role, is_verified, is_active)
                VALUES (:email, :hashed_password, :salt, 'PATIENT', TRUE, TRUE)
            """),
            {"email": email, "hashed_password": hashed_password, "salt": salt}
        )
        db.commit()
        print("✅ Test user created directly in database (verified).")
    except Exception as e:
        print(f"DB Insert failed: {e}")
        db.rollback()
        return
    finally:
        db.close()

    # 2. Attempt 3 Failed Logins (auth_v2 locks at >= 3)
    print("Attempting 3 failed logins...")
    for i in range(1, 4):
        res = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": "WrongPassword!"})
        if res.status_code == 401 and "Invalid credentials" in res.text:
            print(f"   Attempt {i}: Failed as expected (Invalid credentials)")
        elif res.status_code == 403 and "Account locked" in res.text:
            print(f"   Attempt {i}: Already locked (this is fine)")
        else:
            print(f"   Attempt {i}: Unexpected response: {res.status_code} {res.text}")

    # 3. Attempt 4th Login (Should be locked)
    print("Attempting 4th login (Should be locked)...")
    res = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": "WrongPassword!"})
    
    if res.status_code == 403 and "Account locked" in res.text:
        print("✅ Account locked successfully!")
        print(f"   Response: {res.json()['detail']}")
    else:
        print(f"❌ FAILED: Account was NOT locked. Status: {res.status_code}")
        print(res.text)

    # 4. Attempt Correct Login (Should still be locked)
    print("Attempting CORRECT login (Should still be locked)...")
    res = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password})
    
    if res.status_code == 403 and "Account locked" in res.text:
        print("✅ Lockout persists even with correct credentials.")
    else:
        print(f"❌ FAILED: Logged in despite lockout! Status: {res.status_code}")

    cleanup_user(email)

if __name__ == "__main__":
    try:
        # Simple health check
        requests.get(f"{BASE_URL}/health")
    except requests.exceptions.ConnectionError:
        print("❌ CRITICAL: The server is NOT running.")
        print("Please start the backend server in another terminal using:")
        print("   python main.py") # Or whatever the start command is
        sys.exit(1)

    Test_Strong_Password_Policy()
    Test_Account_Lockout()
