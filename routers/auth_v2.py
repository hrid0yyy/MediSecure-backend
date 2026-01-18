"""
Authentication Router with HttpOnly Cookies
Routes: /api/auth/*

This module handles all authentication related endpoints with secure
HttpOnly cookie-based JWT tokens for XSS protection.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter
from config.database import get_db
from config.redis_db import redis_client
from models import User, UserDevice
from schemas import (
    UserCreate, UserLogin, UserVerify, UserForgotPassword, 
    UserResetPassword, UserDeviceVerify, UserResponse, LoginResponse, SignupResponse
)
from utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    generate_salt,
    generate_verification_code,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    generate_device_fingerprint
)
from utils.security import get_current_user
from datetime import datetime, timedelta
import logging
import json
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from pydantic import EmailStr
import os
import secrets

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# ============ CONFIGURATION ============
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# Cookie settings
ACCESS_TOKEN_EXPIRE = 15 * 60  # 15 minutes in seconds
REFRESH_TOKEN_EXPIRE = 7 * 24 * 60 * 60  # 7 days in seconds
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"  # True in production with HTTPS
COOKIE_SAMESITE = "lax"  # or "strict" for more security

def _get_gmail_credentials():
    email = os.getenv("GMAIL_EMAIL")
    password = os.getenv("GMAIL_APP_PASSWORD")
    if not email or not password:
        raise ValueError("Gmail credentials are not configured. Set GMAIL_EMAIL and GMAIL_APP_PASSWORD.")
    return email, password

# ============ EMAIL FUNCTIONS ============
async def send_verification_email(email: EmailStr, code: str):
    """Send verification email using Gmail SMTP"""
    html = f"""
    <html>
        <body>
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Welcome to MediSecure!</h2>
                <p>Please use the following code to verify your email address:</p>
                <h1 style="color: #4CAF50; letter-spacing: 5px;">{code}</h1>
                <p>This code will expire in 10 minutes.</p>
                <p>If you did not request this, please ignore this email.</p>
            </div>
        </body>
    </html>
    """
    try:
        gmail_email, gmail_password = _get_gmail_credentials()
        message = EmailMessage()
        message["Subject"] = "MediSecure - Email Verification"
        message["From"] = gmail_email
        message["To"] = email
        message.set_content("Use the code above to verify your email.")
        message.add_alternative(html, subtype="html")

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(gmail_email, gmail_password)
            server.send_message(message)
        logger.info(f"Verification email sent to {email} via Gmail.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        print(f"FALLBACK - VERIFICATION CODE: {code}")

async def send_password_reset_email(email: EmailStr, code: str):
    """Send password reset email using Gmail SMTP"""
    html = f"""
    <html>
        <body>
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>MediSecure Password Reset</h2>
                <p>You requested to reset your password. Use the code below:</p>
                <h1 style="color: #FF5722; letter-spacing: 5px;">{code}</h1>
                <p>This code will expire in 10 minutes.</p>
                <p>If you did not request this, please ignore this email.</p>
            </div>
        </body>
    </html>
    """
    try:
        gmail_email, gmail_password = _get_gmail_credentials()
        message = EmailMessage()
        message["Subject"] = "MediSecure - Password Reset"
        message["From"] = gmail_email
        message["To"] = email
        message.set_content("Use the code above to reset your password.")
        message.add_alternative(html, subtype="html")

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(gmail_email, gmail_password)
            server.send_message(message)
        logger.info(f"Password reset email sent to {email} via Gmail.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        print(f"FALLBACK - RESET CODE: {code}")

async def send_new_device_email(email: EmailStr, code: str):
    """Send new device verification email using Gmail SMTP"""
    html = f"""
    <html>
        <body>
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>New Device Detected</h2>
                <p>We detected a login from a new device. Please verify it's you using the code below:</p>
                <h1 style="color: #2196F3; letter-spacing: 5px;">{code}</h1>
                <p>This code will expire in 10 minutes.</p>
                <p>If you did not attempt to login, please change your password immediately.</p>
            </div>
        </body>
    </html>
    """
    try:
        gmail_email, gmail_password = _get_gmail_credentials()
        message = EmailMessage()
        message["Subject"] = "MediSecure - New Device Verification"
        message["From"] = gmail_email
        message["To"] = email
        message.set_content("Use the code above to verify your new device.")
        message.add_alternative(html, subtype="html")

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(gmail_email, gmail_password)
            server.send_message(message)
        logger.info(f"New device verification email sent to {email} via Gmail.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        print(f"FALLBACK - DEVICE CODE: {code}")

# ============ HELPER FUNCTIONS ============
def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Set HttpOnly cookies for access and refresh tokens"""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE,
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",  # More restrictive for refresh token
        max_age=REFRESH_TOKEN_EXPIRE,
        path="/api/auth/refresh"
    )

