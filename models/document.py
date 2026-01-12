from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from config.database import Base


class DocumentType(enum.Enum):
    LAB_REPORT = "lab_report"
    IMAGING = "imaging"
    PRESCRIPTION = "prescription"
    INSURANCE = "insurance"
    REFERRAL = "referral"
    CONSENT_FORM = "consent_form"
    MEDICAL_CERTIFICATE = "medical_certificate"
    OTHER = "other"


class MedicalDocument(Base):
    __tablename__ = "medical_documents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    encrypted = Column(Integer, default=1)  # Boolean as int
    ocr_text = Column(Text, nullable=True)  # Extracted text from OCR
    document_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], backref="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
