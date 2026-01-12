from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from models.appointment import AppointmentStatus


# Request Schemas
class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: datetime
    duration_minutes: int = Field(default=30, ge=15, le=240)
    reason: str = Field(..., min_length=10, max_length=1000)

    class Config:
        from_attributes = True


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=240)
    reason: Optional[str] = Field(None, min_length=10, max_length=1000)
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class AppointmentCancel(BaseModel):
    cancellation_reason: str = Field(..., min_length=10, max_length=500)


# Response Schemas
class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    duration_minutes: int
    reason: str
    status: AppointmentStatus
    notes: Optional[str]
    cancellation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppointmentListResponse(BaseModel):
    appointments: list[AppointmentResponse]
    total: int
    page: int
    page_size: int

    class Config:
        from_attributes = True
