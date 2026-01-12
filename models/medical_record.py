from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from config.database import Base


class RecordType(enum.Enum):
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    LAB_RESULT = "lab_result"
    IMAGING = "imaging"
    ALLERGY = "allergy"
    IMMUNIZATION = "immunization"
    VITAL_SIGNS = "vital_signs"
    SURGERY = "surgery"


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_type = Column(SQLEnum(RecordType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    encrypted_data = Column(Text, nullable=True)  # Encrypted sensitive medical data
    diagnosis_code = Column(String(50), nullable=True)  # ICD-10 code
    is_active = Column(Boolean, default=True)
    recorded_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], backref="medical_records")
    doctor = relationship("User", foreign_keys=[doctor_id])
