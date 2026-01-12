from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from config.database import Base


class NotificationType(enum.Enum):
    APPOINTMENT_REMINDER = "appointment_reminder"
    MEDICATION_REMINDER = "medication_reminder"
    TEST_RESULT = "test_result"
    PRESCRIPTION_READY = "prescription_ready"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    NEW_MESSAGE = "new_message"
    PAYMENT_DUE = "payment_due"
    SYSTEM_ALERT = "system_alert"


class NotificationChannel(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    channel = Column(SQLEnum(NotificationChannel), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    failed_reason = Column(Text, nullable=True)
    extra_data = Column(Text, nullable=True)  # JSON string for additional data (renamed from metadata)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="notifications")