def clear_auth_cookies(response: Response):
    """Clear authentication cookies"""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/auth/refresh")

def create_refresh_token(user_id: int) -> str:
    """Create a refresh token and store in Redis"""
    token = secrets.token_urlsafe(32)
    return token

# ============ ENDPOINTS ============

@router.post("/register", status_code=status.HTTP_201_CREATED, 
             response_model=SignupResponse,
             dependencies=[Depends(RateLimiter(times=5, seconds=60))])
@router.post("/signup", status_code=status.HTTP_201_CREATED,
             response_model=SignupResponse, 
             dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def register(user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Register a new user account.
    Sends verification email with 6-digit code.
    
    POST /api/auth/register or /api/auth/signup
    """
    # 1. Check if user exists in DB
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Check if user has a pending registration in Redis
    redis_key = f"registration:{user.email}"
    existing_registration = await redis_client.get(redis_key)
    if existing_registration:
        raise HTTPException(status_code=400, detail="Verification code already sent. Please check your email.")

    # 3. Generate Salt and Hash Password
    salt = generate_salt()
    hashed_password = get_password_hash(user.password, salt)
    
    # 4. Generate Verification Code
    code = generate_verification_code()

    # 5. Prepare data for Redis
    user_data = {
        "email": user.email,
        "name": user.name,
        "hashed_password": hashed_password,
        "salt": salt,
        "role": user.role.value if user.role else "patient",
        "code": code
    }
    
    # 6. Store in Redis (Expire in 10 minutes)
    await redis_client.setex(redis_key, 600, json.dumps(user_data))

    # 7. Send Email (Background Task)
    background_tasks.add_task(send_verification_email, user.email, code)

    return SignupResponse(
        message="Registration successful. Please check your email to verify your account."
    )


@router.post("/verify-email", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
@router.post("/verify", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def verify_email(verification: UserVerify, db: Session = Depends(get_db)):
    """
    Verify email with the code sent to user's email.
    
    POST /api/auth/verify-email or /api/auth/verify
    """
    # 1. Get data from Redis
    redis_key = f"registration:{verification.email}"
    stored_data_json = await redis_client.get(redis_key)

    if not stored_data_json:
        raise HTTPException(status_code=400, detail="Verification code expired or invalid")
    
    stored_data = json.loads(stored_data_json)
    
    # 2. Verify Code (handle both field names)
    code = verification.get_code
    if stored_data["code"] != code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # 3. Create User in DB
    new_user = User(
        email=stored_data["email"],
        name=stored_data.get("name"),
        hashed_password=stored_data["hashed_password"],
        salt=stored_data["salt"],
        role=stored_data["role"],
        is_verified=True,
        is_active=True
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during user creation: {e}")
        raise HTTPException(status_code=500, detail="Database error during user creation")

    # 4. Delete data from Redis
    await redis_client.delete(redis_key)

    return {"message": "Email verified successfully. You can now login."}


@router.post("/login", response_model=LoginResponse, 
             dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def login(
    user_credentials: UserLogin, 
    request: Request, 
    response: Response,
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    Sets HttpOnly cookies with access and refresh tokens.
    
    POST /api/auth/login
    """
    # 1. Get User
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2. Check if account is active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    # 3. Check Verification
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Account not verified. Please verify your email first.")

    # 4. Verify Password
    if not verify_password(user_credentials.password, user.hashed_password, user.salt):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 5. Device Fingerprinting
    if user_credentials.device_fingerprint:
        current_fingerprint = user_credentials.device_fingerprint
    else:
        current_fingerprint = generate_device_fingerprint(request)
    
    # Check if user has any devices registered
    user_devices = db.query(UserDevice).filter(UserDevice.user_id == user.id).all()
    
    if not user_devices:
        # First login ever - register this device automatically
        new_device = UserDevice(user_id=user.id, fingerprint_hash=current_fingerprint)
        db.add(new_device)
        db.commit()
    else:
        # Check if current fingerprint matches any known device
        known_device = next((d for d in user_devices if d.fingerprint_hash == current_fingerprint), None)
        
        if not known_device:
            # New device detected - require 2FA verification
            code = generate_verification_code()
            device_id = secrets.token_urlsafe(16)
            
            # Store in Redis (Expire in 10 minutes)
            redis_key = f"device_verify:{user.email}"
            await redis_client.setex(redis_key, 600, json.dumps({
                "fingerprint": current_fingerprint,
                "code": code,
                "device_id": device_id
            }))
            
            # Send Email
            background_tasks.add_task(send_new_device_email, user.email, code)
            
            # Return response indicating device verification required
            return LoginResponse(
                user=UserResponse.model_validate(user),
                message="Please verify your device. A code has been sent to your email.",
                requires_verification=True,
                device_id=device_id
            )
        else:
            # Update last login for this device
            known_device.last_login = datetime.utcnow()
            db.commit()

    # 6. Generate Tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value, "email": user.email},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(user.id)
    
    # Store refresh token in Redis
    await redis_client.setex(
        f"refresh_token:{user.id}:{refresh_token}", 
        REFRESH_TOKEN_EXPIRE, 
        json.dumps({"user_id": user.id, "email": user.email})
    )

    # 7. Set HttpOnly Cookies
    set_auth_cookies(response, access_token, refresh_token)

    return LoginResponse(
        user=UserResponse.model_validate(user),
        message="Login successful"
    )


@router.post("/verify-device", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def verify_device(
    verification: UserDeviceVerify, 
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Verify a new device with the code sent to user's email.
    
    POST /api/auth/verify-device
    """
    # 1. Get data from Redis
    redis_key = f"device_verify:{verification.email}"
    stored_data_json = await redis_client.get(redis_key)

    if not stored_data_json:
        raise HTTPException(status_code=400, detail="Verification code expired or invalid")
    
    stored_data = json.loads(stored_data_json)
    
    # 2. Verify Code
    if stored_data["code"] != verification.verification_code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # 3. Get fingerprint
    current_fingerprint = verification.device_fingerprint or stored_data["fingerprint"]

    # 4. Get User
    user = db.query(User).filter(User.email == verification.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 5. Register New Device
    new_device = UserDevice(user_id=user.id, fingerprint_hash=current_fingerprint)
    db.add(new_device)
    db.commit()

    # 6. Delete data from Redis
    await redis_client.delete(redis_key)

    # 7. Generate Tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value, "email": user.email},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(user.id)
    
    # Store refresh token in Redis
    await redis_client.setex(
        f"refresh_token:{user.id}:{refresh_token}", 
        REFRESH_TOKEN_EXPIRE, 
        json.dumps({"user_id": user.id, "email": user.email})
    )

    # 8. Set Cookies
    set_auth_cookies(response, access_token, refresh_token)

    return LoginResponse(
        user=UserResponse.model_validate(user),
        message="Device verified successfully"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user.
    
    GET /api/auth/me
    """
    return UserResponse.model_validate(current_user)


@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token from cookie.
    
    POST /api/auth/refresh
    """
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")
    
    # Find the refresh token in Redis (scan for matching token)
    # In production, you'd want a more efficient lookup
    pattern = f"refresh_token:*:{refresh_token}"
    keys = []
    async for key in redis_client.scan_iter(match=pattern):
        keys.append(key)
    
    if not keys:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    # Get user data from Redis
    token_data_json = await redis_client.get(keys[0])
    if not token_data_json:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    token_data = json.loads(token_data_json)
    user_id = token_data["user_id"]
    
    # Get user from DB
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        clear_auth_cookies(response)
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    # Generate new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value, "email": user.email},
        expires_delta=access_token_expires
    )
    
    # Set new access token cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE,
        path="/"
    )
    
    return {"message": "Token refreshed successfully"}


@router.post("/logout")
async def logout(request: Request, response: Response):
    """
    Logout user and clear cookies.
    
    POST /api/auth/logout
    """
    # Try to delete refresh token from Redis
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        pattern = f"refresh_token:*:{refresh_token}"
        async for key in redis_client.scan_iter(match=pattern):
            await redis_client.delete(key)
    
    # Clear cookies
    clear_auth_cookies(response)
    
    return {"message": "Logged out successfully"}


@router.post("/forgot-password", dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def forgot_password(
    request_data: UserForgotPassword, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    Request password reset. Sends code to email.
    
    POST /api/auth/forgot-password
    """
    # Check if user exists (but don't reveal this info)
    user = db.query(User).filter(User.email == request_data.email).first()
    
    if user:
        # Generate Reset Code
        code = generate_verification_code()
        
        # Store in Redis (Expire in 10 minutes)
        redis_key = f"reset:{request_data.email}"
        await redis_client.setex(redis_key, 600, code)
        
        # Send Email
        background_tasks.add_task(send_password_reset_email, request_data.email, code)

    # Always return same message for security
    return {"message": "If the email exists, a reset code has been sent."}


@router.post("/reset-password", dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def reset_password(request_data: UserResetPassword, db: Session = Depends(get_db)):
    """
    Reset password with code sent to email.
    
    POST /api/auth/reset-password
    """
    # 1. Verify Code from Redis
    redis_key = f"reset:{request_data.email}"
    stored_code = await redis_client.get(redis_key)
    
    code = request_data.get_code

    if not stored_code or stored_code != code:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    # 2. Get User
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 3. Hash New Password
    new_salt = generate_salt()
    new_hashed_password = get_password_hash(request_data.new_password, new_salt)

    # 4. Update User
    user.hashed_password = new_hashed_password
    user.salt = new_salt
    user.updated_at = datetime.utcnow()
    db.commit()

    # 5. Delete Code from Redis
    await redis_client.delete(redis_key)

    return {"message": "Password reset successful"}


@router.post("/resend-verification", dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def resend_verification(
    request_data: UserForgotPassword,  # Just needs email
    background_tasks: BackgroundTasks
):
    """
    Resend email verification code.
    
    POST /api/auth/resend-verification
    """
    redis_key = f"registration:{request_data.email}"
    stored_data_json = await redis_client.get(redis_key)
    
    if not stored_data_json:
        raise HTTPException(status_code=400, detail="No pending verification found. Please register again.")
    
    stored_data = json.loads(stored_data_json)
    
    # Generate new code
    new_code = generate_verification_code()
    stored_data["code"] = new_code
    
    # Update in Redis (reset the 10 minute timer)
    await redis_client.setex(redis_key, 600, json.dumps(stored_data))
    
    # Send new verification email
    background_tasks.add_task(send_verification_email, request_data.email, new_code)
    
    return {"message": "Verification code resent. Please check your email."}
