from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
import secrets
import string
from typing import Optional
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config.database import get_db

# Password Hashing Configuration
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

# Security scheme for bearer token
security = HTTPBearer()

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

def verify_password(plain_password: str, hashed_password: str, salt: str) -> bool:
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

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

import hashlib
from fastapi import Request

def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code."""
    return ''.join(secrets.choice(string.digits) for i in range(length))

def generate_device_fingerprint(request: Request) -> str:
    """
    Generate a unique device fingerprint based on request headers.
    Combines User-Agent and Client IP.
    """
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host if request.client else "unknown"
    
    raw_string = f"{user_agent}|{client_ip}"
    return hashlib.sha256(raw_string.encode()).hexdigest()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency to get current authenticated user from JWT token.
    """
    from models.user import User
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user
