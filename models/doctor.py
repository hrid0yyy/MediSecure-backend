"""
Doctor Model
Separate table for doctor-specific data linked to User
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)  # Links to user account
    
    # Personal Information
    name = Column(String(255), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    
    # Professional Information
    specialization = Column(String(100), nullable=False)  # Cardiology, Neurology, etc.
    license_number = Column(String(100), unique=True)
    department = Column(String(100))
    bio = Column(Text)  # Short biography
    
    # Avatar
    avatar_url = Column(String(500))
    
    # Fees
    consultation_fee = Column(Float, default=0.0)
    
    # Availability
    available_days = Column(JSON, default=list)  # ["Monday", "Tuesday", ...]
    available_hours = Column(JSON, default=dict)  # {"start": "09:00", "end": "17:00"}
    is_available = Column(Boolean, default=True)
    
    # Qualifications
    qualifications = Column(JSON, default=list)  # ["MBBS", "MD", ...]
    experience_years = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="doctor_profile")
    appointments = relationship("Appointment", back_populates="doctor", foreign_keys="Appointment.doctor_id")
    medical_records = relationship("MedicalRecord", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")

    def __repr__(self):
        return f"<Doctor {self.name} - {self.specialization}>"


# List of valid specializations
SPECIALIZATIONS = [
    "Cardiology",
    "Neurology",
    "Orthopedics",
    "Pediatrics",
    "Dermatology",
    "General Medicine",
    "Gynecology",
    "Ophthalmology",
    "ENT",
    "Psychiatry",
    "Oncology",
    "Urology",
    "Gastroenterology",
    "Pulmonology",
    "Nephrology",
    "Endocrinology",
    "Rheumatology",
    "Anesthesiology",
    "Radiology",
    "Pathology",
    "Emergency Medicine",
    "Family Medicine",
    "Internal Medicine",
    "Surgery",
    "Plastic Surgery"
]
