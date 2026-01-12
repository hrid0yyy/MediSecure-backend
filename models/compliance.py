from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base


class PHIAccessLog(Base):
    __tablename__ = "phi_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)  # VIEW, CREATE, UPDATE, DELETE
    resource_type = Column(String(100), nullable=False)  # medical_record, prescription, etc.
    resource_id = Column(Integer, nullable=True)
    access_reason = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    access_granted = Column(Boolean, default=True)
    denial_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    accessing_user = relationship("User", foreign_keys=[user_id])
    patient = relationship("User", foreign_keys=[patient_id])


class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consent_type = Column(String(100), nullable=False)  # treatment, data_sharing, research, marketing
    consent_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    granted = Column(Boolean, nullable=False)
    consent_version = Column(String(50), default="1.0")
    granted_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    document_url = Column(String(500), nullable=True)
    signature_data = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User", backref="consents")
