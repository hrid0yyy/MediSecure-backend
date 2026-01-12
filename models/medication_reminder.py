from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from config.database import Base


class ReminderStatus(enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class MedicationReminder(Base):
    __tablename__ = "medication_reminders"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=True)
    medication_name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    reminder_times = Column(String(255), nullable=False)  # JSON string of times
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(SQLEnum(ReminderStatus), default=ReminderStatus.ACTIVE)
    notify_via_email = Column(Boolean, default=True)
    notify_via_sms = Column(Boolean, default=False)
    notify_caregiver = Column(Boolean, default=False)
    caregiver_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User", backref="medication_reminders")
    adherence_logs = relationship("MedicationAdherence", back_populates="reminder", cascade="all, delete-orphan")


class MedicationAdherence(Base):
    __tablename__ = "medication_adherence"

    id = Column(Integer, primary_key=True, index=True)
    reminder_id = Column(Integer, ForeignKey("medication_reminders.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    taken_at = Column(DateTime, nullable=True)
    was_taken = Column(Boolean, default=False)
    was_skipped = Column(Boolean, default=False)
    skip_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reminder = relationship("MedicationReminder", back_populates="adherence_logs")
