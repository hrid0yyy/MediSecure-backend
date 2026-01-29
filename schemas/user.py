from pydantic import BaseModel, EmailStr, validator
from models import UserRole
from typing import Optional
from datetime import datetime
from utils.security import validate_password_strength

class UserBase(BaseModel):
    email: EmailStr

# Registration request - matches frontend SignupRequest
class UserCreate(UserBase):
    password: str
    name: Optional[str] = None
    role: Optional[UserRole] = UserRole.PATIENT

    @validator('password')
    def validate_password(cls, v):
        try:
            validate_password_strength(v)
        except ValueError as e:
            raise ValueError(str(e))
        return v

# Login request - matches frontend LoginRequest
class UserLogin(UserBase):
    password: str
    device_name: Optional[str] = None
    device_fingerprint: Optional[str] = None

# Email verification request
class UserVerify(BaseModel):
    email: EmailStr
    code: Optional[str] = None
    verification_code: Optional[str] = None  # Frontend uses this name
    
    @property
    def get_code(self) -> str:
        return self.verification_code or self.code or ""

class UserForgotPassword(BaseModel):
    email: EmailStr

class UserResetPassword(BaseModel):
    email: EmailStr
    reset_code: Optional[str] = None
    code: Optional[str] = None  # Backend also accepts this
    new_password: str
    
    @property
    def get_code(self) -> str:
        return self.reset_code or self.code or ""

    @validator('new_password')
    def validate_password(cls, v):
        try:
            validate_password_strength(v)
        except ValueError as e:
            raise ValueError(str(e))
        return v

class UserDeviceVerify(BaseModel):
    email: EmailStr
    verification_code: str
    device_fingerprint: Optional[str] = None

# User response - matches frontend User type
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    role: UserRole
    is_verified: bool
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Login response - matches frontend LoginResponse
class LoginResponse(BaseModel):
    user: UserResponse
    message: str = "Login successful"
    requires_verification: Optional[bool] = None
    device_id: Optional[str] = None

# Signup response
class SignupResponse(BaseModel):
    message: str
    user: Optional[UserResponse] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_password(cls, v):
        try:
            validate_password_strength(v)
        except ValueError as e:
            raise ValueError(str(e))
        return v

# Token schema (for internal use, not returned to client anymore)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None
