from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from config.database import Base


class MetricType(enum.Enum):
    BLOOD_PRESSURE = "blood_pressure"
    HEART_RATE = "heart_rate"
    TEMPERATURE = "temperature"
    BLOOD_GLUCOSE = "blood_glucose"
    WEIGHT = "weight"
    HEIGHT = "height"
    BMI = "bmi"
    OXYGEN_SATURATION = "oxygen_saturation"
    STEPS = "steps"
    SLEEP_HOURS = "sleep_hours"


class HealthMetric(Base):
    __tablename__ = "health_metrics"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    metric_type = Column(SQLEnum(MetricType), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    systolic = Column(Float, nullable=True)  # For blood pressure
    diastolic = Column(Float, nullable=True)  # For blood pressure
    notes = Column(String(500), nullable=True)
    source = Column(String(100), default="manual")  # manual, wearable, clinical
    device_name = Column(String(100), nullable=True)
    recorded_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("User", backref="health_metrics")
