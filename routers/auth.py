from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter
from config.database import get_db
from config.redis_db import redis_client
from models import User
from schemas import UserCreate, UserLogin, UserVerify, Token
from utils import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    generate_salt, 
    generate_verification_code,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta
import logging

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)

# Mock Email Service
def send_verification_email(email: str, code: str):
    # In a real application, use aiosmtplib or an email service provider
    logger.info(f"Sending verification code {code} to {email}")
    print(f"============================================")
    print(f"EMAIL TO: {email}")
    print(f"CODE: {code}")
    print(f"============================================")

@router.post("/signup", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def signup(user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 1. Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Generate Salt and Hash Password
    salt = generate_salt()
    hashed_password = get_password_hash(user.password, salt)

    # 3. Create User (Unverified)
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        salt=salt,
        role=user.role,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 4. Generate Verification Code
    code = generate_verification_code()
    
    # 5. Store code in Redis (Expire in 5 minutes)
    redis_key = f"verification:{user.email}"
    redis_client.setex(redis_key, 300, code)

    # 6. Send Email (Background Task)
    background_tasks.add_task(send_verification_email, user.email, code)

    return {"message": "User created. Please check your email for verification code."}

@router.post("/verify-email", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def verify_email(verification: UserVerify, db: Session = Depends(get_db)):
    # 1. Get code from Redis
    redis_key = f"verification:{verification.email}"
    stored_code = redis_client.get(redis_key)

    if not stored_code:
        raise HTTPException(status_code=400, detail="Verification code expired or invalid")
    
    if stored_code != verification.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # 2. Update User status
    user = db.query(User).filter(User.email == verification.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_verified = True
    db.commit()

    # 3. Delete code from Redis
    redis_client.delete(redis_key)

    return {"message": "Email verified successfully"}

@router.post("/login", response_model=Token, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    # 1. Get User
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    # 2. Check Verification
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    # 3. Verify Password (using stored salt)
    if not verify_password(user_credentials.password, user.salt, user.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    # 4. Generate JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
