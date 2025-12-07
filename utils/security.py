from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import secrets
import string
from typing import Optional
import os

# Password Hashing Configuration
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def generate_salt(length: int = 16) -> str:
    """Generate a unique random salt string."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

def get_password_hash(password: str, salt: str) -> str:
    """
    Append salt to password and hash using Argon2id.
    Note: passlib handles the internal salting for Argon2, 
    but we are appending a user-specific salt as requested.
    """
    salted_password = password + salt
    return pwd_context.hash(salted_password)

def verify_password(plain_password: str, salt: str, hashed_password: str) -> bool:
    """Verify the password against the hash using the salt."""
    salted_password = plain_password + salt
    return pwd_context.verify(salted_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code."""
    return ''.join(secrets.choice(string.digits) for i in range(length))
