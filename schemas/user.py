from pydantic import BaseModel, EmailStr
from models import UserRole
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserVerify(BaseModel):
    email: EmailStr
    code: str

class UserForgotPassword(BaseModel):
    email: EmailStr

class UserResetPassword(BaseModel):
    email: EmailStr
    code: str
    new_password: str

class UserDeviceVerify(BaseModel):
    email: EmailStr
    code: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    is_verified: bool
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
