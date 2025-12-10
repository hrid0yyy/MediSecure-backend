from pydantic import BaseModel, EmailStr
from models import UserRole

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
