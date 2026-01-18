from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from config.database import Base
import enum
from datetime import datetime

class UserRole(str, enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"
    STAFF = "staff"
    SUPERADMIN = "superadmin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)  # User's display name
    hashed_password = Column(String, nullable=False)
    salt = Column(String, nullable=False)  # Unique random salt per user
    role = Column(Enum(UserRole), default=UserRole.PATIENT, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # For soft delete / account disable
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    devices = relationship("UserDevice", back_populates="user")
    profile = relationship("UserProfile", back_populates="user", uselist=False)

class UserDevice(Base):
    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fingerprint_hash = Column(String, index=True, nullable=False)
    last_login = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="devices")
