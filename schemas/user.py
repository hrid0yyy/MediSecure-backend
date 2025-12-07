from pydantic import BaseModel, EmailStr
from models import UserRole

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.PATIENT

class UserLogin(UserBase):
    password: str

class UserVerify(BaseModel):
    email: EmailStr
    code: str
