from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from config.database import Base


class PrescriptionStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    prescription_number = Column(String(100), unique=True, nullable=False)
    status = Column(SQLEnum(PrescriptionStatus), default=PrescriptionStatus.ACTIVE)
    diagnosis = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    digital_signature = Column(Text, nullable=True)
    issued_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], backref="prescriptions")
    doctor = relationship("User", foreign_keys=[doctor_id])
    medications = relationship("PrescriptionMedication", back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionMedication(Base):
    __tablename__ = "prescription_medications"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)
    medication_name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration_days = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    instructions = Column(Text, nullable=True)
    refills_allowed = Column(Integer, default=0)
    refills_remaining = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    prescription = relationship("Prescription", back_populates="medications")
