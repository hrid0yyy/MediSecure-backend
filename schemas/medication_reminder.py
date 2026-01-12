from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from models.medication_reminder import ReminderStatus


class MedicationReminderCreate(BaseModel):
    prescription_id: Optional[int] = None
    medication_name: str = Field(..., min_length=2, max_length=255)
    dosage: str = Field(..., min_length=2, max_length=100)
    reminder_times: str = Field(..., description="Comma-separated times (HH:MM format)")
    start_date: datetime
    end_date: Optional[datetime] = None
    notify_via_email: bool = True
    notify_via_sms: bool = False
    notify_caregiver: bool = False
    caregiver_email: Optional[EmailStr] = None

    class Config:
        from_attributes = True


class MedicationReminderUpdate(BaseModel):
    reminder_times: Optional[str] = None
    status: Optional[ReminderStatus] = None
    notify_via_email: Optional[bool] = None
    notify_via_sms: Optional[bool] = None
    notify_caregiver: Optional[bool] = None
    caregiver_email: Optional[EmailStr] = None

    class Config:
        from_attributes = True


class MedicationReminderResponse(BaseModel):
    id: int
    patient_id: int
    medication_name: str
    dosage: str
    reminder_times: str
    start_date: datetime
    end_date: Optional[datetime]
    status: ReminderStatus
    notify_via_email: bool
    notify_via_sms: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdherenceLogCreate(BaseModel):
    was_taken: bool
    was_skipped: bool = False
    skip_reason: Optional[str] = None
    taken_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdherenceLogResponse(BaseModel):
    id: int
    reminder_id: int
    scheduled_time: datetime
    taken_at: Optional[datetime]
    was_taken: bool
    was_skipped: bool
    skip_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
