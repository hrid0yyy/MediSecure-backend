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
    request: Request,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
):
    """
    Dependency to get current authenticated user from JWT token.
    Supports both:
    1. HttpOnly cookie (access_token) - preferred for security
    2. Authorization Bearer header - for API clients
    """
    from models.user import User
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = None
    
    # 1. Try to get token from HttpOnly cookie first (more secure)
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        token = cookie_token
    
    # 2. Fall back to Authorization header if no cookie
    elif credentials:
        token = credentials.credentials
    
    if not token:
        raise credentials_exception
    
    # Decode token
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if hasattr(user, 'is_active') and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    return user


def require_roles(*allowed_roles):
    """
    Dependency factory to require specific roles.
    
    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_roles("admin", "superadmin"))])
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        from models.user import User, UserRole
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


# Convenience dependencies for role checking
async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get current user and verify they are active"""
    if hasattr(current_user, 'is_active') and not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin(current_user = Depends(get_current_user)):
    """Require admin or superadmin role"""
    from models.user import UserRole
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def get_current_doctor(current_user = Depends(get_current_user)):
    """Require doctor role"""
    from models.user import UserRole
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor privileges required"
        )
    return current_user


async def get_current_staff_or_above(current_user = Depends(get_current_user)):
    """Require staff, admin, or superadmin role"""
    from models.user import UserRole
    allowed = [UserRole.STAFF, UserRole.ADMIN, UserRole.SUPERADMIN]
    if current_user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required"
        )
    return current_user
