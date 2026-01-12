from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from config.database import Base


class ClaimStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PARTIALLY_APPROVED = "partially_approved"
    DENIED = "denied"
    APPEALED = "appealed"


class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    claim_number = Column(String(100), unique=True, nullable=False)
    insurance_provider = Column(String(255), nullable=False)
    policy_number = Column(String(100), nullable=False)
    status = Column(SQLEnum(ClaimStatus), default=ClaimStatus.DRAFT)
    claim_amount = Column(Float, nullable=False)
    approved_amount = Column(Float, nullable=True)
    denied_amount = Column(Float, nullable=True)
    denial_reason = Column(Text, nullable=True)
    submission_date = Column(DateTime, nullable=True)
    response_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User", backref="insurance_claims")
    invoice = relationship("Invoice", backref="insurance_claim")
