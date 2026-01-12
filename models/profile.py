from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime

class UserProfile(Base):
    """
    User profile table with PII data.
    Sensitive fields should be encrypted before storing.
    """
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Personal Information (encrypted)
    first_name = Column(String(255), nullable=True)  # Encrypted
    last_name = Column(String(255), nullable=True)   # Encrypted
    date_of_birth = Column(String(255), nullable=True)  # Encrypted (stored as encrypted string)
    phone = Column(String(255), nullable=True)  # Encrypted
    address = Column(Text, nullable=True)  # Encrypted
    
    # Medical Information (encrypted)
    medical_record_number = Column(String(255), nullable=True)  # Encrypted
    insurance_number = Column(String(255), nullable=True)  # Encrypted
    blood_type = Column(String(10), nullable=True)  # Not encrypted (not highly sensitive)
    
    # Emergency Contact (encrypted)
    emergency_contact_name = Column(String(255), nullable=True)  # Encrypted
    emergency_contact_phone = Column(String(255), nullable=True)  # Encrypted
    
    # Non-sensitive metadata
    profile_picture_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", backref="profile")
