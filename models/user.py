from sqlalchemy import Column, Integer, String, Boolean, Enum
from config.database import Base
import enum

class UserRole(str, enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"
    STAFF = "staff"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    salt = Column(String, nullable=False)  # Unique random salt per user
    role = Column(Enum(UserRole), default=UserRole.PATIENT, nullable=False)
    is_verified = Column(Boolean, default=False)
