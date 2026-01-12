from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from config.database import Base


class SessionStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class TelemedicineSession(Base):
    __tablename__ = "telemedicine_sessions"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(500), nullable=True)
    room_id = Column(String(255), unique=True, nullable=False)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.SCHEDULED)
    scheduled_start = Column(DateTime, nullable=False)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    recording_url = Column(String(500), nullable=True)
    recording_consent = Column(Boolean, default=False)
    consultation_notes = Column(Text, nullable=True)
    follow_up_required = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    doctor = relationship("User", foreign_keys=[doctor_id])
    appointment = relationship("Appointment", backref="telemedicine_session")
