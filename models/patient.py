"""
Patient Model
Separate table for patient-specific data linked to User
"""
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)  # Can link to user account
    
    # Personal Information
    name = Column(String(255), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    date_of_birth = Column(Date)
    gender = Column(String(20))  # male, female, other
    blood_type = Column(String(10))  # A+, A-, B+, B-, AB+, AB-, O+, O-
    
    # Address
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    country = Column(String(100), default="USA")
    
    # Emergency Contact
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(50))
    emergency_contact_relation = Column(String(50))
    
    # Medical Information
    medical_history = Column(Text)  # General medical history notes
    allergies = Column(JSON, default=list)  # List of allergies
    current_medications = Column(JSON, default=list)  # List of current medications
    
    # Insurance (encrypted in practice)
    insurance_provider = Column(String(255))
    insurance_policy_number = Column(String(100))
    insurance_group_number = Column(String(100))
    
    # Status
    status = Column(String(20), default="active")  # active, inactive, deceased
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - only to User (other relationships handled separately)
    user = relationship("User", backref="patient_profile")

    def __repr__(self):
        return f"<Patient {self.name}>"

